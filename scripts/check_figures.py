#!/usr/bin/env python3
"""assets/*.svg の機械検証。問題があれば exit 1。

- XML整形性、幅1000、role="img" と aria-label
- 最小フォント14px、テキストのviewBox内収まり（概算幅）、テキスト同士の重なり（概算）
- 配色：許可色（draw_figures.PALETTE）以外を使っていない、地の塗りが1図で4種以内
- 視認性：各テキストの文字色と、その文字を内包する地（最後に描かれた rect / polygon、なければ背景）とのコントラスト比が4.5以上
- 収まり：テキストの推定幅（太字・半角を保守的に見積もる）が、中心点を内包する最小の図形の内側に余白 PAD 以上を残して収まる
"""
from __future__ import annotations
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draw_figures import BG, PALETTE  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
NS = '{http://www.w3.org/2000/svg}'
MIN_FONT = 14
MAX_FILLS = 4
MIN_CONTRAST = 4.5
PAD = 6  # 図形の縁と文字の間に最低限残す余白(px)


def est_w(s: str, size: float, bold: bool = False) -> float:
    """文字幅の保守的な概算。ASCIIは0.6em（太字0.65em）、それ以外（全角・矢印・記号）は1.0em。"""
    half = 0.65 if bold else 0.6
    return sum(size * (half if ord(c) < 0x80 else 1.0) for c in s)


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    def chan(v: float) -> float:
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def point_in_polygon(x: float, y: float, pts: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]; xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def text_bbox(el):
    s = el.text or ''
    size = float(el.get('font-size', '16'))
    x, y = float(el.get('x')), float(el.get('y'))
    w = est_w(s, size, el.get('font-weight') == '700')
    anchor = el.get('text-anchor', 'start')
    x0 = x - w if anchor == 'end' else x - w / 2 if anchor == 'middle' else x
    if 'rotate' in (el.get('transform') or ''):
        return None  # 回転テキストは幅の向きが異なるので収まり判定を省略
    return (x0, y - size, x0 + w, y)


def contains(kind, geom, x: float, y: float) -> bool:
    if kind == 'rect':
        rx, ry, rw, rh = geom
        return rx <= x <= rx + rw and ry <= y <= ry + rh
    return point_in_polygon(x, y, geom)


def area(kind, geom) -> float:
    if kind == 'rect':
        return geom[2] * geom[3]
    xs = [p[0] for p in geom]; ys = [p[1] for p in geom]
    return (max(xs) - min(xs)) * (max(ys) - min(ys))


def background_at(shapes, x: float, y: float) -> str:
    """点 (x, y) を内包する最後の図形の塗りを返す。無ければ背景色。"""
    fill = BG
    for kind, geom, f in shapes:
        if f in ('none', '') or f is None:
            continue
        if contains(kind, geom, x, y):
            fill = f
    return fill


def container_of(shapes, x: float, y: float):
    """点 (x, y) を内包する最小面積の図形（枠線だけの図形も含む）を返す。"""
    hits = [(kind, geom) for kind, geom, f in shapes if contains(kind, geom, x, y)]
    return min(hits, key=lambda h: area(*h)) if hits else None


def fits_inside(kind, geom, bb) -> bool:
    x0, y0, x1, y1 = bb
    if kind == 'rect':
        rx, ry, rw, rh = geom
        return rx + PAD <= x0 and x1 <= rx + rw - PAD and ry + PAD / 2 <= y0 and y1 <= ry + rh - PAD / 2
    return all(point_in_polygon(px, py, geom) for px, py in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)))


def main() -> int:
    errors = []
    for path in sorted(ASSETS.glob('*.svg')):
        raw = path.read_text(encoding='utf-8')
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as e:
            errors.append(f'{path.name}: XML parse error: {e}'); continue
        vb = [float(v) for v in root.get('viewBox', '0 0 0 0').split()]
        W, H = vb[2], vb[3]
        if root.get('width') != '1000':
            errors.append(f'{path.name}: width is {root.get("width")}, expected 1000')
        if root.get('role') != 'img' or not root.get('aria-label'):
            errors.append(f'{path.name}: missing role="img" or aria-label')
        # 配色
        used = set(re.findall(r'#[0-9a-fA-F]{3,6}\b', raw))
        for c in sorted(used - PALETTE):
            errors.append(f'{path.name}: palette violation {c}')
        shapes = []
        ground_fills = set()
        for el in root.iter():
            tag = el.tag.replace(NS, '')
            f = el.get('fill')
            if tag == 'rect':
                if el.get('width') == '100%':
                    continue  # 背景
                geom = tuple(float(el.get(k)) for k in ('x', 'y', 'width', 'height'))
                shapes.append(('rect', geom, f))
            elif tag == 'polygon':
                pts = [tuple(map(float, p.split(','))) for p in el.get('points', '').split()]
                if len(pts) >= 5:  # 矢頭(3点)は除外
                    shapes.append(('polygon', pts, f))
                else:
                    continue
            else:
                continue
            if f and f not in ('none', BG):
                ground_fills.add(f)
        if len(ground_fills) > MAX_FILLS:
            errors.append(f'{path.name}: {len(ground_fills)} ground fills > {MAX_FILLS}: {sorted(ground_fills)}')
        # テキスト
        boxes = []
        for el in root.iter(NS + 'text'):
            s = (el.text or '').strip()
            if not s:
                continue
            size = float(el.get('font-size', '16'))
            if size < MIN_FONT:
                errors.append(f'{path.name}: font-size {size} < {MIN_FONT}: "{s}"')
            bb = text_bbox(el)
            if bb is not None:
                if bb[0] < PAD or bb[2] > W - PAD or bb[1] < 0 or bb[3] > H:
                    errors.append(f'{path.name}: text out of viewBox ({bb[0]:.0f}..{bb[2]:.0f}, {bb[1]:.0f}..{bb[3]:.0f}): "{s}"')
                boxes.append((bb, s))
                cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
                holder = container_of(shapes, cx, cy)
                if holder and not fits_inside(*holder, bb):
                    errors.append(f'{path.name}: text overflows its {holder[0]} (text {bb[0]:.0f}..{bb[2]:.0f}, shape {holder[1][0]:.0f}..{holder[1][0] + holder[1][2]:.0f}): "{s}"' if holder[0] == 'rect'
                                  else f'{path.name}: text overflows its polygon: "{s}"')
            else:
                cx, cy = float(el.get('x')), float(el.get('y'))
            ground = background_at(shapes, cx, cy)
            ratio = contrast(el.get('fill', T1_FALLBACK), ground)
            if ratio < MIN_CONTRAST:
                errors.append(f'{path.name}: contrast {ratio:.2f} < {MIN_CONTRAST} ({el.get("fill")} on {ground}): "{s}"')
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i][0], boxes[j][0]
                ox = min(a[2], b[2]) - max(a[0], b[0]); oy = min(a[3], b[3]) - max(a[1], b[1])
                if ox > 4 and oy > 4:
                    errors.append(f'{path.name}: text overlap: "{boxes[i][1]}" / "{boxes[j][1]}"')
        print(f'checked {path.name} ({W:.0f}x{H:.0f}, {len(boxes)} texts, {len(ground_fills)} fills)')
    if errors:
        print('\n'.join(errors)); print(f'{len(errors)} problem(s)'); return 1
    print('OK'); return 0


T1_FALLBACK = '#223e53'

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""assets/*.svg の機械検証。XML整形性、幅1000、aria-label、最小フォント14px、
テキストのviewBox内収まり（概算幅）、テキスト同士の重なり（概算）を確認し、問題があれば exit 1。"""
from __future__ import annotations
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
NS = '{http://www.w3.org/2000/svg}'
MIN_FONT = 14


def est_w(s: str, size: float) -> float:
    return sum(size * (0.55 if ord(c) < 0x2E80 else 1.0) for c in s)


def text_bbox(el):
    s = el.text or ''
    size = float(el.get('font-size', '16'))
    x, y = float(el.get('x')), float(el.get('y'))
    w = est_w(s, size)
    anchor = el.get('anchor') or el.get('text-anchor', 'start')
    x0 = x - w if anchor == 'end' else x - w / 2 if anchor == 'middle' else x
    if 'rotate' in (el.get('transform') or ''):
        return None  # 回転テキストは幅の向きが異なるので収まり判定のみ省略
    return (x0, y - size, x0 + w, y)


def main() -> int:
    errors = []
    for path in sorted(ASSETS.glob('*.svg')):
        try:
            root = ET.fromstring(path.read_text(encoding='utf-8'))
        except ET.ParseError as e:
            errors.append(f'{path.name}: XML parse error: {e}'); continue
        vb = [float(v) for v in root.get('viewBox', '0 0 0 0').split()]
        W, H = vb[2], vb[3]
        if root.get('width') != '1000':
            errors.append(f'{path.name}: width is {root.get("width")}, expected 1000')
        if root.get('role') != 'img' or not root.get('aria-label'):
            errors.append(f'{path.name}: missing role="img" or aria-label')
        boxes = []
        for el in root.iter(NS + 'text'):
            size = float(el.get('font-size', '16'))
            if size < MIN_FONT:
                errors.append(f'{path.name}: font-size {size} < {MIN_FONT}: "{el.text}"')
            bb = text_bbox(el)
            if bb is None or not (el.text or '').strip():
                continue
            if bb[0] < 0 or bb[2] > W or bb[1] < 0 or bb[3] > H:
                errors.append(f'{path.name}: text out of viewBox ({bb[0]:.0f}..{bb[2]:.0f}, {bb[1]:.0f}..{bb[3]:.0f}): "{el.text}"')
            boxes.append((bb, el.text))
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i][0], boxes[j][0]
                ox = min(a[2], b[2]) - max(a[0], b[0]); oy = min(a[3], b[3]) - max(a[1], b[1])
                if ox > 4 and oy > 4:
                    errors.append(f'{path.name}: text overlap: "{boxes[i][1]}" / "{boxes[j][1]}"')
        print(f'checked {path.name} ({W:.0f}x{H:.0f}, {len(boxes)} texts)')
    if errors:
        print('\n'.join(errors)); print(f'{len(errors)} problem(s)'); return 1
    print('OK'); return 0


if __name__ == '__main__':
    sys.exit(main())

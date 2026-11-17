#!/usr/bin/env python3
"""記事「生成と検証から考えるテスト自動化の歴史とコスト構造」の図版（全22点）を決定論的に生成する。

体裁：幅1000px、最小フォント14px、注記16px、Python標準ライブラリのみ。
配色は役割で固定する（claudedocs/svg-style-rules-plan.md）。
  NEUTRAL   区別を付けない基本要素、従来・自社で担うもの
  PRIMARY   主題のシステム・領域・選択肢
  AI        生成AI・AIエージェントによる支援
  POSITIVE  削減・移転・成功（負担が減る側）
  ATTENTION 残る負担・課題・注意・ボトルネック（1図に1系統）
  INK       結論・題名・判断の強調（色ではなく太字）
1図で使う色相は最大3（NEUTRALは数えない）、地の塗りは最大4種。文字と地色のコントラスト比は4.5以上。
数値を使う図は作らず、定性的な塗り分けと配置だけで示す。
"""
from __future__ import annotations
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'

# --- 中立 ---
BG = '#fcfdfd'; INK = '#18324b'; T1 = '#223e53'; T2 = '#36556d'; MUTED = '#55646d'
LINE = '#607a91'; STROKE = '#8ea6b2'; NEUTRAL = '#eef3f1'; WATER = '#d6e6f2'
# --- 役割色（地 / 線 / 文字） ---
PRIMARY = '#e1edf8'; PRI_TEXT = '#2b5f9e'
AI = '#e9e4f5'; AI_LINE = '#8a6cc1'; AI_TEXT = '#6a4ea6'
POSITIVE = '#e0f0e9'; POS_LINE = '#5aa06f'; POS_TEXT = '#2f6b45'
ATTENTION = '#f7e9d4'; ATT_LINE = '#c0604a'; ATT_TEXT = '#9c3f2a'

PALETTE = {BG, INK, T1, T2, MUTED, LINE, STROKE, NEUTRAL, WATER,
           PRIMARY, PRI_TEXT, AI, AI_LINE, AI_TEXT, POSITIVE, POS_LINE, POS_TEXT, ATTENTION, ATT_LINE, ATT_TEXT}
FONT = 'font-family="sans-serif"'
MIN_FONT = 14
NOTE_FONT = 16


def esc(s: str) -> str:
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def est_w(s: str, size: float) -> float:
    """文字幅の保守的な概算。ASCIIは0.6em、それ以外（全角・矢印・記号）は1.0em。"""
    return sum(size * (0.6 if ord(c) < 0x80 else 1.0) for c in s)


def text(x, y, s, size=17, weight=400, fill=T2, anchor='middle', extra=''):
    size = max(size, MIN_FONT)
    w = f' font-weight="{weight}"' if weight != 400 else ''
    return f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" {FONT} font-size="{size:g}"{w} fill="{fill}"{extra}>{esc(s)}</text>'


def lines(x, y, rows, size=14, weight=400, fill=T2, anchor='middle', lh=None):
    """複数行テキスト。rows の各要素は文字列か (文字列, weight, fill) のタプル。"""
    lh = lh or size + 6
    out = []
    for i, r in enumerate(rows):
        if isinstance(r, tuple):
            s, wt, fl = r
        else:
            s, wt, fl = r, weight, fill
        if s:
            out.append(text(x, y + i * lh, s, size, wt, fl, anchor))
    return ''.join(out)


def title(s):
    return text(50, 50, s, 24, 700, INK, 'start')


def rect(x, y, w, h, fill, stroke=STROKE, sw=1, rx=12, dashed=False):
    dash = ' stroke-dasharray="8 6"' if dashed else ''
    return f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>'


def box(x, y, w, h, fill, head, sub=None, hs=20, ss=15, stroke=STROKE, sw=1, head_fill=T1):
    out = [rect(x, y, w, h, fill, stroke, sw)]
    cx = x + w / 2
    if sub:
        out.append(text(cx, y + h / 2 - 4, head, hs, 700, head_fill))
        out.append(text(cx, y + h / 2 + 20, sub, ss))
    else:
        out.append(text(cx, y + h / 2 + 7, head, hs, 700, head_fill))
    return ''.join(out)


def pill(x, y, w, h, s, fill=NEUTRAL, size=14, weight=400, color=T1, stroke=STROKE, sw=1):
    return rect(x, y, w, h, fill, stroke, sw, rx=h / 2) + text(x + w / 2, y + h / 2 + size * 0.36, s, size, weight, color)


def arrow(x1, y1, x2, y2, dashed=False, color=LINE, width=3):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
    ex, ey = x2 - ux * 10, y2 - uy * 10
    nx, ny = -uy, ux
    dash = ' stroke-dasharray="8 6"' if dashed else ''
    return (f'<path d="M{x1:.1f} {y1:.1f} L{ex:.1f} {ey:.1f}" stroke="{color}" stroke-width="{width}" fill="none"{dash}/>'
            f'<polygon points="{x2:.1f},{y2:.1f} {x2 - ux * 12 + nx * 7:.1f},{y2 - uy * 12 + ny * 7:.1f} {x2 - ux * 12 - nx * 7:.1f},{y2 - uy * 12 - ny * 7:.1f}" fill="{color}"/>')


def path_arrow(d, end, color=LINE, dashed=False, width=3):
    x, y, ux, uy = end; nx, ny = -uy, ux
    dash = ' stroke-dasharray="8 6"' if dashed else ''
    return (f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="none"{dash}/>'
            f'<polygon points="{x:.1f},{y:.1f} {x - ux * 12 + nx * 7:.1f},{y - uy * 12 + ny * 7:.1f} {x - ux * 12 - nx * 7:.1f},{y - uy * 12 - ny * 7:.1f}" fill="{color}"/>')


def bracket(x1, x2, y, label, color=LINE, size=15, weight=700, up=True, tick=12):
    """横方向のブラケット。up=True なら線の上にラベル。"""
    sgn = -1 if up else 1
    d = f'M{x1} {y + sgn * tick} V{y} H{x2} V{y + sgn * tick}'
    ly = y - tick - 10 if up else y + tick + size + 6
    return (f'<path d="{d}" stroke="{color}" stroke-width="2" fill="none"/>'
            + text((x1 + x2) / 2, ly, label, size, weight, color))


def note(y, s, size=NOTE_FONT):
    """図下部の注記。幅880pxを超える場合は句点（なければ中央付近の読点）で2行に折り返す。"""
    if est_w(s, size) <= 880:
        return text(500, y, s, size, 400, MUTED)
    cut = s.find('。')
    if not (0 < cut < len(s) - 1):
        cut = s.rfind('、', 0, len(s) // 2 + 6)
    parts = [s[:cut + 1], s[cut + 1:]]
    return lines(500, y, parts, size, 400, MUTED, lh=22)


CAPTION_MAX = 30  # キャプション（aria-label＝記事の alt）の最大文字数


def svg(w, h, caption, body, desc=''):
    """caption は図の主題を表す名詞句（全角30字以内、要素の列挙はしない）。記事の alt とキャプションになる。
    desc は図の内容の詳しい説明で、SVG を直接開いたときの支援技術向けに <desc> として残す。"""
    if len(caption) > CAPTION_MAX:
        raise ValueError(f'caption too long ({len(caption)} > {CAPTION_MAX}): {caption}')
    d = f'<desc id="desc">{esc(desc)}</desc>\n' if desc else ''
    aria = ' aria-describedby="desc"' if desc else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(caption)}"{aria}>\n'
            f'{d}<rect width="100%" height="100%" fill="{BG}"/>\n' + '\n'.join(body) + '\n</svg>\n')


# =====================================================================
# §1 生成の高速化と検証のボトルネック
# =====================================================================
def fig_01_generation_vs_verification():
    body = [title('生成が速くなるほど、検証がリードタイムを決める')]
    x0 = 200
    segs_before = [('生成', 360, PRIMARY), ('検証', 230, NEUTRAL), ('手戻り・環境維持', 150, NEUTRAL)]
    segs_after = [('生成', 110, PRIMARY), ('検証', 230, ATTENTION), ('手戻り・環境維持', 150, NEUTRAL)]
    for (label, sub, segs, y, hl) in [('生成AI以前', '生成に時間の比重', segs_before, 120, False),
                                       ('生成AI以後', '検証が全体を左右', segs_after, 250, True)]:
        body.append(lines(x0 - 30, y + 28, [(label, 700, T1), (sub, 400, MUTED)], 16, anchor='end', lh=22))
        x = x0
        for name, w, fill in segs:
            focus = hl and name == '検証'
            body.append(rect(x, y, w, 64, fill, ATT_LINE if focus else STROKE, 2 if focus else 1, rx=8))
            body.append(text(x + w / 2, y + 38, name, 16, 700, ATT_TEXT if focus else T1))
            x += w
        body.append(arrow(x0, y + 90, x, y + 90, color=STROKE, width=2))
        body.append(text((x0 + x) / 2, y + 110, 'リードタイム', 14, 400, MUTED))
    body.append(path_arrow('M700 325 H780 V290', (780, 290, 0, -1), color=ATT_LINE, dashed=True, width=2))
    body.append(lines(790, 318, [('検証が', 700, ATT_TEXT), ('クリティカルパスに', 700, ATT_TEXT)], 15, anchor='start', lh=20))
    body.append(text(500, 410, '生成の高速化 ≠ 開発全体の生産性向上', 20, 700, INK))
    body.append(note(445, '生成・検証・手戻り・環境維持まで含めて評価する。検証の短縮が、生成の高速化で得た余力を全体へ波及させる'))
    body.append(note(475, '帯の長さは概念的な比率であり、実測値ではない'))
    return svg(1000, 500, '生成AI以前と以後のリードタイム', body, desc='生成AI以前と以後の工程の帯を比べ、生成が短くなった後も検証の帯が残り、全体のリードタイムを左右することを示す図')


# =====================================================================
# §2 動的検証の5活動
# =====================================================================
def fig_02_dynamic_verification_activities():
    body = [title('動的検証の5つの活動と、自動化・AIが削減してきた範囲')]
    steps = [('テスト設計', '何を確かめるか'), ('テスト実装', 'どう確かめるか'), ('テスト実行', '実際に動かす'),
             ('結果判定', '正しいか比較する'), ('原因分析・保守', '失敗原因の調査と修正')]
    bw, bh, gap, y = 164, 86, 26, 190
    xs = [60 + i * (bw + gap) for i in range(5)]
    for i, ((h, s), x) in enumerate(zip(steps, xs)):
        focus = i == 3
        body.append(rect(x, y, bw, bh, ATTENTION if focus else NEUTRAL, ATT_LINE if focus else STROKE, 2 if focus else 1))
        body.append(text(x + bw / 2, y + 36, h, 18, 700, ATT_TEXT if focus else T1))
        body.append(text(x + bw / 2, y + 62, s, 14))
        if i < 4:
            body.append(arrow(x + bw, y + bh / 2, x + bw + gap, y + bh / 2, width=2))
    body.append(bracket(xs[0], xs[1] + bw, y - 24, '2023年〜 生成AI・AIエージェントが下書き・生成を支援', AI_TEXT, 15))
    body.append(bracket(xs[4], xs[4] + bw, y - 24, '修復を支援', AI_TEXT, 15))
    body.append(bracket(xs[1], xs[2] + bw, y + bh + 24, '2004年〜 テスト自動化が主に削減してきた範囲', POS_TEXT, 15, up=False))
    body.append(path_arrow(f'M{xs[3] + bw / 2:.0f} {y + bh + 30} V{y + bh + 70}', (xs[3] + bw / 2, y + bh + 72, 0, 1), color=ATT_LINE, dashed=True, width=2))
    body.append(lines(xs[3] + bw / 2, y + bh + 96, [('期待結果の正当性と', 700, ATT_TEXT), ('テストの十分性の判断が残る', 700, ATT_TEXT)], 14, lh=19))
    body.append(note(430, '静的検証は生成直後のワークフローに組み込みやすい。動的検証には実行環境・テストデータ・操作手順・期待結果・証跡が要る'))
    return svg(1000, 472, '動的検証の5活動と自動化・AIの範囲', body, desc='テスト設計、実装、実行、結果判定、原因分析・保守の5工程を並べ、従来の自動化が削減した実装・実行の範囲と、生成AIが支援する設計・実装・修復の範囲、残る判断を示す図')


# =====================================================================
# §3 画面テスト自動化の年表
# =====================================================================
def fig_03_gui_test_timeline():
    body = [title('画面テスト自動化の7つの転換点')]
    items = [
        ('2004年〜', 'Selenium', ['ブラウザ操作の自動化', '操作の反復実行']),
        ('2006年〜', 'Selenium IDE', ['記録・再生', 'テスト実装の入口']),
        ('2008〜2013年', 'クラウド実行環境', ['Sauce Labs・BrowserStack', 'ブラウザ・OSの実行環境管理']),
        ('2017〜2020年', 'ノーコード型SaaS', ['テストの作成・実行・', '管理・保守の統合']),
        ('2020〜2022年', '事例の蓄積・先例化', ['導入効果の定量化', '後続の導入判断の材料に']),
        ('2023〜2024年', '生成AI', ['テストケース・コードの', '作成支援（下書き）']),
        ('2025年〜', 'AIエージェント', ['計画・生成・実行・修復', 'の複数工程を横断']),
    ]
    axis_y = 280
    bw, bh = 234, 104
    body.append(f'<path d="M60 {axis_y} H940" stroke="{STROKE}" stroke-width="3"/>')
    body.append(f'<polygon points="952,{axis_y} 938,{axis_y - 7} 938,{axis_y + 7}" fill="{STROKE}"/>')
    for i, (year, name, improved) in enumerate(items):
        cx = 137 + i * 121
        up = i % 2 == 0
        by = axis_y - 40 - bh if up else axis_y + 40
        body.append(f'<circle cx="{cx}" cy="{axis_y}" r="7" fill="{BG}" stroke="{LINE}" stroke-width="3"/>')
        body.append(f'<path d="M{cx} {axis_y - 7 if up else axis_y + 7} V{by + bh if up else by}" stroke="{LINE}" stroke-width="2"/>')
        body.append(rect(cx - bw / 2, by, bw, bh, NEUTRAL))
        rows = [(year, 700, INK), (name, 700, T1)] + [(t, 400, T2) for t in improved]
        body.append(lines(cx, by + 26, rows, 14, lh=20))
    body.append(note(482, '年代は技術・サービスの登場時期を示し、普及完了時期ではない。横軸は等間隔で、縮尺ではない'))
    return svg(1000, 512, '画面テスト自動化の7つの転換点', body, desc='2004年のSeleniumから2025年のAIエージェントまで、画面テスト自動化の7つの転換点を時間軸上に並べ、それぞれが主に改善したものを示す年表')


# =====================================================================
# §4 TASとSUT（2点）
# =====================================================================
def fig_04a_tas_sut_systems():
    body = [title('テスト自動化はもう一つのシステム（TAS）を生む')]
    body.append(box(60, 100, 340, 104, PRIMARY, 'SUT（System Under Test）', 'テスト対象のシステム。業務アプリケーションなど', 17, 14))
    body.append(box(600, 100, 340, 104, PRIMARY, 'TAS（Test Automation System）', 'テストスクリプト、実行制御、結果取得など', 17, 14))
    body.append(arrow(400, 152, 600, 152, color=ATT_LINE))
    body.append(lines(500, 128, [('機能追加・画面変更', 700, ATT_TEXT), ('→ テストの変更が必要に', 700, ATT_TEXT)], 14, lh=19))
    causes = [('ライブラリ更新', 124), ('ブラウザのバージョン変更', 194), ('テストデータ整備', 138), ('実行環境の障害対応', 152)]
    x = 310
    for i, (c, w) in enumerate(causes):
        body.append(pill(x, 262, w, 34, c, ATTENTION, 14))
        body.append(arrow(x + w / 2, 262, 660 + (i - 1.5) * 50, 206, color=LINE, width=2))
        x += w + 12
    body.append(text(770, 326, 'TAS自身にも保守が発生する', 15, 700, T1))
    body.append(note(380, 'SUTの変更に追従する修正と、TAS自身の更新・障害対応の両方が、自動化の後も継続して発生する'))
    return svg(1000, 408, 'SUTの変更とTAS自身の保守', body, desc='テスト対象のSUTと、テストを自動実行するTASの二つのシステムを並べ、SUTの機能追加や画面変更がTASのテスト修正を生むことと、TAS自身にもライブラリ更新、ブラウザのバージョン変更、テストデータ整備、実行環境の障害対応が発生することを示す図')


def fig_04b_exchange_balance():
    body = [title('人手によるテスト実行の削減は、TASの構築・保守の負担と交換されている')]
    fx, by = 500, 118
    body.append(f'<path d="M{fx - 250} {by} H{fx + 250}" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>')
    body.append(f'<polygon points="{fx},{by} {fx - 30},{by + 66} {fx + 30},{by + 66}" fill="{LINE}"/>')
    body.append(f'<path d="M{fx - 70} {by + 66} H{fx + 70}" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>')
    body.append(f'<circle cx="{fx}" cy="{by}" r="8" fill="{BG}" stroke="{LINE}" stroke-width="3"/>')
    for sx in (-250, 250):
        body.append(f'<path d="M{fx + sx} {by} V{by + 36}" stroke="{LINE}" stroke-width="2"/>')
    body.append(rect(fx - 390, by + 36, 280, 96, POSITIVE, POS_LINE, 2))
    body.append(lines(fx - 250, by + 64, [('削減されるもの', 700, POS_TEXT), ('人手によるテスト実行', 700, T1), ('反復実行にかかる工数', 400, T2)], 15, lh=22))
    body.append(rect(fx + 110, by + 36, 280, 96, ATTENTION, ATT_LINE, 2))
    body.append(lines(fx + 250, by + 64, [('交換で生まれる負担', 700, ATT_TEXT), ('TASの構築・保守', 700, T1), ('SUT変更への追従、TAS自身の更新', 400, T2)], 15, lh=22))
    body.append(text(fx, by + 100, '経済的に成立するか', 15, 700, INK))
    body.append(note(292, '自動化の価値は、この交換が経済的に成立するかどうかで決まる'))
    return svg(1000, 318, '削減される工数とTASの負担の交換', body, desc='天秤の図。左の皿に削減されるものとして人手によるテスト実行、右の皿に交換で生まれる負担としてTASの構築・保守を載せ、自動化の価値はこの交換が経済的に成立するかどうかで決まることを示す')


# =====================================================================
# §5 時代ごとのTASコスト要素の移転
# =====================================================================
def fig_05_cost_shift_by_era():
    body = [title('TASのコスト要素は、時代ごとにどこへ移ったか')]
    cols = [('自前の', 'Selenium', '2004年〜'), ('クラウド', '実行環境', '2008年〜'), ('ノーコード型', 'SaaS', '2017年〜'), ('AIエージェント', '＋Playwright', '2025年〜')]
    rows = ['テスト設計・ケース作成', 'テストコード作成', '実行環境', '定期実行・証跡', 'テスト修復', 'SUT固有の期待結果・データ']
    S, R, P, K = 'self', 'reduce', 'provider', 'keep'
    grid = [
        [S, S, R, R],
        [S, S, R, R],
        [S, P, P, S],
        [S, S, P, S],
        [S, S, P, R],
        [K, K, K, K],
    ]
    style = {
        S: (NEUTRAL, '自社で担う', T1, STROKE, 1),
        R: (AI, '支援で軽減', AI_TEXT, STROKE, 1),
        P: (POSITIVE, '提供者が担う', POS_TEXT, STROKE, 1),
        K: (ATTENTION, '利用者側に残る', ATT_TEXT, ATT_LINE, 2),
    }
    x0, y0, lw, cw, rh, hh = 60, 84, 250, 158, 50, 84
    for j, (n1, n2, yr) in enumerate(cols):
        cx = x0 + lw + j * cw + cw / 2
        body.append(lines(cx, y0 + 20, [(n1, 700, T1), (n2, 700, T1), (yr, 400, MUTED)], 14, lh=20))
    for i, rname in enumerate(rows):
        y = y0 + hh + i * rh
        body.append(f'<path d="M{x0} {y} H{x0 + lw + 4 * cw}" stroke="{STROKE}" stroke-width="1"/>')
        body.append(text(x0 + lw - 14, y + rh / 2 + 5, rname, 15, 700, T1, 'end'))
        for j in range(4):
            fill, label, color, stroke, sw = style[grid[i][j]]
            bx = x0 + lw + j * cw + 5
            body.append(rect(bx, y + 5, cw - 10, rh - 10, fill, stroke, sw, rx=8))
            body.append(text(bx + (cw - 10) / 2, y + rh / 2 + 5, label, 14, 700, color))
    yb = y0 + hh + len(rows) * rh
    body.append(f'<path d="M{x0} {yb} H{x0 + lw + 4 * cw}" stroke="{STROKE}" stroke-width="1"/>')
    lx = 70
    legend = {R: '支援で軽減（GUI・AI）'}
    for key in (S, R, P, K):
        fill, label, color, stroke, sw = style[key]
        label = legend.get(key, label)
        body.append(rect(lx, yb + 22, 22, 16, fill, stroke, sw, rx=4))
        body.append(text(lx + 30, yb + 35, label, 14, 400, T2, 'start'))
        lx += est_w(label, 14) + 60
    body.append(note(yb + 72, 'AIエージェントは作成・修復を軽減するが、実行環境と定期実行・証跡は再び利用者側へ戻る。期待結果とデータの責任はどの時代も残る'))
    return svg(1000, yb + 122, '時代ごとのTASコスト要素の担い手', body, desc='テスト設計、コード作成、実行環境、定期実行・証跡、修復、期待結果・データの6要素について、自前Selenium、クラウド実行環境、ノーコード型SaaS、AIエージェントとPlaywrightの4時代で、自社で担うか、支援で軽減されるか、提供者が担うか、利用者側に残るかを塗り分けた格子図')


# =====================================================================
# §7 運用要素の氷山
# =====================================================================
def fig_07_iceberg_of_operation():
    body = [title('AIが下げるのは作成部分。水面下に運用要素が残る')]
    wl = 240
    body.append(f'<rect x="0" y="{wl}" width="1000" height="{676 - wl}" fill="{WATER}"/>')
    body.append(f'<path d="M0 {wl} H1000" stroke="{LINE}" stroke-width="2" stroke-dasharray="10 8"/>')
    poly_above = f'500,90 560,135 620,185 650,{wl} 350,{wl} 380,185 440,135'
    poly_below = f'650,{wl} 820,340 860,440 760,560 600,610 400,610 240,560 140,440 180,340 350,{wl}'
    body.append(f'<polygon points="{poly_above}" fill="{AI}" stroke="{STROKE}" stroke-width="2"/>')
    body.append(f'<polygon points="{poly_below}" fill="{NEUTRAL}" stroke="{STROKE}" stroke-width="2"/>')
    body.append(text(500, 200, 'テストコード生成・修復', 16, 700, AI_TEXT))
    body.append(f'<path d="M660 150 H730" stroke="{AI_LINE}" stroke-width="2"/>')
    body.append(lines(740, 140, [('作成部分', 700, AI_TEXT), ('AIエージェントで短時間に', 400, T2), ('行えるようになった', 400, T2)], 15, anchor='start', lh=20))
    body.append(text(120, wl - 12, '見えやすい部分', 14, 400, MUTED, 'start'))
    body.append(text(120, wl + 22, '見えにくい部分', 14, 400, MUTED, 'start'))
    items = ['CI Runnerの構築・管理', 'ブラウザ・依存パッケージの更新', '認証情報・アクセス権限の管理', 'テスト実行対象環境の準備',
             'テストデータの初期化・管理', '実行結果・証跡の保存', '実行失敗時の原因調査', '障害発生時の復旧・再実行']
    for i, s in enumerate(items):
        col, row = i % 2, i // 2
        body.append(pill(230 + col * 280, 300 + row * 48, 260, 36, s, BG, 14, 400, T1))
    body.append(text(500, 540, '継続的にテストを動かすための運用要素（残る部分）', 16, 700, ATT_TEXT))
    body.append(note(636, 'これらはAIで設定ファイルを生成すれば完了する仕事ではなく、更新確認・切り分け・運用責任を含めて管理し続ける必要がある'))
    return svg(1000, 676, '作成部分と水面下の運用要素', body, desc='氷山の図。水面上の小さな部分がAIエージェントで短時間に行えるテストコード生成・修復で、水面下の大きな部分にCI Runner、ブラウザ更新、認証情報、対象環境、テストデータ、証跡、原因調査、復旧という8つの運用要素が残ることを示す')


# =====================================================================
# §8 2022年の判断
# =====================================================================
def fig_08_2022_decision_context():
    body = [title('2022年の判断を形づくった5つの条件')]
    conds = [('8.1 先行事例の存在', '導入判断の不確実性を減らす材料があった'),
             ('8.2 保守開発が約8割', '内部構造の変更を伴う施策は適用しにくい'),
             ('8.3 技術スタックの多様さ', '画面E2Eは内部実装に依存しにくく横断できる'),
             ('8.4 JSP中心の画面実装', 'フロントエンド単体のテスト層を持ちにくい'),
             ('8.5 CI/CD成熟度の制約', '実行基盤の構築・保守を自前で持ちにくい')]
    for i, (h, s) in enumerate(conds):
        y = 96 + i * 84
        body.append(box(60, y, 400, 68, NEUTRAL, h, s, 17, 14))
        body.append(arrow(460, y + 34, 560, 304, width=2))
    body.append(rect(560, 222, 380, 164, PRIMARY, INK, 2))
    body.append(lines(750, 260, [('2022年の判断', 700, INK), ('SaaS型の画面E2Eテスト自動化', 700, T1)], 18, lh=28))
    body.append(lines(750, 324, ['狙い：限られた専門人材で、', '多様な既存案件へ横展開できる', '検証効率化策を選ぶ'], 14, lh=19))
    body.append(note(552, 'ホワイトボックステストの価値を否定した判断ではない。個別案件での最大効果より、横展開できることを重視した'))
    return svg(1000, 584, '2022年の判断を形づくった5つの条件', body, desc='先行事例の存在、保守開発が約8割、技術スタックの多様さ、JSP中心の画面実装、CI/CD成熟度の制約という5つの条件が、SaaS型の画面E2Eテスト自動化という2022年の判断へ収束することを示す図')


# =====================================================================
# §9.1 一度動かす技術と動かし続ける技術
# =====================================================================
def fig_09_run_once_vs_keep_running():
    body = [title('専門性は、テストを一度動かす技術ではなく、動かし続ける技術にある')]
    ay = 300
    body.append(f'<path d="M70 {ay} H930" stroke="{STROKE}" stroke-width="3"/>')
    body.append(f'<polygon points="944,{ay} 930,{ay - 7} 930,{ay + 7}" fill="{STROKE}"/>')
    body.append(text(930, ay + 30, '時間', 14, 400, MUTED, 'end'))
    body.append(f'<circle cx="150" cy="{ay}" r="22" fill="{POSITIVE}" stroke="{POS_LINE}" stroke-width="3"/>')
    body.append(f'<path d="M139 {ay} l8 8 l15 -16" stroke="{POS_LINE}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    body.append(lines(150, ay - 48, [('初回成功', 700, POS_TEXT), ('生成したテストが動く', 400, T2)], 14, lh=19))
    events = ['SUTの画面変更', 'ブラウザ・依存ライブラリの更新', 'テストデータの変化', '実行環境の障害']
    for i, e in enumerate(events):
        x = 330 + i * 185
        body.append(f'<path d="M{x} {ay - 14} V{ay + 14}" stroke="{ATT_LINE}" stroke-width="4"/>')
        body.append(f'<circle cx="{x}" cy="{ay}" r="9" fill="{ATT_LINE}"/>')
        body.append(text(x, ay - 48, e, 14, 700, ATT_TEXT))
        body.append(text(x, ay - 28, 'テスト失敗', 14, 400, T2))
        body.append(pill(x - 88, ay + 36, 176, 32, '切り分け→修正→再実行', NEUTRAL, 14, 400, T1))
    body.append(bracket(100, 200, 205, '一度動かす技術', MUTED, 15))
    body.append(bracket(250, 900, 205, '動かし続ける技術（専門性の所在）', ATT_TEXT, 16))
    body.append(text(500, 410, '失敗のたびに「SUTの不具合か、テストコードの問題か、実行環境の問題か」を切り分ける', 15, 700, INK))
    body.append(note(440, '切り分けには複数の技術領域にまたがる知識が要る。初回に動いただけでは、継続運用できるTASを構築したとはいえない'))
    return svg(1000, 470, '一度動かす技術と動かし続ける技術', body, desc='1本のテストの時間軸。初回成功の後に、画面変更、ブラウザ更新、テストデータの変化、実行環境の障害が順に起きてテストが失敗し、そのたびに切り分けと修正と再実行が必要になることで、専門性が動かし続ける側にあることを示す図')


# =====================================================================
# §1 生成と検証（定義）
# =====================================================================
def fig_01a_generation_and_verification():
    body = [title('生成はつくる作業、検証は確かめる作業')]
    for x, head, sub, left, right, mid, foot in [
        (60, '生成', '要求から成果物をつくる', '要求', '成果物', 'つくる', '生成AI・開発者が行う。生成AIの登場で高速化した'),
        (520, '検証', '成果物が要求を満たすかを確かめる', '成果物', '判定', '要求と照合', '満たせば次の工程へ、満たさなければ手戻り'),
    ]:
        body.append(rect(x, 90, 420, 190, PRIMARY, LINE, 2))
        body.append(text(x + 210, 124, head, 18, 700, PRI_TEXT))
        body.append(text(x + 210, 148, sub, 14))
        body.append(pill(x + 30, 176, 140, 36, left, BG, 15, 700, T1))
        body.append(arrow(x + 170, 194, x + 250, 194, width=2))
        body.append(text(x + 210, 182, mid, 14, 700, T1))
        body.append(pill(x + 250, 176, 140, 36, right, BG, 15, 700, T1))
        body.append(text(x + 210, 252, foot, 14, 400, T2))
    body.append(note(332, '生成が速くなっても、検証が同じ割合で速くなるとは限らない'))
    return svg(1000, 358, '生成と検証', body, desc='左に生成（要求から成果物をつくる作業。生成AIの登場で高速化した）、右に検証（成果物が要求を満たすかを確かめる作業。満たせば次の工程へ、満たさなければ手戻り）を並べた2パネルの図')


# =====================================================================
# §4 SUTとTAS（定義）
# =====================================================================
def fig_04a_sut_and_tas():
    body = [title('SUTはテスト対象、TASはテストを自動実行するシステム')]
    panels = [
        (60, 'SUT（System Under Test）', 'テスト対象のシステム。業務アプリケーションなど', ['画面', 'API', '業務ロジック', 'データ']),
        (520, 'TAS（Test Automation System）', 'テストを自動実行・制御するシステム', ['テストスクリプト', '実行制御', '結果取得・証跡', '実行環境・テストデータ']),
    ]
    for x, head, sub, items in panels:
        body.append(rect(x, 90, 420, 200, PRIMARY, LINE, 2))
        body.append(text(x + 210, 124, head, 17, 700, PRI_TEXT))
        body.append(text(x + 210, 148, sub, 14))
        for i, it in enumerate(items):
            body.append(pill(x + 24 + (i % 2) * 190, 170 + (i // 2) * 46, 182, 34, it, BG, 14, 400, T1))
    body.append(arrow(520, 190, 480, 190, width=3))
    body.append(text(500, 172, 'テスト実行', 14, 700, T1))
    body.append(note(342, 'SUTは機能追加や画面変更で変わり続け、TASはその変更に追従する。TASはテストを自動化すると新たに生まれるもう一つのシステム'))
    return svg(1000, 390, 'SUTとTAS', body, desc='左にSUT（テスト対象のシステム。画面、API、業務ロジック、データ）、右にTAS（テストを自動実行・制御するシステム。テストスクリプト、実行制御、結果取得・証跡、実行環境・テストデータ）を並べ、TASからSUTへテスト実行の矢印を引いた図')


# =====================================================================
# §8 2022年の転換
# =====================================================================
def fig_08a_2022_saas_shift():
    body = [title('2022年の転換：テスト自動化SaaSの利用で安定したコスト効果を創出')]
    body.append(rect(60, 100, 260, 130, NEUTRAL))
    body.append(lines(190, 130, [('それ以前', 700, T1), ('案件ごとに自動化環境を構築し、', 400, T2), ('投資効果を個別に検証していた', 400, T2)], 14, lh=22))
    body.append(arrow(320, 165, 370, 165))
    body.append(rect(370, 100, 260, 130, PRIMARY, LINE, 2))
    body.append(lines(500, 130, [('2022年の転換', 700, PRI_TEXT), ('テスト自動化SaaSを利用し、', 400, T2), ('多様な既存案件へ横展開', 400, T2)], 14, lh=22))
    body.append(arrow(630, 165, 680, 165))
    body.append(rect(680, 100, 260, 130, POSITIVE, POS_LINE, 2))
    body.append(lines(810, 130, [('安定したコスト効果', 700, POS_TEXT), ('実行基盤と運用をサービス側へ', 400, T2), ('先行事例で効果を見積もれる', 400, T2), ('技術スタックを問わず適用', 400, T2)], 14, lh=22))
    body.append(note(290, '狙いは、限られた専門人材で、多様な既存案件に横展開できる検証効率化策を選ぶこと'))
    return svg(1000, 316, '2022年の転換とその効果', body, desc='左の「それ以前」（案件ごとに自動化環境を構築し投資効果を個別に検証）から、中央の「2022年の転換」（テスト自動化SaaSの利用と横展開）を経て、右の「安定したコスト効果」（実行基盤と運用の外部化、先行事例による見積り、技術スタックを問わない適用）へ至る3段の図')


# =====================================================================
# §2 静的検証と動的検証
# =====================================================================
def fig_02a_static_vs_dynamic():
    body = [title('検証は、動かさない検証と動かす検証に分かれる')]
    y, h = 90, 160
    for x, fill, head, sub, items, head_fill in [
        (60, NEUTRAL, '静的検証', '実行を伴わない調査', ['要件・設計のレビュー', '型チェック', '静的解析', 'コードレビュー'], T1),
        (530, PRIMARY, '動的検証', '実行による振る舞いの確認', ['単体テスト', 'APIテスト', '画面テスト', '性能テスト'], PRI_TEXT),
    ]:
        body.append(rect(x, y, 410, h, fill))
        body.append(text(x + 205, y + 30, head, 18, 700, head_fill))
        body.append(text(x + 205, y + 54, sub, 14))
        for i, it in enumerate(items):
            px = x + 18 + (i % 2) * 194
            py = y + 76 + (i // 2) * 42
            body.append(pill(px, py, 180, 32, it, BG, 14, 400, T1))
    body.append(text(735, 282, '必要になるもの：実行環境・テストデータ・操作手順・期待結果・証跡', 14, 700, T1))
    body.append(note(322, '静的検証は生成直後のワークフローに組み込みやすい。以降は動的検証、とくに画面テストの自動化を扱う'))
    return svg(1000, 346, '静的検証と動的検証の区分', body, desc='左に実行を伴わない静的検証（要件・設計のレビュー、型チェック、静的解析、コードレビュー）、右に実行による動的検証（単体テスト、APIテスト、画面テスト、性能テスト）を並べ、動的検証には実行環境、テストデータ、操作手順、期待結果、証跡が必要になることを示す図')


# =====================================================================
# §6 責任の境界
# =====================================================================
def fig_06_responsibility_boundary():
    body = [title('機能の一部はSaaS事業者が担う。責任はSIerに残る')]
    bx = 500
    body.append(f'<path d="M{bx} 92 V452" stroke="{LINE}" stroke-width="2" stroke-dasharray="10 8"/>')
    body.append(text(bx, 476, '役割の境界', 14, 700, MUTED))
    body.append(text(260, 118, 'SaaS事業者が担う機能', 16, 700, POS_TEXT))
    left = ['クラウド上での実行', 'スケジュール実行', '結果ログ', '通知', 'テストの自動修復', '操作説明などの利用者サポート']
    for i, label in enumerate(left):
        body.append(pill(70, 142 + i * 46, 380, 34, label, POSITIVE, 14, 400, T1))
    body.append(text(740, 118, 'SIer（利用者）に残る役割と責任', 16, 700, ATT_TEXT))
    right = ['テスト対象の仕様の理解', '期待結果の定義', 'テストデータ・アカウントの準備', 'テストの十分性判断']
    for i, label in enumerate(right):
        body.append(pill(550, 142 + i * 46, 380, 34, label, ATTENTION, 14, 400, T1))
    body.append(note(520, 'ノーコード型SaaSは左側の範囲が広い。検証の責任はSIer側に残り、サービス利用料とベンダーへの依存は別途評価する'))
    return svg(1000, 546, 'SaaS事業者が担う機能とSIerに残る役割', body, desc='縦の破線の境界の左に、SaaS事業者が担う機能（クラウド上での実行、スケジュール実行、結果ログ、通知、テストの自動修復、操作説明などの利用者サポート）、右にSIer（利用者）に残る役割と責任（テスト対象の仕様の理解、期待結果の定義、テストデータ・アカウントの準備、テストの十分性判断）を並べた図')


# =====================================================================
# §8.2 保守開発の比率
# =====================================================================
def fig_08a_maintenance_share():
    body = [title('案件の約8割は保守開発')]
    x0, y, w, h = 60, 110, 880, 60
    wm = w * 0.8
    body.append(rect(x0, y, wm, h, ATTENTION, ATT_LINE, 2, rx=8))
    body.append(rect(x0 + wm, y, w - wm, h, NEUTRAL, STROKE, 1, rx=8))
    body.append(text(x0 + wm / 2, y + 37, '保守開発　約8割', 18, 700, ATT_TEXT))
    body.append(text(x0 + wm + (w - wm) / 2, y + 37, '新規開発', 16, 700, T1))
    body.append(text(x0 + wm / 2, 206, 'ソースコードや内部設計の変更範囲が限られ、テスト容易性のための内部構造の変更が難しい', 14, 400, T2))
    body.append(note(246, '比率は本文の「約8割」に基づく概数。ホワイトボックステストの改善施策を全社横断で適用しにくい前提になる'))
    return svg(1000, 272, '保守開発と新規開発の比率', body, desc='横1本の帯を保守開発約8割と新規開発に分け、保守開発では内部構造の変更が難しいことを示す図')


# =====================================================================
# §8.3 技術スタックに依存しにくい画面E2E
# =====================================================================
def fig_08b_stack_agnostic_e2e():
    body = [title('画面E2Eテストは、SUTの実装技術に依存しにくい')]
    body.append(box(300, 90, 400, 70, PRIMARY, '画面E2Eテスト', '利用者から見える画面操作とその結果を検証', 17, 14, head_fill=PRI_TEXT))
    suts = [('JSP', 'サーバーサイド描画'), ('SPA', 'クライアント側描画'), ('JS多用のWebアプリ', '動的な画面更新'), ('レガシーWebアプリ', '既存の技術構成')]
    for i, (head, sub) in enumerate(suts):
        x = 70 + i * 220
        body.append(box(x, 250, 190, 76, NEUTRAL, head, sub, 16, 14))
        body.append(arrow(500, 160, x + 95, 250, width=2))
    body.append(text(500, 232, '同じ検証のしかた', 14, 700, T1))
    body.append(note(372, '画面の実装技術が異なれば、要素特定や非同期処理への対応などの個別調整は必要になる'))
    return svg(1000, 398, '画面E2Eテストと4種類のSUT', body, desc='上の画面E2Eテストから、JSP、SPA、JavaScriptを多用するWebアプリ、レガシーWebアプリという4つのSUTへ同じ矢印が伸び、実装技術に依存しにくいことを示す図')


# =====================================================================
# §10.1 TASの総コストの内訳
# =====================================================================
def fig_10a_tco_breakdown():
    body = [title('TASの総コストは、テストコードの作成費だけではない')]
    parts = ['テスト設計・実装費', '実行基盤の構築費', 'テスト修復・基盤保守費', '定期実行・障害対応費', 'ツール・クラウド利用料']
    x0, y, w, h = 60, 130, 176, 60
    for i, label in enumerate(parts):
        x = x0 + i * w
        first = i == 0
        body.append(rect(x, y, w, h, AI if first else NEUTRAL, STROKE, 1, rx=8 if first or i == 4 else 0))
        body.append(text(x + w / 2, y + 36, label, 14, 700, AI_TEXT if first else T1))
    body.append(text(x0 + w / 2, 110, 'AIエージェントが主に下げる部分', 14, 700, AI_TEXT))
    body.append(bracket(x0 + w, x0 + 5 * w, y + h + 24, '継続運用で発生し続ける部分', T1, 15, up=False))
    body.append(note(292, '区分は等幅で描いており、金額の比率ではない。ROIは便益を過大計上せず、この総コストと比較して評価する'))
    return svg(1000, 318, 'TASの総コストの5区分', body, desc='横1本の帯を、テスト設計・実装費、実行基盤の構築費、テスト修復・基盤保守費、定期実行・障害対応費、ツール・クラウド利用料の5区分に分け、AIエージェントが主に下げるのは左端の1区分だけであることを示す図')


# =====================================================================
# §10.2 成熟度による選択（2パターン）と §10.3 推進方針
# =====================================================================
def _pattern(title_s, conds, choice_fill, choice_stroke, choice_head, choice_head_fill, reasons, caption, desc):
    body = [title(title_s)]
    for i, (h, s) in enumerate(conds):
        y = 100 + i * 78
        body.append(box(60, y, 380, 62, NEUTRAL, h, s, 16, 14))
        body.append(arrow(440, y + 31, 540, 206, width=2))
    body.append(rect(540, 112, 400, 188, choice_fill, choice_stroke, 2))
    body.append(text(740, 148, choice_head, 18, 700, choice_head_fill))
    body.append(lines(560, 184, ['・' + r for r in reasons], 14, anchor='start', lh=24))
    body.append(text(60, 92, '組織・案件の状態', 14, 700, MUTED, 'start'))
    body.append(text(540, 92, '適した選択肢と理由', 14, 700, MUTED, 'start'))
    body.append(note(364, '一般的な傾向であり、個々の製品機能、契約条件、システム制約によって判断は変わる'))
    return svg(1000, 390, caption, body, desc=desc)


def fig_10b_pattern_saas():
    return _pattern('パターンA：ノーコード型SaaSが適する組織・案件',
                    [('CI/CD成熟度が低い', '共通の実行基盤・標準設定・運用体制がない'),
                     ('保守開発中心・技術スタックが多様', '内部構造を変えにくく、案件ごとに技術が異なる'),
                     ('自動化の専門人材が不足', '案件ごとに専門家を配置できない')],
                    PRIMARY, LINE, 'ノーコード型SaaS', PRI_TEXT,
                    ['実行基盤・運用負担の外部化', 'ブラックボックス型E2Eテストの汎用性', '導入・運用の専門知識への依存低減'],
                    'パターンA：ノーコード型SaaSが適する条件',
                    'CI/CD成熟度が低い、保守開発中心で技術スタックが多様、自動化の専門人材が不足という3つの状態から、ノーコード型SaaSが適することを、実行基盤・運用負担の外部化、ブラックボックス型E2Eテストの汎用性、専門知識への依存低減という理由とともに示す図')


def fig_10c_pattern_playwright():
    return _pattern('パターンB：Playwright＋AIエージェントが適する組織・案件',
                    [('CI/CD基盤が共通化済み', '実行環境・標準設定・運用手順が整っている'),
                     ('テストコードの高度な制御が必要', 'ノーコードでは表現しにくい検証がある'),
                     ('基盤を保守する共通チームが存在', '案件横断で基盤保守を引き受けられる')],
                    AI, AI_LINE, 'Playwright＋AIエージェント', AI_TEXT,
                    ['既存CI/CD基盤の再利用', 'テストコードの実装自由度の高さ', '基盤保守コストの共通化'],
                    'パターンB：Playwright＋AIが適する条件',
                    'CI/CD基盤が共通化済み、テストコードの高度な制御が必要、基盤を保守する共通チームが存在という3つの状態から、PlaywrightとAIエージェントが適することを、既存基盤の再利用、実装自由度の高さ、基盤保守コストの共通化という理由とともに示す図')


def fig_10d_short_and_long_term():
    body = [title('短期はSaaSで効果を得て、中長期は共通基盤と運用能力を整える')]
    body.append(rect(60, 100, 400, 120, PRIMARY, LINE, 2))
    body.append(lines(260, 134, [('短期', 700, PRI_TEXT), ('SaaSで検証効率化の効果を獲得する', 700, T1), ('CI/CD基盤が未成熟な案件でも効果を得やすい', 400, T2)], 15, lh=24))
    body.append(arrow(460, 160, 540, 160, dashed=True, color=INK))
    body.append(rect(540, 100, 400, 120, AI, AI_LINE, 2))
    body.append(lines(740, 134, [('中長期', 700, AI_TEXT), ('共通CI/CD基盤と運用能力を整備する', 700, T1), ('PlaywrightなどのOSSを活用できる案件を増やす', 400, T2)], 15, lh=24))
    body.append(note(270, 'SaaSとOSSの排他的な選択ではなく、それぞれを適切な条件で利用できる状態を目指す'))
    return svg(1000, 296, '短期と中長期の推進方針', body, desc='左の短期（SaaSで検証効率化の効果を獲得する）から、右の中長期（共通CI/CD基盤と運用能力を整備し、PlaywrightなどのOSSを活用できる案件を増やす）へ破線の矢印でつないだ図')


def fig_10e_policy_routing():
    body = [title('案件への当てはめ')]
    rows = [
        ('SPAの案件', 'コンポーネント構成で単体の層を持てる', PRIMARY, LINE, PRI_TEXT,
         ['Vitest・Storybook・Playwrightで', 'E2E以前の確認を広げ、繰り返し安定して', '回せるCI環境を整える']),
        ('JSPの案件', 'E2Eの比重が大きく、環境が整ってから着手', PRIMARY, LINE, PRI_TEXT,
         ['SaaSの利用を推奨', '実行基盤を自前で構築する時間を', '取りにくいため']),
        ('CI/CD成熟度が低い保守開発案件', '共通の実行基盤・運用体制がない', PRIMARY, LINE, PRI_TEXT,
         ['SaaSクラウドを使う', '実行基盤と運用をサービス側へ', '']),
        ('例外：テスト情報をSaaSクラウドに', '載せる顧客許諾がどうしても得られない', ATTENTION, ATT_LINE, ATT_TEXT,
         ['PlaywrightでTASを構築する', '共通基盤・運用体制の整備と', 'あわせて進める']),
    ]
    for i, (h, s, fill, stroke, hf, lines_) in enumerate(rows):
        y = 92 + i * 94
        body.append(box(60, y, 400, 76, NEUTRAL, h, s, 16, 14))
        body.append(arrow(460, y + 38, 520, y + 38, width=2))
        body.append(rect(520, y, 420, 76, fill, stroke, 2 if fill == ATTENTION else 1))
        body.append(lines(730, y + 24, [(lines_[0], 700, hf)] + [(t, 400, T2) for t in lines_[1:] if t], 14, lh=20))
    body.append(note(492, 'SaaSとOSSは排他ではない。案件の状態に応じて使い分け、中長期で共通基盤を整える'))
    return svg(1000, 518, '案件ごとの推進方針', body, desc='SPAの案件、JSPの案件、CI/CD成熟度が低い保守開発案件、テスト情報をSaaSクラウドに載せる顧客許諾が得られない例外の4行について、それぞれの方針（E2E以前の確認の拡充とCI整備、SaaSの推奨、SaaSクラウドの利用、PlaywrightによるTAS構築）を矢印で対応づけた図')


# =====================================================================
# §5 負担の移り変わり（流れ）
# =====================================================================
def fig_05a_burden_shift_flow():
    body = [title('テストを動かし続ける仕組みを、自社で作る負担はどう減ったか')]
    steps = [
        ('Seleniumの初期', ['操作スクリプトも実行環境も', '自社で準備'], ['（出発点）']),
        ('Selenium IDE', ['テストの作成負担を軽減'], ['画面変更に伴う修正']),
        ('クラウド実行環境', ['ブラウザ・OSの用意と維持の', '一部を提供者へ'], ['テスト作成・期待結果・', '業務データの準備']),
        ('ノーコード型SaaS', ['作成・実行スケジュール・', '結果と証跡・修復を一体提供'], ['期待結果・データ・', '十分性の判断']),
    ]
    bw, gap, y = 214, 20, 120
    body.append(text(60, 104, '減った負担', 14, 700, POS_TEXT, 'start'))
    body.append(text(60, 280, '残った負担', 14, 700, ATT_TEXT, 'start'))
    for i, (name, reduced, remain) in enumerate(steps):
        x = 60 + i * (bw + gap)
        body.append(rect(x, y, bw, 110, NEUTRAL))
        body.append(text(x + bw / 2, y + 28, name, 16, 700, T1))
        body.append(lines(x + bw / 2, y + 54, reduced, 14, 400, T2, lh=19))
        body.append(rect(x, 296, bw, 64, ATTENTION if i else BG, ATT_LINE if i else STROKE, 1))
        body.append(lines(x + bw / 2, 320, remain, 14, 400, ATT_TEXT if i else MUTED, lh=19))
        if i < 3:
            body.append(arrow(x + bw, y + 55, x + bw + gap, y + 55, width=2))
    body.append(note(412, 'ノーコード型SaaSにより、テストを動かし続けるための仕組みそのものを自社で作る負担を減らせるようになった'))
    return svg(1000, 438, '自社で担う負担の移り変わり', body, desc='Seleniumの初期、Selenium IDE、クラウド実行環境、ノーコード型SaaSの4段階について、上段に減った負担（作成負担の軽減、実行環境の一部の外部化、作成・実行・証跡・修復の一体提供）、下段に残った負担（画面変更に伴う修正、作成・期待結果・業務データ、期待結果・データ・十分性の判断）を並べた流れ図')


FIGURES = {
    '01a-generation-and-verification': fig_01a_generation_and_verification,
    '01b-generation-vs-verification': fig_01_generation_vs_verification,
    '02a-static-vs-dynamic': fig_02a_static_vs_dynamic,
    '02b-dynamic-verification-activities': fig_02_dynamic_verification_activities,
    '03-gui-test-timeline': fig_03_gui_test_timeline,
    '04a-sut-and-tas': fig_04a_sut_and_tas,
    '04b-tas-sut-systems': fig_04a_tas_sut_systems,
    '04c-exchange-balance': fig_04b_exchange_balance,
    '05a-burden-shift-flow': fig_05a_burden_shift_flow,
    '05b-cost-shift-by-era': fig_05_cost_shift_by_era,
    '06-responsibility-boundary': fig_06_responsibility_boundary,
    '07-iceberg-of-operation': fig_07_iceberg_of_operation,
    '08a-2022-saas-shift': fig_08a_2022_saas_shift,
    '08b-maintenance-share': fig_08a_maintenance_share,
    '08c-stack-agnostic-e2e': fig_08b_stack_agnostic_e2e,
    '08d-2022-decision-context': fig_08_2022_decision_context,
    '09-run-once-vs-keep-running': fig_09_run_once_vs_keep_running,
    '10a-tco-breakdown': fig_10a_tco_breakdown,
    '10b-pattern-saas': fig_10b_pattern_saas,
    '10c-pattern-playwright': fig_10c_pattern_playwright,
    '10d-short-and-long-term': fig_10d_short_and_long_term,
    '10e-policy-routing': fig_10e_policy_routing,
}



def main():
    ASSETS.mkdir(exist_ok=True)
    for name, fn in FIGURES.items():
        (ASSETS / f'{name}.svg').write_text(fn(), encoding='utf-8')
        print('wrote', name)


if __name__ == '__main__':
    main()

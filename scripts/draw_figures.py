#!/usr/bin/env python3
"""記事「生成と検証から考えるテスト自動化の歴史とコスト構造」の図版（全10点）を決定論的に生成する。

体裁：幅1000px、最小フォント14px、注記16px、Python標準ライブラリのみ。配色・関数構成は
yamaguchiyoshito/sier-resource-series の scripts/draw_figures.py に合わせる。
数値を使う図は作らず、定性的な塗り分けと配置だけで示す。
"""
from __future__ import annotations
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'

BG = '#fcfdfd'; INK = '#18324b'; T1 = '#223e53'; T2 = '#36556d'; MUTED = '#5d6c75'
LINE = '#607a91'; STROKE = '#8ea6b2'; ACCENT = '#c0604a'; GREEN = '#5aa06f'; PURPLE = '#8a6cc1'; BAR = '#9dbbd3'; SOFT = '#eef3f1'
FILLS = ['#e1edf8', '#e0f0e9', '#f7e9d4', '#e9e4f5', '#f6e4e8']
WATER = '#d6e6f2'
FONT = 'font-family="sans-serif"'
MIN_FONT = 14


def esc(s: str) -> str:
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def est_w(s: str, size: float) -> float:
    """文字幅の概算。全角1.0em、半角0.55em。"""
    return sum(size * (0.55 if ord(c) < 0x2E80 else 1.0) for c in s)


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
        out.append(text(x, y + i * lh, s, size, wt, fl, anchor))
    return ''.join(out)


def title(s):
    return text(50, 50, s, 24, 700, INK, 'start')


def rect(x, y, w, h, fill, stroke=STROKE, sw=1, rx=12, dashed=False):
    dash = ' stroke-dasharray="8 6"' if dashed else ''
    return f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>'


def box(x, y, w, h, fill, head, sub=None, hs=20, ss=15, stroke=STROKE, sw=1):
    out = [rect(x, y, w, h, fill, stroke, sw)]
    cx = x + w / 2
    if sub:
        out.append(text(cx, y + h / 2 - 4, head, hs, 700, T1))
        out.append(text(cx, y + h / 2 + 20, sub, ss))
    else:
        out.append(text(cx, y + h / 2 + 7, head, hs, 700, T1))
    return ''.join(out)


def pill(x, y, w, h, s, fill=SOFT, size=14, weight=400, color=T1, stroke=STROKE, sw=1):
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
    """横方向の波括弧風ブラケット。up=True なら線の上にラベル。"""
    sgn = -1 if up else 1
    d = f'M{x1} {y + sgn * tick} V{y} H{x2} V{y + sgn * tick}'
    ly = y - tick - 10 if up else y + tick + size + 6
    return (f'<path d="{d}" stroke="{color}" stroke-width="2" fill="none"/>'
            + text((x1 + x2) / 2, ly, label, size, weight, color))


NOTE_FONT = 16


def note(y, s, size=NOTE_FONT):
    """図下部の注記。幅880pxを超える場合は句点（なければ中央付近の読点）で2行に折り返す。"""
    if est_w(s, size) <= 880:
        return text(500, y, s, size, 400, MUTED)
    cut = s.find('。')
    if not (0 < cut < len(s) - 1):
        cut = s.rfind('、', 0, len(s) // 2 + 6)
    parts = [s[:cut + 1], s[cut + 1:]]
    return lines(500, y, parts, size, 400, MUTED, lh=22)


def svg(w, h, label, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">\n'
            f'<rect width="100%" height="100%" fill="{BG}"/>\n' + '\n'.join(body) + '\n</svg>\n')


# =====================================================================
# §1 生成の高速化と検証のボトルネック
# =====================================================================
def fig_01_generation_vs_verification():
    body = [title('生成が速くなるほど、検証がリードタイムを決める')]
    x0 = 230
    segs_before = [('生成', 400, FILLS[0]), ('検証', 240, FILLS[2]), ('手戻り・環境維持', 110, FILLS[3])]
    segs_after = [('生成', 120, FILLS[0]), ('検証', 240, FILLS[2]), ('手戻り・環境維持', 110, FILLS[3])]
    for (label, sub, segs, y, hl) in [('生成AI以前', '生成に時間の比重', segs_before, 120, False),
                                       ('生成AI以後', '検証が全体を左右', segs_after, 250, True)]:
        body.append(lines(x0 - 30, y + 28, [(label, 700, T1), (sub, 400, MUTED)], 16, anchor='end', lh=22))
        x = x0
        for name, w, fill in segs:
            stroke, sw = (ACCENT, 3) if (hl and name == '検証') else (STROKE, 1)
            body.append(rect(x, y, w, 64, fill, stroke, sw, rx=8))
            body.append(text(x + w / 2, y + 38, name, 16, 700, ACCENT if (hl and name == '検証') else T1))
            x += w
        body.append(arrow(x0, y + 90, x, y + 90, color=STROKE, width=2))
        body.append(text((x0 + x) / 2, y + 110, 'リードタイム', 14, 400, MUTED))
    body.append(path_arrow('M700 325 H780 V290', (780, 290, 0, -1), color=ACCENT, dashed=True))
    body.append(lines(790, 318, [('検証が', 700, ACCENT), ('クリティカルパスに', 700, ACCENT)], 15, anchor='start', lh=20))
    body.append(text(500, 410, '生成の高速化 ≠ 開発全体の生産性向上', 20, 700, INK))
    body.append(note(445, '生成・検証・手戻り・環境維持まで含めて評価する。検証の短縮が、生成の高速化で得た余力を全体へ波及させる'))
    body.append(note(475, '帯の長さは概念的な比率であり、実測値ではない'))
    return svg(1000, 500, '生成AI以前と以後の工程の帯を比べ、生成が短くなった後も検証の帯が残り、全体のリードタイムを左右することを示す図', body)


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
        stroke, sw = (ACCENT, 3) if i == 3 else (STROKE, 1)
        body.append(rect(x, y, bw, bh, FILLS[i], stroke, sw))
        body.append(text(x + bw / 2, y + 36, h, 18, 700, T1))
        body.append(text(x + bw / 2, y + 62, s, 14))
        if i < 4:
            body.append(arrow(x + bw, y + bh / 2, x + bw + gap, y + bh / 2, width=2))
    # 上：生成AI・エージェントの支援範囲（設計・実装、修復）
    body.append(bracket(xs[0], xs[1] + bw, y - 24, '2023年〜 生成AI・AIエージェントが下書き・生成を支援', PURPLE, 15))
    body.append(bracket(xs[4], xs[4] + bw, y - 24, '修復を支援', PURPLE, 15))
    # 下：従来の自動化の範囲（実装・実行）
    body.append(bracket(xs[1], xs[2] + bw, y + bh + 24, '2004年〜 テスト自動化が主に削減してきた範囲', LINE, 15, up=False))
    body.append(path_arrow(f'M{xs[3] + bw / 2:.0f} {y + bh + 30} V{y + bh + 70}', (xs[3] + bw / 2, y + bh + 72, 0, 1), color=ACCENT, dashed=True, width=2))
    body.append(lines(xs[3] + bw / 2, y + bh + 96, [('期待結果の正当性と', 700, ACCENT), ('テストの十分性の判断が残る', 700, ACCENT)], 14, lh=19))
    body.append(note(430, '静的検証は生成直後のワークフローに組み込みやすい。動的検証には実行環境・テストデータ・操作手順・期待結果・証跡が要る'))
    return svg(1000, 472, 'テスト設計、実装、実行、結果判定、原因分析・保守の5工程を並べ、従来の自動化が削減した実装・実行の範囲と、生成AIが支援する設計・実装・修復の範囲、残る判断を示す図', body)


# =====================================================================
# §3 画面テスト自動化の年表
# =====================================================================
def fig_03_gui_test_timeline():
    body = [title('画面テスト自動化の転換点と、各時期に残った課題')]
    items = [
        ('2004年〜', 'Selenium', ['ブラウザ操作の自動化', '改善：操作の反復実行'], '残：スクリプトの作成・保守'),
        ('2006年〜', 'Selenium IDE', ['記録・再生', '改善：テスト実装の入口'], '残：SUT変更への追従'),
        ('2008〜2013年', 'クラウド実行環境', ['Sauce Labs・BrowserStack', '改善：実行環境の管理'], '残：設計・実装・運用の調整'),
        ('2017〜2020年', 'ノーコード型SaaS', ['作成・実行・管理・保守の統合'], '残：業務知識・期待結果・対象環境'),
        ('2020〜2022年', '事例の蓄積・先例化', ['導入効果の定量化と横展開'], '残：構築費・保守費込みの再現性'),
        ('2023〜2024年', '生成AI', ['テスト設計・実装の下書き'], '残：生成結果の妥当性・実行基盤'),
        ('2025年〜', 'AIエージェント', ['計画・生成・実行・修復の連携'], '残：継続運用・品質判断・独立性'),
    ]
    axis_y = 300
    bw, bh = 228, 118
    body.append(f'<path d="M60 {axis_y} H940" stroke="{STROKE}" stroke-width="3"/>')
    body.append(f'<polygon points="952,{axis_y} 938,{axis_y - 7} 938,{axis_y + 7}" fill="{STROKE}"/>')
    for i, (year, name, improved, remain) in enumerate(items):
        cx = 137 + i * 121
        up = i % 2 == 0
        by = axis_y - 40 - bh if up else axis_y + 40
        body.append(f'<circle cx="{cx}" cy="{axis_y}" r="7" fill="{BG}" stroke="{LINE}" stroke-width="3"/>')
        body.append(f'<path d="M{cx} {axis_y - 7 if up else axis_y + 7} V{by + bh if up else by}" stroke="{LINE}" stroke-width="2"/>')
        bx = cx - bw / 2
        body.append(rect(bx, by, bw, bh, FILLS[i % 5]))
        rows = [(year, 700, ACCENT), (name, 700, T1)] + [(s, 400, T2) for s in improved] + [(remain, 400, MUTED)]
        body.append(lines(cx, by + 24, rows, 14, lh=19))
    body.append(note(520, '年代は技術・サービスの登場時期を示し、普及完了時期ではない。横軸は等間隔で、縮尺ではない'))
    return svg(1000, 550, '2004年のSeleniumから2025年のAIエージェントまで7つの転換点を時間軸上に並べ、それぞれが改善したものと残った課題を示す年表', body)


# =====================================================================
# §4 TASとSUT
# =====================================================================
def fig_04_tas_sut_exchange():
    body = [title('テスト自動化はもう一つのシステム（TAS）を生む')]
    body.append(box(70, 100, 320, 104, FILLS[0], 'SUT（System Under Test）', 'テスト対象のシステム。業務アプリケーションなど', 18, 14))
    body.append(box(610, 100, 320, 104, FILLS[2], 'TAS（Test Automation System）', 'テストスクリプト、実行制御、結果取得など', 18, 14))
    body.append(arrow(390, 152, 610, 152, color=ACCENT))
    body.append(lines(500, 128, [('機能追加・画面変更', 700, ACCENT), ('→ テストの変更が必要に', 400, ACCENT)], 14, lh=19))
    # TAS自身の保守要因
    causes = [('ライブラリ更新', 124), ('ブラウザのバージョン変更', 194), ('テストデータ整備', 138), ('実行環境の障害対応', 152)]
    x = 310
    for i, (c, w) in enumerate(causes):
        body.append(pill(x, 262, w, 34, c, FILLS[4], 14))
        body.append(arrow(x + w / 2, 262, 660 + (i - 1.5) * 50, 206, color=LINE, width=2))
        x += w + 12
    body.append(text(770, 326, 'TAS自身にも保守が発生する', 15, 700, T1))
    # 天秤
    fx, fy = 500, 470
    body.append(f'<polygon points="{fx},{fy - 10} {fx - 26},{fy + 36} {fx + 26},{fy + 36}" fill="{LINE}"/>')
    body.append(f'<path d="M{fx - 230} {fy - 20} L{fx + 230} {fy - 40}" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>')
    body.append(f'<path d="M{fx - 230} {fy - 20} V{fy + 10}" stroke="{LINE}" stroke-width="2"/>')
    body.append(f'<path d="M{fx + 230} {fy - 40} V{fy - 10}" stroke="{LINE}" stroke-width="2"/>')
    body.append(rect(fx - 360, fy + 10, 260, 60, FILLS[1], GREEN, 2))
    body.append(lines(fx - 230, fy + 34, [('削減されるもの', 700, GREEN), ('人手によるテスト実行', 400, T1)], 14, lh=19))
    body.append(rect(fx + 100, fy - 10, 260, 60, FILLS[2], ACCENT, 2))
    body.append(lines(fx + 230, fy + 14, [('交換で生まれる負担', 700, ACCENT), ('TASの構築・保守', 400, T1)], 14, lh=19))
    body.append(text(500, 392, '人手によるテスト実行の削減は、TASを構築・保守する負担と交換されている', 17, 700, INK))
    body.append(note(572, '自動化の価値は、この交換が経済的に成立するかどうかで決まる'))
    return svg(1000, 600, 'テスト対象のSUTと、テストを自動実行するTASの二つのシステムを並べ、SUTの変更がTASの修正を生み、TAS自身にも更新や障害対応が発生すること、そして人手のテスト実行の削減とTASの構築・保守の負担が天秤で交換されていることを示す図', body)


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
        S: (FILLS[4], '自社で担う', T1, STROKE, 1),
        R: (FILLS[0], '支援で軽減', T1, STROKE, 1),
        P: (FILLS[1], '提供者が担う', GREEN, STROKE, 1),
        K: (FILLS[2], '利用者側に残る', ACCENT, ACCENT, 2),
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
    # 凡例
    lx = 70
    for key in (S, R, P, K):
        fill, label, color, stroke, sw = style[key]
        body.append(rect(lx, yb + 22, 22, 16, fill, stroke, sw, rx=4))
        body.append(text(lx + 30, yb + 35, label, 14, 400, T2, 'start'))
        lx += est_w(label, 14) + 60
    body.append(note(yb + 72, 'AIエージェントは作成・修復を軽減するが、実行環境と定期実行・証跡は再び利用者側へ戻る。期待結果とデータの責任はどの時代も残る'))
    return svg(1000, yb + 122, 'テスト設計、コード作成、実行環境、定期実行・証跡、修復、期待結果・データの6要素について、自前Selenium、クラウド実行環境、ノーコード型SaaS、AIエージェントとPlaywrightの4時代で、自社で担うか、支援で軽減されるか、提供者が担うか、利用者側に残るかを塗り分けた格子図', body)


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
    body.append(f'<polygon points="{poly_above}" fill="{SOFT}" stroke="{STROKE}" stroke-width="2"/>')
    body.append(f'<polygon points="{poly_below}" fill="{FILLS[0]}" stroke="{STROKE}" stroke-width="2"/>')
    body.append(text(500, 200, 'テストコード生成・修復', 16, 700, T1))
    body.append(f'<path d="M660 150 H730" stroke="{LINE}" stroke-width="2"/>')
    body.append(lines(740, 140, [('作成部分', 700, T1), ('AIエージェントで短時間に', 400, T2), ('行えるようになった', 400, T2)], 15, anchor='start', lh=20))
    body.append(text(120, wl - 12, '見えやすい部分', 14, 400, MUTED, 'start'))
    body.append(text(120, wl + 22, '見えにくい部分', 14, 400, MUTED, 'start'))
    items = ['CI Runnerの構築・管理', 'ブラウザ・依存パッケージの更新', '認証情報・アクセス権限の管理', 'テスト実行対象環境の準備',
             'テストデータの初期化・管理', '実行結果・証跡の保存', '実行失敗時の原因調査', '障害発生時の復旧・再実行']
    for i, s in enumerate(items):
        col, row = i % 2, i // 2
        x = 230 + col * 280
        y = 300 + row * 48
        body.append(pill(x, y, 260, 36, s, BG, 14, 400, T1))
    body.append(text(500, 540, '継続的にテストを動かすための運用要素（残る部分）', 16, 700, ACCENT))
    body.append(note(636, 'これらはAIで設定ファイルを生成すれば完了する仕事ではなく、更新確認・切り分け・運用責任を含めて管理し続ける必要がある'))
    return svg(1000, 676, '氷山の図。水面上の小さな部分がAIエージェントで短時間に行えるテストコード生成・修復で、水面下の大きな部分にCI Runner、ブラウザ更新、認証情報、対象環境、テストデータ、証跡、原因調査、復旧という8つの運用要素が残ることを示す', body)


# =====================================================================
# §8 2022年の判断
# =====================================================================
def fig_08_2022_decision_context():
    body = [title('2022年の判断を形づくった4つの条件')]
    conds = [('8.1 先行事例の存在', '導入判断の不確実性を減らす材料があった'),
             ('8.2 保守開発が約8割', '内部構造の変更を伴う施策は適用しにくい'),
             ('8.3 技術スタックの多様さ', '画面E2Eは内部実装に依存しにくく横断できる'),
             ('8.4 CI/CD成熟度の制約', '実行基盤の構築・保守を自前で持ちにくい')]
    for i, (h, s) in enumerate(conds):
        y = 96 + i * 84
        body.append(box(60, y, 400, 68, FILLS[i], h, s, 17, 14))
        body.append(arrow(460, y + 34, 560, 262, width=2))
    body.append(rect(560, 180, 380, 164, FILLS[2], ACCENT, 3))
    body.append(lines(750, 218, [('2022年の判断', 700, ACCENT), ('SaaS型の画面E2Eテスト自動化', 700, T1)], 18, lh=28))
    body.append(lines(750, 282, ['狙い：限られた専門人材で、', '多様な既存案件へ横展開できる', '検証効率化策を選ぶ'], 14, lh=19))
    body.append(note(468, 'ホワイトボックステストの価値を否定した判断ではない。個別案件での最大効果より、横展開できることを重視した'))
    return svg(1000, 500, '先行事例の存在、保守開発が約8割、技術スタックの多様さ、CI/CD成熟度の制約という4つの条件が、SaaS型の画面E2Eテスト自動化という2022年の判断へ収束することを示す図', body)


# =====================================================================
# §9.1 一度動かす技術と動かし続ける技術
# =====================================================================
def fig_09_run_once_vs_keep_running():
    body = [title('専門性は、テストを一度動かす技術ではなく、動かし続ける技術にある')]
    ay = 300
    body.append(f'<path d="M70 {ay} H930" stroke="{STROKE}" stroke-width="3"/>')
    body.append(f'<polygon points="944,{ay} 930,{ay - 7} 930,{ay + 7}" fill="{STROKE}"/>')
    body.append(text(930, ay + 30, '時間', 14, 400, MUTED, 'end'))
    # 初回成功
    body.append(f'<circle cx="150" cy="{ay}" r="22" fill="{FILLS[1]}" stroke="{GREEN}" stroke-width="3"/>')
    body.append(f'<path d="M139 {ay} l8 8 l15 -16" stroke="{GREEN}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    body.append(lines(150, ay - 48, [('初回成功', 700, GREEN), ('生成したテストが動く', 400, T2)], 14, lh=19))
    events = ['SUTの画面変更', 'ブラウザ・依存ライブラリの更新', 'テストデータの変化', '実行環境の障害']
    for i, e in enumerate(events):
        x = 330 + i * 185
        body.append(f'<path d="M{x} {ay - 14} V{ay + 14}" stroke="{ACCENT}" stroke-width="4"/>')
        body.append(f'<circle cx="{x}" cy="{ay}" r="9" fill="{ACCENT}"/>')
        body.append(text(x, ay - 48, e, 14, 700, ACCENT))
        body.append(text(x, ay - 28, 'テスト失敗', 14, 400, T2))
        body.append(pill(x - 80, ay + 36, 160, 32, '切り分け → 修正 → 再実行', FILLS[2], 14, 400, T1))
    body.append(bracket(100, 200, 205, '一度動かす技術', MUTED, 15))
    body.append(bracket(250, 900, 205, '動かし続ける技術（専門性の所在）', ACCENT, 16))
    body.append(text(500, 410, '失敗のたびに「SUTの不具合か、テストコードの問題か、実行環境の問題か」を切り分ける', 15, 700, T1))
    body.append(note(440, '切り分けには複数の技術領域にまたがる知識が要る。初回に動いただけでは、継続運用できるTASを構築したとはいえない'))
    return svg(1000, 470, '1本のテストの時間軸。初回成功の後に、画面変更、ブラウザ更新、テストデータの変化、実行環境の障害が順に起きてテストが失敗し、そのたびに切り分けと修正と再実行が必要になることで、専門性が動かし続ける側にあることを示す図', body)


# =====================================================================
# §10 成熟度による選択マップ
# =====================================================================
def fig_10_maturity_choice_map():
    body = [title('組織の成熟度で選択肢は変わる。短期と中長期を分けて考える')]
    px0, py0, pw, ph = 170, 90, 740, 390
    body.append(rect(px0, py0, pw, ph, BG, STROKE, 1, rx=0))
    body.append(arrow(px0, py0 + ph, px0 + pw + 20, py0 + ph, color=LINE, width=2))
    body.append(arrow(px0, py0 + ph, px0, py0 - 20, color=LINE, width=2))
    body.append(text(px0 + pw / 2, py0 + ph + 40, 'CI/CD成熟度（共通基盤・標準設定・運用手順・障害対応体制）', 15, 700, T1))
    body.append(text(px0 + 4, py0 + ph + 22, '低い', 14, 400, MUTED, 'start'))
    body.append(text(px0 + pw, py0 + ph + 22, '高い', 14, 400, MUTED, 'end'))
    body.append(text(px0 - 24, py0 + ph / 2, 'テスト基盤を保守する共通チーム', 15, 700, T1, 'middle', f' transform="rotate(-90 {px0 - 24} {py0 + ph / 2:.0f})"'))
    body.append(text(px0 - 48, py0 + ph - 6, 'なし', 14, 400, MUTED, 'middle', f' transform="rotate(-90 {px0 - 48} {py0 + ph - 6})"'))
    body.append(text(px0 - 48, py0 + 12, 'あり', 14, 400, MUTED, 'middle', f' transform="rotate(-90 {px0 - 48} {py0 + 12})"'))
    # SaaS領域（左下）
    body.append(rect(px0 + 16, py0 + 180, 360, 194, FILLS[0], LINE, 2))
    body.append(lines(px0 + 196, py0 + 210, [('ノーコード型SaaS', 700, T1)], 18))
    body.append(lines(px0 + 36, py0 + 242, ['・実行基盤・運用負担の外部化', '・ブラックボックス型E2Eの汎用性', '・導入・運用の専門知識への依存低減', '・保守開発中心・技術スタックが多様な案件向き'], 14, anchor='start', lh=22))
    # Playwright領域（右上）
    body.append(rect(px0 + 384, py0 + 16, 340, 194, FILLS[2], LINE, 2))
    body.append(lines(px0 + 554, py0 + 46, [('Playwright＋AIエージェント', 700, T1)], 18))
    body.append(lines(px0 + 404, py0 + 78, ['・既存CI/CD基盤の再利用', '・テストコードの実装自由度の高さ', '・基盤保守コストの共通化', '・高度な制御が必要な案件向き'], 14, anchor='start', lh=22))
    # 移行の矢印
    body.append(arrow(px0 + 376, py0 + 290, px0 + 520, py0 + 218, dashed=True, color=ACCENT, width=3))
    body.append(lines(px0 + 530, py0 + 300, [('中長期', 700, ACCENT), ('共通CI/CD基盤と運用能力を', 400, T2), ('整備し、OSSを活用できる', 400, T2), ('案件を増やす', 400, T2)], 14, anchor='start', lh=19))
    body.append(lines(px0 + 36, py0 + 140, [('短期', 700, ACCENT), ('SaaSで検証効率化の効果を先に得る', 400, T2)], 14, anchor='start', lh=19))
    body.append(note(550, 'SaaSとOSSの排他的な選択ではなく、それぞれを適切な条件で利用できる状態を目指す。個々の製品機能・契約条件・制約で判断は変わる'))
    return svg(1000, 598, '横軸をCI/CD成熟度、縦軸を基盤保守の共通チームの有無とした2軸のマップ。左下にノーコード型SaaSが適する領域、右上にPlaywrightとAIエージェントが適する領域を置き、短期はSaaSで効果を得て、中長期は共通基盤を整備して右上へ移る方針を破線の矢印で示す', body)


# =====================================================================
# §11 ボトルネックの移動
# =====================================================================
def fig_11_bottleneck_shift():
    body = [title('検証のボトルネックは、実行作業から二つの課題へ移った')]
    body.append(rect(60, 150, 220, 180, SOFT, STROKE, 1))
    body.append(lines(170, 200, [('従来のボトルネック', 700, MUTED), ('', 400, T2), ('単純な実行作業', 700, T1), ('テストの作成・実行・', 400, T2), ('保守にかかる作業', 400, T2)], 15, lh=22))
    body.append(arrow(280, 240, 360, 240, color=ACCENT, width=4))
    body.append(text(320, 222, '生成コスト低下後', 14, 700, ACCENT))
    # 第一層
    body.append(rect(360, 100, 580, 110, FILLS[0], LINE, 2))
    body.append(lines(380, 130, [('第一層　自動化を維持する能力', 700, T1)], 17, anchor='start'))
    body.append(lines(380, 158, ['TASを安定して運用するための基盤と組織能力。', 'テストが自動で作成・実行されても、継続運用コストはなくならない'], 14, anchor='start', lh=20))
    # 第二層
    body.append(rect(360, 230, 580, 230, FILLS[2], LINE, 2))
    body.append(lines(380, 260, [('第二層　正しさを判断する根拠', 700, T1)], 17, anchor='start'))
    chain = ['要件・設計・リスク', 'テスト観点', '期待結果', '証跡']
    cx = 380
    widths = [150, 110, 100, 80]
    for i, (s, w) in enumerate(zip(chain, widths)):
        body.append(pill(cx, 282, w, 36, s, BG, 14, 700, T1))
        if i < 3:
            body.append(arrow(cx + w, 300, cx + w + 24, 300, width=2))
        cx += w + 24
    body.append(text(380, 346, '要件・設計・リスクとテスト観点・期待結果を結び付け、検証の根拠を追跡できるようにする', 14, 400, T2, 'start'))
    body.append(rect(380, 366, 540, 76, BG, ACCENT, 2, dashed=True))
    body.append(lines(650, 396, [('注意：SUTの現在の振る舞いだけを根拠に期待結果を作ると、', 700, ACCENT), ('既存の不具合を正しい動作として固定してしまう', 700, ACCENT)], 14, lh=20))
    body.append(note(510, 'テストの十分性や期待結果の正しさは、自動的に作成・実行されても自動的には保証されない'))
    return svg(1000, 540, '左の従来のボトルネックである単純な実行作業から、右の二層の課題、第一層の自動化を維持する能力と、第二層の正しさを判断する根拠へ移ったことを示す図。第二層には要件・設計・リスク、テスト観点、期待結果、証跡をつなぐ追跡の鎖と、SUTの現状だけを根拠にすると不具合を固定するという注意を含む', body)


FIGURES = {
    '01-generation-vs-verification': fig_01_generation_vs_verification,
    '02-dynamic-verification-activities': fig_02_dynamic_verification_activities,
    '03-gui-test-timeline': fig_03_gui_test_timeline,
    '04-tas-sut-exchange': fig_04_tas_sut_exchange,
    '05-cost-shift-by-era': fig_05_cost_shift_by_era,
    '07-iceberg-of-operation': fig_07_iceberg_of_operation,
    '08-2022-decision-context': fig_08_2022_decision_context,
    '09-run-once-vs-keep-running': fig_09_run_once_vs_keep_running,
    '10-maturity-choice-map': fig_10_maturity_choice_map,
    '11-bottleneck-shift': fig_11_bottleneck_shift,
}


def main():
    ASSETS.mkdir(exist_ok=True)
    for name, fn in FIGURES.items():
        (ASSETS / f'{name}.svg').write_text(fn(), encoding='utf-8')
        print('wrote', name)


if __name__ == '__main__':
    main()

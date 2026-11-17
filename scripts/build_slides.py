#!/usr/bin/env python3
"""slides/deck.md から登壇用スライド（_site/slides/index.html）とトークスクリプト（_site/slides/script.html）を生成する。

deck.md の書式：スライドは `---` だけの行で区切る。各ブロックは次の行からなる。
  ## 見出し            メッセージ（1文。全角28字以内）
  type: title|section|summary|normal   省略時 normal
  section: 01 問題     ヘッダー左の章ラベル
  figure: assets/xx.svg  図（1点まで。箇条書きと併用しない）
  - 箇条書き           3項目まで
  message: 結論文      メッセージライン（1〜2文、全角64字以内）。スライド単体で読んで分かるようにする。表紙以外は必須
  sub: 補足1行         任意（全角40字以内）
  eyebrow: / date: / url:  表紙用
  appendix: true       予備スライド（原稿の合計には数えない）
  notes:               以降の行がトーク原稿（空行区切りの段落）
目安時間は原稿の文字数から 300字/分 で算出する。スライドにはキー操作用の最小限のインラインスクリプトだけを埋め込む。scripts/build.py の後に実行する（_site/ を前提にする）。
"""
from __future__ import annotations
import argparse
import html
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / 'slides/deck.md'
CSS = ROOT / 'site-src/slides.css'
CHARS_PER_MINUTE = 300
# スライド送りのキー操作だけを扱う最小限のスクリプト（外部通信なし、ライブラリなし）。
KEY_SCRIPT = ("(function(){var s=[].slice.call(document.querySelectorAll('.slide'));"
              "function cur(){var y=window.scrollY+window.innerHeight/2;for(var i=s.length-1;i>=0;i--){if(s[i].offsetTop<=y)return i;}return 0;}"
              "function go(i){i=Math.max(0,Math.min(s.length-1,i));s[i].scrollIntoView({behavior:'instant'});history.replaceState(null,'','#s'+(i+1));}"
              "document.addEventListener('keydown',function(e){if(e.metaKey||e.ctrlKey||e.altKey)return;var k=e.key;"
              "if(k==='ArrowRight'||k==='ArrowDown'||k==='PageDown'||k===' '||k==='Enter'){e.preventDefault();go(cur()+1);}"
              "else if(k==='ArrowLeft'||k==='ArrowUp'||k==='PageUp'||k==='Backspace'){e.preventDefault();go(cur()-1);}"
              "else if(k==='Home'){e.preventDefault();go(0);}else if(k==='End'){e.preventDefault();go(s.length-1);}});})();")


def parse_deck(text: str) -> list[dict]:
    blocks = re.split(r'^---\s*$', text, flags=re.M)
    slides = []
    for raw in blocks:
        if not raw.strip():
            continue
        slide = {'bullets': [], 'notes': '', 'type': 'normal', 'appendix': False}
        lines = raw.strip('\n').split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith('## '):
                slide['title'] = line[3:].strip()
            elif line.startswith('- '):
                slide['bullets'].append(line[2:].strip())
            elif line.startswith('notes:'):
                rest = line[len('notes:'):].strip()
                body = [rest] if rest else []
                body += lines[i + 1:]
                slide['notes'] = '\n'.join(body).strip()
                break
            elif ':' in line and not line.startswith(' '):
                key, _, value = line.partition(':')
                key = key.strip(); value = value.strip()
                if key == 'appendix':
                    slide['appendix'] = value.lower() == 'true'
                elif key:
                    slide[key] = value
            i += 1
        slides.append(slide)
    return slides


def note_chars(notes: str) -> int:
    return len(re.sub(r'\s', '', notes))


def seconds_for(notes: str) -> int:
    return math.ceil(note_chars(notes) / (CHARS_PER_MINUTE / 60))


def fmt_time(sec: int) -> str:
    return f'{sec // 60}分{sec % 60:02d}秒'


def figure_caption(figure: str) -> str:
    svg = (ROOT / figure).read_text(encoding='utf-8')
    m = re.search(r'aria-label="([^"]+)"', svg)
    return html.unescape(m.group(1)) if m else ''


def render_slide(s: dict, n: int, total: int, site: dict) -> str:
    kind = s['type']
    classes = f'slide type-{kind}' + (' appendix' if s['appendix'] else '')
    header = (f'<header><span class="sec">{html.escape(s.get("section", ""))}</span>'
              f'<span class="num" data-total="{total}"></span></header>')
    footer = (f'<footer><span>{html.escape(site["short_title"])} — {html.escape(site["date"])}</span>'
              f'<span>{html.escape(site["url"])}</span></footer>')
    if kind == 'title':
        main = (f'<main><p class="eyebrow">{html.escape(s.get("eyebrow", site.get("eyebrow", "")))}</p>'
                f'<h1>{html.escape(s["title"])}</h1>'
                f'<p class="meta">{html.escape(s.get("sub", ""))}</p><div class="spacer"></div></main>')
    elif kind == 'section':
        main = (f'<main><p class="chapter">{html.escape(s.get("section", ""))}</p><h1>{html.escape(s["title"])}</h1>'
                f'<p class="message">{html.escape(s.get("message", ""))}</p></main>')
    else:
        parts = [f'<h1>{html.escape(s["title"])}</h1>']
        if s.get('figure'):
            cap = figure_caption(s['figure'])
            parts.append(f'<figure><img src="../{html.escape(s["figure"])}" alt="{html.escape(cap)}"></figure>')
        elif s['bullets']:
            parts.append('<ul class="points">' + ''.join(f'<li>{html.escape(b)}</li>' for b in s['bullets']) + '</ul>')
        else:
            parts.append('<div class="spacer"></div>')
        parts.append(f'<p class="message">{html.escape(s.get("message", ""))}</p>')
        if s.get('sub'):
            parts.append(f'<p class="sub">{html.escape(s["sub"])}</p>')
        main = '<main>' + ''.join(parts) + '</main>'
    return f'<section class="{classes}" id="s{n}"><div class="frame">{header}{main}{footer}</div></section>'


def render_deck(slides: list[dict], site: dict, css: str) -> str:
    total = len(slides)
    body = ''.join(render_slide(s, i + 1, total, site) for i, s in enumerate(slides))
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(site["title"])} — 登壇用スライド</title>
<style>{css}</style></head><body>{body}
<script>{KEY_SCRIPT}</script></body></html>'''


def render_script(slides: list[dict], site: dict, css: str) -> str:
    main = [s for s in slides if not s['appendix']]
    extra = [s for s in slides if s['appendix']]
    total_chars = sum(note_chars(s['notes']) for s in main)
    total_sec = sum(seconds_for(s['notes']) for s in main)

    def article(s: dict, n: int) -> str:
        meta = [s.get('section', ''), f'目安 {seconds_for(s["notes"])}秒', f'{note_chars(s["notes"])}字']
        message = f'<p class="msg">{html.escape(s["message"])}</p>' if s.get('message') else ''
        if s.get('figure'):
            meta.append('図 ' + Path(s['figure']).stem)
        paras = ''.join(f'<p>{html.escape(p.strip())}</p>' for p in re.split(r'\n\s*\n', s['notes']) if p.strip())
        return (f'<article><h2>{n}. {html.escape(s["title"])}</h2>'
                f'<p class="meta">{html.escape(" · ".join(m for m in meta if m))}</p>{message}{paras}</article>')

    items = ''.join(article(s, i + 1) for i, s in enumerate(slides) if not s['appendix'])
    extras = ''.join(article(s, i + 1) for i, s in enumerate(slides) if s['appendix'])
    extra_html = f'<h2 class="appendix-head">予備（質疑・時間調整用）</h2>{extras}' if extra else ''
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(site["title"])} — トークスクリプト</title>
<style>{css}</style></head><body><div class="script">
<h1>トークスクリプト</h1>
<p class="lead">{html.escape(site["title"])} ／ 本編 {len(main)}枚、原稿 {total_chars}字、目安 {fmt_time(total_sec)}（{CHARS_PER_MINUTE}字/分）。
<a href="index.html">スライドを開く</a></p>{items}{extra_html}</div></body></html>'''


def build(output: Path) -> dict:
    site = json.loads((ROOT / 'site.json').read_text(encoding='utf-8'))
    site.setdefault('short_title', site['title'])
    site.setdefault('url', '')
    slides = parse_deck(DECK.read_text(encoding='utf-8'))
    css = CSS.read_text(encoding='utf-8')
    out = output / 'slides'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'index.html').write_text(render_deck(slides, site, css), encoding='utf-8')
    (out / 'script.html').write_text(render_script(slides, site, css), encoding='utf-8')
    main = [s for s in slides if not s['appendix']]
    return dict(slides=len(slides), main=len(main), appendix=len(slides) - len(main),
                chars=sum(note_chars(s['notes']) for s in main), seconds=sum(seconds_for(s['notes']) for s in main))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    args = parser.parse_args()
    if not args.output.exists():
        print('_site/ がない。先に scripts/build.py を実行する。', file=sys.stderr)
        return 1
    print(json.dumps(build(args.output), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

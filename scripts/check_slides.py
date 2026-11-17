#!/usr/bin/env python3
"""slides/deck.md と生成した _site/slides/ を検査する。問題があれば exit 1。

- 各スライドに見出しがあり、全角28字以内（表紙は40字以内）
- 図は1点以内で assets/ に実在し、箇条書き（3項目・各24字以内）と併用しない
- 表紙以外にメッセージライン（message）があり、64字以内
- 補足（sub）は40字以内
- 各スライドに原稿（notes）があり、本編は40〜160字、表紙・章扉・予備は10〜160字
- 本編の原稿合計は 2000〜2400字（300字/分で8分以内）
- 生成HTMLの <script> はスライド本体のキー操作用インライン1つだけ（外部スクリプトなし）で、相対リンク・画像が解決する
"""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_slides import DECK, parse_deck, note_chars  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'
TITLE_MAX, TITLE_MAX_COVER, BULLET_MAX, BULLETS, SUB_MAX, MESSAGE_MAX = 28, 40, 24, 3, 40, 64
NOTE_MIN, NOTE_MIN_LIGHT, NOTE_MAX, TOTAL_MIN, TOTAL_MAX = 40, 10, 160, 2000, 2400


class Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str]] = []
        self.scripts = 0
        self.external_scripts = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'script':
            self.scripts += 1
            if a.get('src'):
                self.external_scripts += 1
        for attr in ('href', 'src'):
            if a.get(attr):
                self.refs.append((attr, a[attr]))


def main() -> int:
    errors: list[str] = []
    slides = parse_deck(DECK.read_text(encoding='utf-8'))
    for i, s in enumerate(slides, 1):
        tag = f'slide {i}'
        title = s.get('title', '')
        if not title:
            errors.append(f'{tag}: 見出しが無い'); continue
        limit = TITLE_MAX_COVER if s['type'] == 'title' else TITLE_MAX
        if len(title) > limit:
            errors.append(f'{tag}: 見出しが{limit}字を超える（{len(title)}字）: {title}')
        if s.get('figure') and s['bullets']:
            errors.append(f'{tag}: 図と箇条書きを併用している')
        if s.get('figure') and not (ROOT / s['figure']).exists():
            errors.append(f'{tag}: 図が無い {s["figure"]}')
        if len(s['bullets']) > BULLETS:
            errors.append(f'{tag}: 箇条書きが{BULLETS}項目を超える')
        for b in s['bullets']:
            if len(b) > BULLET_MAX:
                errors.append(f'{tag}: 箇条書きが{BULLET_MAX}字を超える: {b}')
        msg = s.get('message', '')
        if s['type'] != 'title' and not msg:
            errors.append(f'{tag}: メッセージライン（message）が無い: {title}')
        if len(msg) > MESSAGE_MAX:
            errors.append(f'{tag}: メッセージラインが{MESSAGE_MAX}字を超える（{len(msg)}字）: {msg}')
        if len(s.get('sub', '')) > SUB_MAX:
            errors.append(f'{tag}: 補足が{SUB_MAX}字を超える: {s["sub"]}')
        n = note_chars(s['notes'])
        light = s['type'] in ('title', 'section') or s['appendix']
        lo = NOTE_MIN_LIGHT if light else NOTE_MIN
        if n < lo or n > NOTE_MAX:
            errors.append(f'{tag}: 原稿が{lo}〜{NOTE_MAX}字の範囲外（{n}字）: {title}')
    total = sum(note_chars(s['notes']) for s in slides if not s['appendix'])
    if not (TOTAL_MIN <= total <= TOTAL_MAX):
        errors.append(f'本編の原稿合計が{TOTAL_MIN}〜{TOTAL_MAX}字の範囲外（{total}字）')
    out = SITE / 'slides'
    if not out.exists():
        errors.append('_site/slides/ がない。先に scripts/build_slides.py を実行する')
    else:
        for page in sorted(out.glob('*.html')):
            c = Collector(); c.feed(page.read_text(encoding='utf-8'))
            allowed = 1 if page.name == 'index.html' else 0
            if c.scripts > allowed or c.external_scripts:
                errors.append(f'{page.relative_to(SITE)}: 許可されていない <script> を含む（スライド本体のキー操作用インライン1つだけ許可）')
            for attr, ref in c.refs:
                p = urlsplit(ref)
                if p.scheme or ref.startswith(('#', '//', 'data:')):
                    continue
                if not (page.parent / unquote(p.path)).resolve().exists():
                    errors.append(f'{page.relative_to(SITE)}: {attr}="{ref}" が解決しない')
    for e in errors:
        print(e, file=sys.stderr)
    print({'slides': len(slides), 'main_chars': total, 'errors': len(errors)})
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())

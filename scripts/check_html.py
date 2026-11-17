#!/usr/bin/env python3
"""生成した _site/ を検査する。相対リンクと画像の実在、ページ内アンカーの実在、外部スクリプト不在、
記事中の図版参照がすべて配置されていること、alt が30字以内であること、原稿に数式があればMathMLの存在を確認する。"""
from __future__ import annotations
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'
CAPTION_MAX = 30  # 図のキャプション（alt）の最大文字数。scripts/draw_figures.py と合わせる


class Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str]] = []
        self.scripts = 0
        self.math = 0
        self.images = 0
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == 'script':
            self.scripts += 1
        if tag == 'math':
            self.math += 1
        if tag == 'img':
            self.images += 1
            if not a.get('alt'):
                self.refs.append(('alt', a.get('src') or ''))
            elif len(a['alt']) > CAPTION_MAX:
                self.refs.append(('alt-long', a['alt']))
        if a.get('id'):
            self.ids.add(a['id'])
        for attr in ('href', 'src'):
            if a.get(attr):
                self.refs.append((attr, a[attr]))


def main() -> int:
    if not SITE.exists():
        print('_site/ がない。先に scripts/build.py を実行する。', file=sys.stderr)
        return 1
    site = json.loads((ROOT / 'site.json').read_text(encoding='utf-8'))
    source_text = (ROOT / site['article']).read_text(encoding='utf-8')
    expected_images = source_text.count('](assets/')
    errors: list[str] = []
    pages = sorted(SITE.rglob('*.html'))
    for page in pages:
        parser = Collector()
        parser.feed(page.read_text(encoding='utf-8'))
        if parser.scripts and page != SITE / 'slides' / 'index.html':
            errors.append(f'{page.relative_to(SITE)}: <script> を含む')
        if page == SITE / 'index.html' and '$' in source_text and parser.math == 0:
            errors.append(f'{page.relative_to(SITE)}: MathML が無い')
        if page == SITE / 'index.html' and parser.images != expected_images:
            errors.append(f'{page.relative_to(SITE)}: 図版が {parser.images} 点（原稿は {expected_images} 点）')
        for attr, ref in parser.refs:
            if attr == 'alt':
                errors.append(f'{page.relative_to(SITE)}: alt の無い画像 {ref}')
                continue
            if attr == 'alt-long':
                errors.append(f'{page.relative_to(SITE)}: alt が {CAPTION_MAX} 字を超える: "{ref}"')
                continue
            parsed = urlsplit(ref)
            if parsed.scheme or ref.startswith(('#', '//', 'data:')):
                if ref.startswith('#') and ref[1:] and ref[1:] not in parser.ids:
                    errors.append(f'{page.relative_to(SITE)}: ページ内アンカー {ref} が無い')
                continue
            target = (page.parent / unquote(parsed.path)).resolve()
            if not target.exists():
                errors.append(f'{page.relative_to(SITE)}: {attr}="{ref}" が解決しない')
    for e in errors:
        print(e, file=sys.stderr)
    print(json.dumps({'pages': len(pages), 'errors': len(errors)}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())

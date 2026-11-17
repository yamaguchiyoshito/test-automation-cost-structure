#!/usr/bin/env python3
"""_site/index.html から、インターネット接続なしで開ける単一HTML（_site/offline.html）を生成する。

CSS は build.py がすでに埋め込んでいるので、ここでは図（assets/*.svg）を data URI として <img> に埋め込み、
相対リンクを公開URLへの絶対リンク（記事題名のリンクはページ先頭）に書き換える。外部スクリプトやフォントは使っていないため、
生成したファイル1つだけを保存すれば、どこへ置いても同じ表示になる。scripts/build.py の後に実行する。"""
from __future__ import annotations
import argparse
import base64
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_NAME = 'offline.html'


def data_uri(path: Path) -> str:
    body = base64.b64encode(path.read_bytes()).decode('ascii')
    return f'data:image/svg+xml;base64,{body}'


def inline_images(page: str, site_dir: Path) -> tuple[str, int]:
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        src = m.group(2)
        target = site_dir / src
        if urlsplit(src).scheme or not target.exists():
            raise FileNotFoundError(f'埋め込む画像が無い: {src}')
        count += 1
        return f'{m.group(1)}{data_uri(target)}{m.group(3)}'

    page = re.sub(r'(<img\b[^>]*\bsrc=")([^"]+)(")', repl, page)
    return page, count


def absolutize_links(page: str, base_url: str) -> str:
    def repl(m: re.Match) -> str:
        href = m.group(2)
        if href.startswith('#') or urlsplit(href).scheme or href.startswith('//'):
            return m.group(0)
        if href == 'index.html':
            return f'{m.group(1)}#{m.group(3)}'
        return f'{m.group(1)}{urljoin(base_url, href)}{m.group(3)}'

    return re.sub(r'(<a\b[^>]*\bhref=")([^"]+)(")', repl, page)


def build(site_dir: Path) -> dict:
    index = site_dir / 'index.html'
    if not index.exists():
        raise FileNotFoundError('_site/index.html がない。先に scripts/build.py を実行する。')
    site = json.loads((ROOT / 'site.json').read_text(encoding='utf-8'))
    base_url = site.get('url', '')
    if base_url and not base_url.endswith('/'):
        base_url += '/'
    page = index.read_text(encoding='utf-8')
    page, images = inline_images(page, site_dir)
    page = absolutize_links(page, base_url)
    out = site_dir / OUTPUT_NAME
    out.write_text(page, encoding='utf-8')
    return dict(output=str(out.relative_to(ROOT)), images=images, bytes=out.stat().st_size)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, default=ROOT / '_site', help='build.py の出力ディレクトリ')
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.site), ensure_ascii=False, indent=2))
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

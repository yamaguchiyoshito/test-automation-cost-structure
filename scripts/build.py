#!/usr/bin/env python3
"""記事(Markdown)からGitHub Pages用の閲覧サイト(_site/)を生成する。1記事構成で、index.html が記事本体になる。Pandoc 3.x が必要。"""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
READER = 'markdown+tex_math_dollars+footnotes+pipe_tables+autolink_bare_uris'
STATIC_DIRS = ('assets',)


def run_pandoc(text: str, args: list[str]) -> str:
    if not shutil.which('pandoc'):
        raise RuntimeError('Pandoc 3.x が必要である。README.md の「ブラウザで読む」を参照。')
    result = subprocess.run(['pandoc', *args], input=text, text=True, encoding='utf-8', capture_output=True, check=False)
    if result.returncode or result.stderr.strip():
        raise RuntimeError(f'Pandoc conversion failed: {result.stderr.strip()}')
    return result.stdout


def parse_markdown(text: str) -> dict:
    # --columns を十分大きくし、パイプテーブルに区切り行由来の相対列幅(colgroup)を付けさせない。
    return json.loads(run_pandoc(text, ['--from', READER, '--to', 'json', '--columns=10000']))


def map_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme or url.startswith(('#', '//')):
        return url
    path = parsed.path
    if path.endswith('.md'):
        path = path[:-3] + '.html'
        if Path(path).name in ('README.html', 'ARTICLE.html'):
            path = path[:-len(Path(path).name)] + 'index.html'
    return path + ('?' + parsed.query if parsed.query else '') + ('#' + parsed.fragment if parsed.fragment else '')


def transform_links(node: object) -> None:
    if isinstance(node, dict):
        if node.get('t') in ('Link', 'Image'):
            node['c'][-1][0] = map_url(node['c'][-1][0])
        for child in node.values():
            transform_links(child)
    elif isinstance(node, list):
        for child in node:
            transform_links(child)


def wrap_tables(output: str) -> str:
    """<table> を横スクロール用の <div class="table-wrap"> で包む。"""
    output = re.sub(r'<table(\s[^>]*)?>', lambda m: f'<div class="table-wrap"><table{m.group(1) or ""}>', output)
    return output.replace('</table>', '</table></div>')


def render(text: str) -> str:
    ast = parse_markdown(text)
    transform_links(ast)
    output = run_pandoc(json.dumps(ast, ensure_ascii=False), ['--from', 'json', '--to', 'html5', '--mathml', '--wrap=none'])
    return wrap_tables(output)


def headings(body: str) -> list[tuple[str, str]]:
    """本文の h2 から (id, 見出し文字列) を取り出す。目次ドロワーに使う。"""
    out = []
    for ident, inner in re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', body, re.S):
        out.append((ident, html.unescape(re.sub(r'<[^>]+>', '', inner)).strip()))
    return out


def wrap_page(title: str, body: str, site: dict, css: str) -> str:
    links = []
    ref_anchor = ''
    for i, (ident, text) in enumerate(headings(body), 1):
        label = re.sub(r'^\d+\.\s*', '', text)
        if text == '参考資料':
            ref_anchor = ident
            continue
        links.append(f'<a class="chapter-link" href="#{ident}"><span>{i:02d}</span>{html.escape(label)}</a>')
    ref_link = f'<a href="#{ref_anchor}">参考資料</a>' if ref_anchor else ''
    footer_label = f'{html.escape(site.get("date", ""))}時点 / 第{str(site.get("version", "1")).split(".")[0]}版'
    return f'''<!doctype html>
<html lang="{html.escape(site.get("language", "ja"))}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><title>{html.escape(title)}</title>
<style>{css}</style></head><body>
<a class="skip" href="#main">本文へ移動</a>
<input type="checkbox" id="toc-state" class="toc-state" aria-label="目次を開く">
<header class="topbar"><a href="index.html" class="brand">{html.escape(site["title"])}<span>{html.escape(site.get("eyebrow", ""))}</span></a><div class="topbar-actions"><label class="toc-toggle" for="toc-state"><svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 5h14M3 10h14M3 15h14"/></svg>目次</label></div></header>
<label class="toc-backdrop" for="toc-state" aria-hidden="true"></label>
<aside class="toc-drawer" aria-label="記事の目次"><div class="toc-drawer-head"><strong>記事の目次</strong><label class="toc-close" for="toc-state" title="閉じる"><svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 5l10 10M15 5L5 15"/></svg></label></div><nav aria-label="記事の目次">{''.join(links)}</nav><div class="toc-drawer-foot"><p>{html.escape(site.get("tagline", ""))}</p>{ref_link}</div></aside>
<div class="layout"><main id="main" tabindex="-1"><article>{body}</article><footer>{footer_label} — 本文はMarkdown、図はSVG。図の帯や配置は概念的な比率であり、実測値ではない。</footer></main></div></body></html>'''


def build(output: Path) -> dict:
    output = output.resolve()
    if output == ROOT or ROOT.is_relative_to(output):
        raise RuntimeError('出力先にはリポジトリ自身またはその親を指定できない。')
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    site = json.loads((ROOT / 'site.json').read_text(encoding='utf-8'))
    css = (ROOT / 'site-src/styles.css').read_text(encoding='utf-8')
    source = ROOT / site['article']
    text = source.read_text(encoding='utf-8')
    title = re.search(r'^# (.+)', text, re.M).group(1)
    content = render(text)
    (output / 'index.html').write_text(wrap_page(title, content, site, css), encoding='utf-8')
    for name in STATIC_DIRS:
        shutil.copytree(ROOT / name, output / name, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.DS_Store'))
    shutil.copy2(ROOT / 'site.json', output / 'site.json')
    (output / '.nojekyll').write_text('', encoding='utf-8')
    result = dict(pages=1, title=title, sections=len(headings(content)), figures=content.count('<img '),
                  math_nodes=content.count('<math '), svg_files=len(list((output / 'assets').rglob('*.svg'))))
    (output / 'build-report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.output), ensure_ascii=False, indent=2))
        return 0
    except (RuntimeError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

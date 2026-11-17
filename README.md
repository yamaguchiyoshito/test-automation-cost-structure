# 生成と検証から考えるテスト自動化の歴史とコスト構造

**生成のコストが下がった今、検証のボトルネックは「自動化を維持する能力」と「正しさを判断する根拠」へ移っている。**

画面テスト（E2Eテスト）自動化の歴史を、生成と検証、TAS（Test Automation System）とSUT（System Under Test）の区別から読み直し、ノーコード型SaaSとAIエージェント＋Playwrightの総保有コストを比較する1本の記事。2022年にMagicPodによるE2Eテスト自動化を推進した理由と、AIエージェント登場後も同じ選択を推奨する理由を、組織のCI/CD成熟度と案件構成から説明する。

[記事を読む](ARTICLE.md)

本文は `ARTICLE.md` の1記事で、連載形式ではない。図版10点は `assets/` のSVGで、すべて `scripts/draw_figures.py` が生成する。

## ファイル構成

```text
TAS_SUT/
├── README.md                  # リポジトリ案内（本ファイル）
├── ARTICLE.md                 # 記事本文（Markdown）。閲覧サイトでは index.html になる
├── site.json                  # サイト定義（題名、肩書き、要約文、版、日付、記事のパス）
├── assets/                    # 図（SVG、10点）。ファイル名は章番号で始める
├── site-src/styles.css        # 閲覧サイトのスタイル（sier-resource-series と共通）
├── scripts/
│   ├── draw_figures.py        # 全図版を決定論的に生成（Python標準ライブラリのみ）
│   ├── check_figures.py       # SVGの整形性・最小フォント・はみ出し・文字重なりを検査
│   ├── build.py               # ARTICLE.md → _site/（HTML）
│   └── check_html.py          # _site/ のリンク・図版数・alt・スクリプト不在を検査
├── .github/workflows/pages.yml# mainへのpushでビルドしGitHub Pagesへ公開
└── claudedocs/                # 挿絵計画などの作業記録（サイトには載せない）
```

生成物 `_site/` は `.gitignore` で除外する。

## GitHubで読む

`ARTICLE.md` をGitHubのPreviewで開く。図は相対リンク先のSVGとして表示される。閲覧のためにPagesや専用アプリは必要ない。

## ブラウザで読む（ローカル生成）

Python 3.11以降とPandoc 3.xを使う。Python標準ライブラリだけで動き、追加パッケージは不要である。この版はPython 3.13・Pandoc 3.7系で検証した。

```sh
python3 scripts/draw_figures.py    # 図版を再生成（図を変えたとき）
python3 scripts/check_figures.py   # 図版の検査
python3 scripts/build.py
python3 scripts/check_html.py
```

`_site/index.html` をブラウザで開く。目次ドロワー（記事の章見出し）、相対リンクの図をローカルで表示する。

## GitHub Pagesで公開する

1. リポジトリを作成し、この内容を `main` へpushする。
2. Settings → Pages → Build and deployment の Source を **GitHub Actions** にする。
3. `main` へのpush（または Actions の「Build and publish reader」を手動実行）で `_site/` がビルドされ、公開される。URLはActionsの成功したジョブから取得する。

ワークフローはPandoc 3.7.0.2を固定して取得し、`scripts/check_figures.py`、`scripts/build.py`、`scripts/check_html.py` を順に実行してから公開する。検証に失敗した場合は公開しない。Markdown原本・スクリプト・`claudedocs/` はサイトへ配置しない。

## 編集ルール

1. 記事は単独で読めるように結論・前提・用語を記述する。年代は技術・サービスの登場時期を示し、普及完了時期ではない。
2. SVGのファイル名は図を置く章の番号で始める。
3. `assets/` の図はすべて `scripts/draw_figures.py` が生成する。SVGを手で編集せず、スクリプトを直して再生成する。文字は14px以上、注記は16px（本文では720pxに縮小表示される）。
4. 図は定性的な配置と塗り分けで示し、根拠のない数値を描かない。概念的な比率を使う図は、その旨を図中に明記する。
5. 引用・参考資料は記事末尾の「参考資料」で確認する。
6. 題名・日付・版を変えたときは `site.json` と本READMEを更新し、`scripts/build.py` と `scripts/check_html.py` を通す。

# 生成と検証から考えるテスト自動化の歴史とコスト構造

**短期的にはSaaSによって検証効率化の効果を獲得し、中長期的には共通CI/CD基盤と運用能力を整備することが合理的である。**

画面テスト（E2Eテスト）自動化の歴史を、生成と検証、TAS（Test Automation System）とSUT（System Under Test）の区別から読み直し、ノーコード型SaaSとAIエージェント＋Playwrightの総保有コストを比較する1本の記事。2022年にMagicPodによるE2Eテスト自動化を推進した理由と、AIエージェント登場後も同じ選択を推奨する理由を、組織のCI/CD成熟度と案件構成から説明する。

[記事を読む](ARTICLE.md)

本文は `ARTICLE.md` の1記事で、連載形式ではない。図版31点は `assets/` のSVGで、すべて `scripts/draw_figures.py` が生成する。

## ファイル構成

```text
TAS_SUT/
├── README.md                  # リポジトリ案内（本ファイル）
├── ARTICLE.md                 # 記事本文（Markdown）。閲覧サイトでは index.html になる
├── site.json                  # サイト定義（題名、肩書き、版、日付、記事のパス）
├── assets/                    # 図（SVG、31点）。ファイル名は章番号で始める
├── site-src/styles.css        # 閲覧サイトのスタイル（sier-resource-series と共通）
├── site-src/slides.css        # 登壇用スライドのスタイル（配色は図と共通）
├── slides/deck.md             # 登壇用スライドの原稿（1スライド1メッセージ＋トーク原稿）
├── scripts/
│   ├── draw_figures.py        # 全図版を決定論的に生成（Python標準ライブラリのみ）
│   ├── check_figures.py       # SVGの整形性・最小フォント・配色・コントラスト・箱からのはみ出し・文字重なりを検査
│   ├── build.py               # ARTICLE.md → _site/（HTML）
│   ├── build_slides.py        # slides/deck.md → _site/slides/（スライドとトークスクリプト）
│   ├── check_slides.py        # スライド規約（見出し・図・原稿の文字数・時間）を検査
│   └── check_html.py          # _site/ のリンク・図版数・alt・スクリプト不在（スライドのキー操作用を除く）を検査
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
python3 scripts/build_slides.py        # 登壇用スライドとトークスクリプト
python3 scripts/check_slides.py
python3 scripts/check_html.py
```

`_site/index.html` をブラウザで開く。目次ドロワー（記事の章見出し）、相対リンクの図をローカルで表示する。`_site/slides/index.html` がスライド、`_site/slides/script.html` がトークスクリプトである。

## 登壇資料

`slides/deck.md` が唯一の原稿で、`---` 区切りの1ブロックが1スライドである。各ブロックは見出し（`## `、全角28字以内）、章ラベル（`section:`）、図1点（`figure:`、`assets/` のSVGを再利用）または箇条書き3項目以内、メッセージライン（`message:`、1〜2文・64字以内。スライド単体で読んで分かる結論文で、表紙以外は必須）、補足1行（`sub:`、40字以内、任意）、トーク原稿（`notes:`）を持つ。`type: title|section|summary` で表紙・章扉・まとめ、`appendix: true` で予備スライドにする。

スライドは16:9で、矢印キー・PageUp/PageDown・スペース・Home/Endでめくれ（そのための最小限のインラインスクリプトだけを含む。外部通信・ライブラリなし）、印刷すると1スライド1ページになる。ヘッダー（左：章ラベル、右：ページ番号）とフッター（左：短縮題名と日付、右：公開URL）は全スライド共通で、配色は図と同じ役割色を使う。目安時間は原稿の文字数から300字/分で算出し、本編の原稿合計は2,000〜2,400字（300字/分で8分以内）に収める。これらは `scripts/check_slides.py` が機械的に検査する。

## GitHub Pagesで公開する

1. リポジトリを作成し、この内容を `main` へpushする。
2. Settings → Pages → Build and deployment の Source を **GitHub Actions** にする。
3. `main` へのpush（または Actions の「Build and publish reader」を手動実行）で `_site/` がビルドされ、公開される。URLはActionsの成功したジョブから取得する。

ワークフローはPandoc 3.7.0.2を固定して取得し、`scripts/check_figures.py`、`scripts/build.py`、`scripts/build_slides.py`、`scripts/check_slides.py`、`scripts/check_html.py` を順に実行してから公開する。検証に失敗した場合は公開しない。Markdown原本・スクリプト・`claudedocs/` はサイトへ配置しない。

## 編集ルール

1. 記事は単独で読めるように結論・前提・用語を記述する。年代は技術・サービスの登場時期を示し、普及完了時期ではない。
2. SVGのファイル名は図を置く章の番号で始める。
3. `assets/` の図はすべて `scripts/draw_figures.py` が生成する。SVGを手で編集せず、スクリプトを直して再生成する。文字は14px以上、注記は16px（本文では720pxに縮小表示される）。
4. 図は定性的な配置と塗り分けで示し、根拠のない数値を描かない。概念的な比率を使う図は、その旨を図中に明記する。
5. 色は役割で固定する。NEUTRAL（区別しない基本要素・従来・自社負担）、PRIMARY（主題のシステム・領域）、AI（生成AI・エージェントの支援）、POSITIVE（削減・移転・成功）、ATTENTION（残る負担・注意・ボトルネック、1図に1系統）、INK（結論は色ではなく太字）。1図の地の塗りは4種以内、文字と地色のコントラスト比は4.5以上とし、`scripts/check_figures.py` が機械的に検査する。色だけで状態を伝える図には凡例と文字ラベルを併記する。実線は流れ、破線は遷移・方針、2pxの細線は注釈の引き出し線に使う。
6. 図のキャプション（Markdown の alt ＝ SVG の aria-label）は、図の主題を表す名詞句で全角30字以内とし、要素の列挙や「〜を示す図」で終える書き方はしない。図の内容の詳しい説明は SVG 内の `<desc>` に書く。長さは `scripts/check_figures.py` と `scripts/check_html.py` が機械的に検査する。
7. 引用・参考資料は記事末尾の「参考資料」で確認する。
8. 題名・日付・版を変えたときは `site.json` と本READMEを更新し、`scripts/build.py` と `scripts/check_html.py` を通す。

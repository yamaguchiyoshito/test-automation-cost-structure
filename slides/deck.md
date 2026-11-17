## 生成と検証から考えるテスト自動化の歴史とコスト構造
type: title
section: 登壇資料
sub: 2026年11月17日 ／ 登壇8分
notes: 「生成と検証から考えるテスト自動化の歴史とコスト構造」というテーマで、8分お話しします。
---
## 短期はSaaS、中長期は共通CI/CD基盤と運用能力
section: 結論
figure: assets/10d-short-and-long-term.svg
sub: 本日の主張。理由を順に説明します
notes: 先に結論です。短期的にはSaaSで検証効率化の効果を得て、中長期的には共通のCI/CD基盤と運用能力を整える。この二段構えが合理的だ、というのが本日の主張です。理由を、生成と検証、TASとSUTという二つの区別から順に説明します。
---
## 生成は速くなった。検証の速さがボトルネックになる
section: 01 問題
figure: assets/01a-generation-and-verification.svg
notes: 生成AIで、コードもテストも短時間で大量につくれるようになりました。しかし、つくったものが要求を満たすかを確かめる検証は、同じ割合では速くなっていません。生成が速くなるほど、検証の速さが全体のボトルネックになります。
---
## 生成が短くなっても、検証の帯は残る
section: 01 問題
figure: assets/01b-generation-vs-verification.svg
notes: 工程を帯で見るとこうなります。生成の帯が短くなっても、検証の帯はそのまま残る。全体のリードタイムは、検証で決まるようになります。
---
## 動的検証には、整備して維持し続ける要素が多い
section: 01 問題
figure: assets/02b-verification-elements.svg
sub: ここが後半のCI/CDの話につながります
notes: 検証を静的と動的に分けると、整備するものの量が違います。静的検証はルールを整えれば、生成直後に自動で回せます。動的検証は実行環境、テストデータ、操作手順、期待結果、証跡を整え、維持し続けなければなりません。これが後半のCI/CDの話につながります。
---
## 自動化が削減してきたのは実装と実行。判断は残る
section: 01 問題
figure: assets/02c-dynamic-verification-activities.svg
notes: 動的検証を5つの活動に分けると、従来のテスト自動化が削減してきたのは主に実装と実行です。期待結果が正しいか、テストが十分かという判断は、今も残っています。
---
## 画面テスト自動化の7つの転換点
section: 02 歴史
figure: assets/03-gui-test-timeline.svg
sub: 年代は技術・サービスの登場時期です
notes: 画面テスト自動化の歴史を7つの転換点で振り返ります。2004年のSeleniumに始まり、記録再生、クラウド実行環境、ノーコード型SaaS、事例の蓄積、生成AI、そして2025年のAIエージェントです。年代は登場時期です。
---
## テスト自動化はもう一つの保守対象のシステムを生む
section: 03 構造
figure: assets/04b-tas-sut-systems.svg
notes: テスト対象のSUTと、テストを自動実行するTASです。SUTが変わればTASのテストも直す必要があり、TAS自身にもライブラリやブラウザの更新、環境の障害対応が発生します。テスト自動化は、もう一つの保守対象のシステムを生むのです。
---
## 人手の削減は、TASの構築・保守と交換されている
section: 03 構造
figure: assets/04c-exchange-balance.svg
notes: 人手によるテスト実行の削減は、TASを構築し保守する負担と交換されています。自動化の価値は、この交換が経済的に成立するかどうかで決まります。
---
## 動かし続ける仕組みを自社で作る負担はどう減ったか
section: 03 構造
figure: assets/05a-burden-shift-flow.svg
notes: Seleniumの初期は全部自社で用意していました。IDEで作成が楽になり、クラウド実行環境で環境の一部が外に出て、ノーコード型SaaSで作成から実行、証跡、修復までが一体で提供されるようになりました。
---
## SaaSとAI＋Playwrightは下げるコストが違う
section: 03 構造
figure: assets/05b-saas-vs-agent-effects.svg
notes: SaaSは実行環境や定期実行、修復を提供者が担います。AI＋Playwrightは設計やコード生成を支援しますが、実行環境と定期実行は利用者側に残ります。
---
## 機能はSaaS事業者が担う。責任はSIerに残る
section: 03 構造
figure: assets/06-responsibility-boundary.svg
notes: SaaSに移るのは機能と役割です。クラウド実行、スケジュール、証跡、自動修復、利用者サポートはSaaS事業者が担います。仕様の理解、期待結果、テストデータ、十分性の判断、そして検証の責任はSIerに残ります。
---
## AIが下げるのは作成部分。水面下に運用要素が残る
section: 03 構造
figure: assets/07a-iceberg-of-operation.svg
notes: AIエージェントが下げるのはテストコードの生成と修復、水面の上の部分です。水面下にはCI Runner、ブラウザの更新、認証情報、テストデータ、証跡、原因調査、復旧といった運用要素が残ります。設定ファイルを生成すれば終わる仕事ではありません。
---
## AIとテスト環境の接続は、まさにTASの領域
section: 03 構造
figure: assets/07c-ai-test-environment-connection.svg
notes: AIを継続運用に組み込むには、CIとの接続に加えてテスト環境との接続が要ります。打鍵できるブラウザと対象環境、結果を確かめるためのDBやバッチへの接続です。これを作り、維持するのは、まさにTASの領域です。
---
## 2022年の転換：SaaS利用で安定したコスト効果を創出
section: 04 判断
figure: assets/08a-2022-saas-shift.svg
notes: 2022年、テスト自動化SaaSの利用に舵を切りました。案件ごとに環境を作って効果を個別に検証する状態から、SaaSで多様な既存案件に横展開し、安定したコスト効果を得る方向です。
---
## 保守開発の制約が、内部に手を入れる施策を阻む
section: 04 判断
figure: assets/08c-maintenance-constraints.svg
notes: 背景の一つは保守開発の制約です。案件の約8割が保守開発で、内部構造を自由に変えられません。単体テストの強化や依存関係の分離のような、内部に手を入れる施策は適用しにくいのです。
---
## SPAは手前の層を厚くできる。JSPはE2Eになりがち
section: 04 判断
figure: assets/08e-spa-vs-jsp-test-layers.svg
notes: もう一つは画面の実装方式です。SPAならVitest、Storybook、Playwrightで、E2Eより手前の層を厚くできます。JSPは単体で描画できないため、打鍵によるビッグバン型のE2Eになりがちです。だからこそ、E2Eの自動化そのものが方策になります。
---
## 5つの条件が、SaaS型の画面E2E自動化へ収束した
section: 04 判断
figure: assets/08f-2022-decision-context.svg
notes: 先行事例の存在、保守開発が約8割、技術スタックの多様さ、JSP中心の画面実装、CI/CD成熟度の制約。この5つの条件が、SaaS型の画面E2E自動化という判断に収束しました。
---
## 専門家が解決してきたのは、スクリプト作成ではなく安定運用
section: 05 AI時代
figure: assets/09a-expertise-scope.svg
notes: AIエージェントの登場後も、この判断は変わりません。専門家が解決してきたのはスクリプト作成ではなく、安定実行、データ管理、切り分け、変更追従など、動かし続ける技術です。
---
## 自動化の効果には、CI/CDの成熟がセットで要る
section: 05 AI時代
figure: assets/09c-automation-plus-cicd.svg
notes: テスト自動化の効果には、CI/CDの成熟がセットで要ります。共通の実行基盤、標準設定、運用手順、障害対応体制です。これを欠くと、導入と維持は各案件の責任になり、属人化します。
---
## SaaSもAIの恩恵を受ける：MagicPod MCP
section: 05 AI時代
figure: assets/09d-magicpod-with-claude-code.svg
notes: そしてSaaSもAIの恩恵を受けます。MagicPodとClaude Codeを組み合わせ、2026年にはMagicPod MCPによって、画面を見ながらシナリオを作る時間はほぼなくなりました。運用面の優位性を保ったまま、作成と保守も効率化できています。
---
## TASの総コストは、作成費だけではない
section: 06 方針
figure: assets/10a-tco-breakdown.svg
notes: ツール選定は総保有コストで比べます。テストコードの作成費は5区分のうちの1つにすぎません。AIが主に下げるのはそこだけで、実行基盤、修復と保守、定期実行と障害対応、利用料は継続して発生します。
---
## 案件への当てはめ：SPA、JSP、CI/CD未成熟の保守
section: 06 方針
figure: assets/10e-policy-routing.svg
notes: 案件への当てはめです。SPAの案件はE2E以前の確認を広げ、繰り返し回せるCI環境を整える。JSPの案件はSaaSを推奨。CI/CD成熟度が低い保守開発案件はSaaSクラウドを使い、テスト情報をクラウドに載せる顧客許諾がどうしても得られない案件だけ、PlaywrightでTASを構築します。
---
## 短期はSaaS、中長期は共通基盤。責任は常にSIer
type: summary
section: まとめ
- 生成は速くなり、検証がボトルネックになった
- テスト自動化はもう一つの保守対象のシステムを生む
- 短期はSaaS、中長期は共通基盤。責任はSIer
notes: まとめます。生成は速くなり、検証がボトルネックになった。テスト自動化はもう一つの保守対象のシステムを生む。短期はSaaSで効果を得て、中長期は共通基盤と運用能力を整える。そして検証の責任は常にSIerにあります。ありがとうございました。
---
## 静的検証と動的検証の区分
section: 01 問題
appendix: true
figure: assets/02a-static-vs-dynamic.svg
notes: 静的検証は実行を伴わない調査、動的検証は実行による振る舞いの確認です。本日は動的検証、とくに画面テストの自動化を扱いました。
---
## SUTとTASの構成
section: 03 構造
appendix: true
figure: assets/04a-sut-and-tas.svg
notes: SUTは画面、API、業務ロジック、データからなるテスト対象。TASはテストスクリプト、実行制御、結果取得、実行環境とテストデータからなる、テストを自動実行するシステムです。
---
## 時代ごとのTASコスト要素の担い手
section: 03 構造
appendix: true
figure: assets/05c-cost-shift-by-era.svg
notes: 時代ごとに、コスト要素を誰が担ったかの一覧です。期待結果とデータの責任は、どの時代も利用者側に残ります。
---
## 保守開発と新規開発の比率
section: 04 判断
appendix: true
figure: assets/08b-maintenance-share.svg
notes: 案件の約8割が保守開発です。内部構造を変えにくいことが、ホワイトボックス寄りの施策を全社展開しにくい前提になります。
---
## 画面E2Eテストは、SUTの実装技術に依存しにくい
section: 04 判断
appendix: true
figure: assets/08d-stack-agnostic-e2e.svg
notes: 画面E2Eは利用者から見える操作と結果を検証するため、JSP、SPA、レガシーといった実装技術の違いを超えて適用できます。要素特定や非同期処理の個別調整は必要です。
---
## 一度動かす技術と、動かし続ける技術
section: 05 AI時代
appendix: true
figure: assets/09b-run-once-vs-keep-running.svg
notes: 初回成功のあとに、画面変更、ブラウザ更新、データの変化、環境障害が順に起きます。そのたびに切り分けと修正が要る。専門性は動かし続ける側にあります。
---
## パターンA：ノーコード型SaaSが適する条件
section: 06 方針
appendix: true
figure: assets/10b-pattern-saas.svg
notes: CI/CD成熟度が低い、保守開発中心で技術スタックが多様、専門人材が不足、という条件ではノーコード型SaaSが適します。
---
## パターンB：Playwright＋AIが適する条件
section: 06 方針
appendix: true
figure: assets/10c-pattern-playwright.svg
notes: CI/CD基盤が共通化済み、高度な制御が必要、基盤を保守する共通チームが存在、という条件ではPlaywright＋AIエージェントが適します。

# 変更履歴（Changelog）

**ToyoSono フォーク**が [vijaymasand/BKChem_python_3](https://github.com/vijaymasand/BKChem_python_3)（BKChem 0.14.0-pre2 がベース）をフォークした後に行った変更の一覧です。ToyoSono の指示のもと META Muse が実装し、Windows（Python 3.15 / Tk 9）で動作確認しています。

English version: [CHANGELOG.md](CHANGELOG.md)

## フォーク リリース 10 — 2026-11-12

### 追加・変更（Added / Changed）

- **「選択範囲を SVG としてクリップボードへコピー」が Linux と macOS でも画像として貼れるようになりました**: Linux では `xclip`（X11）または `wl-copy`（Wayland、wl-clipboard パッケージ）がインストールされている場合、SVG をそのヘルパーに渡して `image/svg+xml` 形式で提供するため、対応アプリには SVG ソースのテキストではなく画像として貼り付きます。ヘルパーが常駐するので、BKChem を終了しても内容が残ります。macOS では `pyobjc-framework-Cocoa` がインストールされている場合、Windows と同様に `public.svg-image` と `public.utf8-plain-text` の2形式でシステムのペーストボードに登録します。これらのヘルパーが無い場合は従来通り（Tk クリップボード、テキストのみ）です。X11 の経路は検証済みで、Wayland と macOS の経路は同じヘルパーの公開インターフェースに沿っていますが、実機では未検証です。（`bkchem/paper.py`）
- **アプリ本体が使っていないモジュールに、その旨の注記を付けました**: `http_server.py`、`http_server2.py`、`svg_out.py`、`structure_database.py`、`name_database.py` の先頭に、BKChem アプリケーション自体は使っていないことを明記しました。動作に変更はありません。

### 修正（Fixed）

- **oasa のコマンドライン変換ツールが動くようになりました**: `bkchem/oasa/convert.py` が Python 2 の `file()` と `raw_input()` を素通しの `except` の下で使っていたため、ファイルが存在しても「cannot open file ... for reading」という誤ったメッセージで全ての変換が失敗していました（終了コードも 0）。SMILES から MOL、SMILES の往復、MOL から SMILES を確認済みで、ブリリアントブルー（53原子・57結合）でも変換できます。（`bkchem/oasa/convert.py`）
- **oasa の共通モジュールに残っていた Python 2 の比較組み込みを修正しました**: `is_uniquely_sorted()` の既定値が Python 3 で削除された `cmp` で、比較関数を指定せずに呼ぶと `NameError` になりました。アプリ内の呼び出し元（CIP 判定）は常に関数を渡すため、GUI からは到達しません。（`bkchem/oasa/oasa/common.py`）
- **oasa の単体 SVG ライターが動くようになりました**: `svg_out.py` の `mol_to_svg()` が `file()` を使っていて、呼ばれると `NameError` になりました。BKChem 本体の SVG 書き出しは自前の `xml_writer` が担当するため、影響するのはライブラリ関数を直接使う場合だけです。（`bkchem/oasa/oasa/svg_out.py`）
- **oasa の部分構造データの読み取りと生成が動くようになりました**: `subsearch.py` の `file()` 6か所と、生成器が `map` オブジェクトを生成先の `subsearch_data.py` にそのまま書き出してしまう問題を修正しました。読み取り関数はモジュール内で deprecated と明記されているもので、Molecular Descriptors の実働の基検索（生成済みデータを参照）は不変です。（`bkchem/oasa/oasa/subsearch.py`）

## フォーク リリース 9 — 2026-11-10

### 追加・変更（Added / Changed）

- **公開するポータブル版のビルドを GitHub Actions で自動化します**: （`.github/workflows/build-portable.yml`）

### 修正（Fixed）

- **実験的な Web サーバーモジュールの不具合を修正しました**: `http_server.py` と `http_server2.py` の Python 2 のコードを修正し、import とハンドラの動作テストを通過できるようにしました。なお、唯一の呼び出し元である `main.py` の `start_server()` はコメントアウトされています。（`bkchem/http_server.py`、`bkchem/http_server2.py`）
- **BKChem 内のコードで Read SMILES / Read InChI を実行する際のアルゴリズムを変更しました**: BKChem 内部の構造式生成プログラムの仕上げ処理を、実質完全に重なった原子（結合長の 5% 未満）だけを 0.6 結合長まで離すという保守的な方法に変更しました。フィロキシンBのような変形しにくい化合物の変換は良好になった反面、酢酸トコフェロールなど長めの炭素鎖を持つ化合物を変換すると時々絡み合った形状になります。再読み込みも有効ですが、OpenBabel の利用をよりおすすめします。（`bkchem/oasa_bridge.py`）
- **構造データベースのモジュールを修正しました**: これは BKChem のメニューからこのモジュールを呼ぶ場所はなく、import 失敗時に oasa が無言で無効化していたライブラリ機能です。既になくなった外部パッケージ `pysqlite2` を要求していたのを標準ライブラリの `sqlite3` を使うように変更しました。同じファイル内の 3 件（`file()`、gzip のテキストモードでの open、`dict.values()` を sqlite3 に渡す箇所）も直しました。（`bkchem/oasa/oasa/structure_database.py`）
- **InChIKey 生成を修正しました**: `get_sha256()` が `hashlib` に `str` を渡していたため Python 3 では `TypeError` になっていました。UTF-8 のバイト列からダイジェストを計算し latin-1 で戻すことで、従来の `ord()` を使うコードが Python 2 と同じ文字を見るようにしました。エタノール・水・ベンゼン・酢酸・メタンの公式キーと照合し 5/5 が一致しました。外部の InChI プログラムがキーを返さなかったときの代替手段で、`inchi-1.exe` 経由の Generate InChI には影響しません。（`bkchem/oasa/oasa/inchi_key.py`）

## フォーク リリース 8 — 2026-11-09

### 追加・変更（Added / Changed）

- **Chemistry → Read SMILES / Read InChI で OpenBabel が使えるようになりました**: Options → OpenBabel program path で `obabel.exe` / `obabel` を指定すると、両方の読み込みを OpenBabel が担当します（解析と `--gen2d` による 2D 座標生成を行い、MOL 経由で取り込みます）。フロキシンBの比較で、OpenBabel の方が結合長・結合角が均一で見た目がきれいだったことが採用の決め手です。プログラムが存在しない場合や、OpenBabel が読めない入力では無言で従来の oasa 読み込みに戻り、欄を空にすれば完全に元の動作です。検証で見つけた落とし穴: OpenBabel の座標は y 軸が上向きで BKChem のキャンバスは下向きのため、そのまま取り込むとすべての立体中心が反転しました（立体バッテリー 9/48）。CML 取り込みと同じ上下反転を入れて 48/48 に直してあります。副次的な改善として、複数成分（塩）の InChI が読めるようになり（ブリリアントブルー FCF、53 原子)、InChI の立体（/t 層）も描画に反映されます。Windows では OpenBabel 3.1.1（GitHub のインストーラー）で確認済みです。`pip install openbabel` には Python 3.15 用ホイールがないため、インストーラー版を使ってください（README の「SMILES / InChI 読み込みと OpenBabel」参照）。（`bkchem/oasa_bridge.py`、`bkchem/main.py`、`bkchem/interactors.py`）

### 修正（Fixed）

- **混み合った分子が SMILES からときどき大きく歪んで読み込まれる**: 配置の評価が原子同士の距離しか見ていなかったため、腕が中央に覆いかぶさった崩れが見抜けず、候補も 6 個しか作っていなかったため良い配置がそもそも試されない回がありました（ブリリアントブルー FCF は 12 回中 3 回が大きく歪みました）。評価に密集 pair 数・原子と結合の距離・結合の上に乗った原子の数を追加し、候補数を SMILES 6→12、InChI 3→8 に増やしました。修正後はブリリアントブルー FCF の新規 12 回読み込みがすべて交叉なしの整った配置になり、J-GLOBAL 5 化合物とステレオバッテリー 48/48 に悪化はありません。一番きれいな向きが毎回出る保証まではありません。（`bkchem/oasa_bridge.py`）
- **呼び出し元のない旧 API に残っていた Python 3 非互換を修正**: `periodic_table.py` のジェネレータ内の `raise StopIteration`、`graph.py` の同じパターンと `sort()` へのラムダ渡し、`molecule.py` 旧関数の `map(...).sort()` を直しました。いずれも現在の機能からは呼ばれていないコードで、動作への影響はありません。（`bkchem/oasa/oasa/periodic_table.py`、`bkchem/oasa/oasa/graph/graph.py`、`bkchem/oasa/oasa/molecule.py`）

## フォーク リリース 7 — 2026-11-08

### 追加・変更（Added / Changed）

- **Chemistry → Generate InChI が使えるようになりました**: もともと公式 InChI プログラムを外部実行する設計でしたが、Python 3 ではプログラムを正しく設定しても失敗していました（subprocess に文字列のまま渡していたため）。また InChI 1.07 は従来の STDIO オプション形式を受け付けなくなったため、呼び出しを一時ファイル経由に変えました。パスが間違っている場合は「Unknown error」ではなく専用のエラーダイアログが出ます。設定方法: IUPAC-InChI の GitHub リリースから InChI ソフトウェア（v1.07 以降、MIT ライセンス）を入手し、Options → InChI program path で自分の OS 用の `inchi-1.exe` / `inchi-1` を指定してください（README の「Generate InChI について」参照）。InChI 1.07.5 でエタノール、酢酸イオン、L-アラニン（立体化学を含む)、トロキセルチンで確認済みです。（`bkchem/oasa/oasa/inchi.py`）
- **CML インポートの向きが他の形式と揃いました**: CML ファイルは、同じ構造を MOL で読み込んだ場合と上下が鏡像になって描かれていました。BKChem が書き出した CML も他のエディタで開くと反転していました。インポート・エクスポートとも y 座標を対称に反転するよう統一し、CML2 インポーターは Ketcher の `<bondStereo>` 要素を読むようになりました（従来はくさび/ハッシュ結合がすべて無言で落ちていました）。注意: この修正より前に BKChem が書き出した CML ファイルは、今後は反転して読み込まれます。（`bkchem/plugins/CML.py`、`bkchem/plugins/CML2.py`)

### 修正（Fixed）

- **Ketcher の MDL MOL V3000 ファイルが読み込めませんでした**: oasa の molfile リーダーは V2000 しか理解できず、V3000 ファイルを原子 0 個の分子として読み、インポートプラグインがクラッシュしていました。V3000 リーダー（原子/結合ブロック、電荷、結合の立体）を追加し、まったく解析できないファイルはクラッシュではなく通常のインポートエラーになるようにしました。（`bkchem/oasa/oasa/molfile.py`、`bkchem/plugins/molfile.py`)
- **CDXML エクスポートが他のプログラムで全結合と元素情報を失っていました**: 書き出した結合に `id` 属性がなく（ChemSketch は id のないオブジェクトを無言で捨てるため、孤立した原子だけが表示されました)、ヘテロ原子には `Element` 属性がなく、他のプログラムでは全原子が炭素として読まれていました。文書全体で一意な id、`Element` / `NodeType`、明示的な結合次数と電荷を書くようにし、インポーターも `Element` 属性を尊重するようになりました（反転した "HO" 水酸基ラベルがホルミウムとして往復することもなくなります）。（`bkchem/plugins/CDXML.py`)
- **Ketcher の CML インポートが `KeyError: 'name'` でクラッシュしました**: インポーターは古い CML1 形式の子要素しか読めず、Ketcher の書く CML2 属性形式に対応していませんでした。さらに、通常なら丁寧にエラーになるはずの経路自体が存在しないフィールドを参照して壊れており、CML の cis/trans 立体表記は未知の結合タイプになって描画で落ちていました。3点とも直し、くさび/ハッシュの立体も保持されます。（`bkchem/plugins/CML.py`)
- **oasa の CIP 優先順位コードが Python 3 で死んでいました**（組み込み `cmp` など削除された記法のため）: 優先順位の計算が再び動くようになりました。例: FC(Cl)(Br)I はキラルと判定され、優先順位は I > Br > Cl > F です。BKChem の機能からはまだ呼ばれていませんが、Python 3 対応の一環として直しました。（`bkchem/oasa/oasa/atom.py`)
- **環状 SMILES の書き出し**: oasa の `is_pure_ring()` が `filter()` オブジェクトとリストを比較していたため、Python 3 では常に「純粋な環ではない」という答えになっていました。（`bkchem/oasa/oasa/smiles.py`)
- **無言で誤動作する Python 3 の名残が2件**: 外部データモジュールの型チェックが常に合格になっていて（`filter()` オブジェクトは常に真）、不正な値が無言で通っていました。また oasa の misc モジュール内の未使用ヘルパー3件が、呼ばれると NameError / TypeError になる状態でした。（`bkchem/external_data.py`、`bkchem/oasa/oasa/misc.py`)

## フォーク リリース 6 — 2026-11-07

### 修正（Fixed）

- **Chemistry → Read InChI が電荷のある分子にも対応**: 酢酸イオン・ギ酸イオン・水酸化物イオンは誤ったイオン（電荷 +1、水素1個多い）として描かれていました（符号が途中で落ちていたため）。メチルアンモニウムはクラッシュし、硫黄を含む分子は中性でもクラッシュしていました。厳密な照合36件中34件が合格。残る制限: ジボランと水素化ホウ素は oasa の価数モデルの限界できれいに失敗します。硝酸イオンも oasa の電荷配置の都合で今も読めません。ステレオ（/t 層）は描画に未反映で、塩のような複数成分の InChI は未対応です。（`bkchem/oasa/oasa/inchi.py`）
- **SMILES / InChI 読み込みで大きな分子が重なって融合して見える**: oasa の座標生成は衝突を全く見ていなかったため、ビタミンK・トロキセルチン・α-トコフェロールアセタートでは別の原子の真上（距離 0.0）に着地していました。生成器自体を衝突回避付きにし、複数案から最もきれいな配置を選ぶようにしたので、5化合物×両経路とも重なり・結合の交叉は 0 件になりました。ストレプトマイシンの InChI は別の原因（整数除算の名残）でも失敗していましたが、そちらも直り 40 原子で読めます。残る制限: α-トコフェロールアセタートとトロキセルチンは、当たりの悪い配置で交叉が 1〜2 件残ることがあります。ブリリアントブルー FCF の InChI（複数成分の塩）は oasa の未対応のままです。（`bkchem/oasa/oasa/coords_generator.py`、`bkchem/oasa_bridge.py`、`bkchem/oasa/oasa/misc.py`）
- **官能基の置換で置き換えた基が隣の構造に重なる**: トロキセルチンの水酸基をフェニル基に置換すると、フェニル基の炭素が隣の環の原子に 0.53（結合長比）まで接近していました。置換直後に、深刻な接近（0.6 未満）がある場合だけ置き換えた基を剛体回転させて空いた方向へ逃がすようにしました。ご提示の例では 0.53 → 0.61 になり、深刻な接近はなくなりました。ただし回転だけではこれ以上は離れず、まだ窮屈なままです（手本のように分子全体の向きを変える配置は、局所的な回転では得られません）。接近がない置換は従来と全く同じ配置のままです。（`bkchem/group.py`）
- **Molfile の書き出しで "M  END" の前に空行が入る**: すべての .mol ファイルに、プロパティ行の位置に余分な空行が入っていました（Python 3 の `filter()` は常に真になるため、行がない場合でも1行書き出していました）。読み込み側は無視するのでデータは壊れませんが、形式どおりではありませんでした。（`bkchem/oasa/oasa/molfile.py`）

## フォーク リリース 5 — 2026-11-06

### 追加・変更（Added / Changed）

- **SMILES の立体化学（キラル）に対応**: Chemistry → Read SMILES が `@` / `@@` を読み取り、キラル中心をウェッジ（手前）／ハッシュ（奥）結合で描くようになりました。環の中心では環の外に出る結合を優先してウェッジを付けるので、環は平面のまま表示されます。逆向きも対応し、Chemistry → Generate SMILES は描かれたウェッジ／ハッシュから `@` / `@@` を出力します（oasa が保持していた立体情報を、橋渡しコードが捨てていたのが原因でした）。既知の制限: α-Thujone のような縮環系では、oasa の SMILES 書き出し側の既存の問題により、Generate SMILES の結果が鏡像になる場合があります。（`bkchem/oasa_bridge.py`）

### 修正（Fixed）

- **キラル中心と二重結合を持つ分子で Generate SMILES が落ちる**: Pyrethrin II などで `TypeError: unhashable type: 'explicit_hydrogen'` が出ていました。`__eq__` だけを定義したクラスが Python 3 でハッシュ化できないためです。（`bkchem/oasa/oasa/stereochemistry.py`）
- **ラジカルを含む分子の Molfile 書き出しで落ちる**: ラジカルの原子番号一覧の並べ替えが Python 2 の書き方のままでした。通常の分子の書き出しには影響ありません。（`bkchem/oasa/oasa/molfile.py`）
- **Chemistry → Read InChI が中性分子でも失敗する**: 変換ループの成功条件が Python 3 では常に成り立たない書き方になっており、「Localization of bonds, charges or movable hydrogens failed」で終わっていました。中性・ステレオ指定なしの分子が取り込めるようになりました（電荷のある InChI は別の原因で未対応）。（`bkchem/oasa/oasa/inchi.py`）
- **Read SMILES で原子1個だけの文字列が落ちる**: `C` や `O` のように結合のない分子でゼロ除算になっていました。（`bkchem/oasa_bridge.py`）

## フォーク リリース 4 — 2026-11-05

### 修正（Fixed）

- **Molecular Descriptors で「Group:」の項目がすべて欠落していた**（水酸基・ベンゼン・カルボキシ基など）: 同梱の oasa 部分構造検索の中に Python 3 で壊れている箇所が5つあり、失敗が握りつぶされていたため、CSV に Group の列が出てきませんでした。あわせて、部分構造検索が座標を持たないテンプレート原子に描画用のプロパティを設定して落ちる問題（BKChem 側の原子クラス）も直しました。（`bkchem/oasa/oasa/common.py`、`bkchem/oasa/oasa/molecule.py`、`bkchem/atom.py`）
- **実際のアプリケーションが書き出した CDXML の読み込みが失敗する**（ChemSketch の書き出しファイルで確認）: フォントサイズが小数で書かれている（例: `size="10.5"`）とエラーになる、「OH」のような通常の水素付きラベルで原子コード内の Python 3 残り（`dict_keys`）により落ちる、取り込み中の再描画でまだ描画されていない原子が落ちる、電荷のマイナスが長いダッシュ（ChemSketch の「O–」）で書かれていると電荷付き酸素ではなくただのテキストとして取り込まれる、の4点を直しました。（`bkchem/plugins/CDXML.py`、`bkchem/atom.py`）

## フォーク リリース 3 — 2026-11-04

### 修正（Fixed）

- **CDXML（ChemDraw XML）の読み込みが失敗する**: 色テーブル付きファイルで色の読み取り時にエラーになり、ページ内テキスト・「+」記号・矢印を含むファイルも読み込めず、何も取り込まれませんでした。あわせて4か所を修正しました。（`bkchem/plugins/CDXML.py`）
- **ポータブル版で Import メニューが空で、Export が SVG だけだった**: 読み書きプラグインは名前で動的に読み込まれる仕組みのため、PyInstaller の解析から外れて exe に入っていませんでした。ビルド設定（spec）にプラグインを明示するよう直しました。（`bkchem.spec`）

## フォーク リリース 2 — 2026-11-03

### 修正（Fixed）

- **図形を含むファイルが開けない**: 四角形・正方形・楕円・円を含む保存ファイルが、"object of type 'map' has no len()" エラーで読み込めませんでした。（`graphics.py`）
- **設定ダイアログで現在のフォントが表示されない**: Object → Configure（右クリックの Properties）の Font タブで、使用中のフォント名が常に空白でした。対象を持たない選択でもタブが出てしまう問題もあわせて直しました。（`dialogs.py`）

## フォーク リリース 1 — 2026-11-02

### 修正（Fixed）

- **設定が再起動で消える**: メニュー言語とウィンドウサイズが毎回初期値に戻っていました。設定ファイルの読み書きを直し、起動時に読み込んだ設定が破棄されないようにしました。（`pref_manager.py`、`main.py`）
- **Tk 9 ＋ 日本語メニューで起動時にクラッシュ**: 日本語ラベルのように英数字を含まないメニューでは Pmw のホットキー処理が Tk 9 で落ちました。BKChem 側でホットキーなしのメニューバーを使うようにしました。（`main.py`）
- **Group substitution で実際には結合していないのに結合して見える**: 原子の価数に収まらない基（例: 環の炭素に CHO）を置くと、見た目だけ結合した表示になり、内部データと食い違って Undo が失敗したり基が画面に残ったりしました。そのような置換は「Can not replace」エラーで拒否し、何も変更しないようにしました。あわせて Undo 自体も修正しました（Python 3.11 で削除された `inspect.getargspec` を使用していたため）。（`context_menu.py`、`undo.py`、`group.py`、`export.py`、`marks.py`、`main.py`）
- **Options → Standard ダイアログが使えない**: 開く途中でクラッシュし（Python 3 の dict ビューのソート）、Save ボタンも常に失敗していた（Python 2 の `file()`）ため、個人用標準値が保存されませんでした。両方とも修正しました。（`dialogs.py`、`paper.py`）
- **マウスホイールのズームで途中で落ちる**: 拡大後のフォントサイズが調整テーブルにない場合にエラーになり、文字サイズがばらばらになっていました。（`tuning.py`）
- **環の炭素に COOH / COOCH3 が付いてしまう**: 式パーサーが基を勝手に変形して無理に当てはめていました。占有価数 2 以上の原子への基の置換を拒否し、パーサー自体も高価数で変形した解釈を成功させないよう堅牢化しました。（`group.py`、`oasa/oasa/linear_formula.py`）
- **原子記号の変更で価数を超えてしまう**: 例えば環の炭素を酸素に変えると結合3本の酸素ができていました。有効な価数が存在しない変更は拒否するようになりました（オキソニウム O+ やアンモニウム N+ のような電荷付きの正当なケースは許可）。クエリ原子へのフォールバック経路も塞ぎました。（`atom.py`、`queryatom.py`）
- **ODF / OpenOffice Draw エクスポートが失敗**: "object of type 'map' has no len()" エラーが出ていました。（`plugins/odf.py`、`plugins/openoffice.py`）
- **Align → Center horizontally / Center vertically が失敗**: "module 'operator' has no attribute 'div'" エラーが出ていました。（`paper.py`）
- **Chemistry → Check chemistry が常に「OK」と表示**: 分子の検証が実際には実行されていませんでした（Python 3 で消費されない `map()` 呼び出し）。正しく所見を表示するようになりました。あわせて、翻訳ファイルのない環境で同じダイアログとテンプレート保存が落ちる問題（`ngettext` 未定義）も修正しました。（`validator.py`、`interactors.py`）
- **＋記号が削除できない**、削除したオブジェクトが内部スタックに残ることがある、Fragment overview のオレンジ色ハイライトが画面から消えない、といった問題を修正しました。（`paper.py`、`dialogs.py`）
- **3D 回転で装飾の残像が残る**: ハッシュ結合・破線・点線の装飾が、回転前の姿のまま描画を閉じるまで残っていました。（`bond.py`）

### 追加・変更（Added / Changed）

- **「Selected to clipboard as SVG」で画像としても登録**: SVG のソースを文字列としてのみ登録していました。Windows では `image/svg+xml` 形式の画像としてもクリップボードに登録するようにしたので、Word に「画像 (SVG)」としてベクター図で貼れるようになりました。（`paper.py`）
- **ファイルダイアログが前回のフォルダを記憶**: 開く / 保存 / インポート / エクスポート（および Molecular Descriptors / Fingerprints のファイル選択）が毎回 `C:\Windows\System32` から開いていました。再起動をまたいでも前回使ったフォルダで開くようになりました。（`main.py`、`descriptor_dialog.py`、`fingerprint_dialog.py`）
- **About ダイアログ**: Help → About の末尾にこのフォークのクレジットを追加しました。（`messages.py`）
- **Windows ポータブル版のビルド対応**: 起動用 `run_bkchem.py` と PyInstaller 用 `bkchem.spec` を追加し、フォルダ形式のポータブル実行ファイルを作れるようにしました（素朴なビルドでは Pmw の中で無言で失敗していました）。手順は README_JP.md を見てください。

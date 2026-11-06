# 変更履歴（Changelog）

**ToyoSono フォーク**が [vijaymasand/BKChem_python_3](https://github.com/vijaymasand/BKChem_python_3)（BKChem 0.14.0-pre2 がベース）をフォークした後に行った変更の一覧です。ToyoSono の指示のもと META Muse が実装し、Windows（Python 3.15 / Tk 9）で動作確認しています。

English version: [CHANGELOG.md](CHANGELOG.md)

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

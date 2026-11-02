# 変更履歴（Changelog）

**ToyoSono フォーク**が [vijaymasand/BKChem_python_3](https://github.com/vijaymasand/BKChem_python_3)（BKChem 0.14.0-pre2 がベース）をフォークした後に行った変更の一覧です。ToyoSono の指示のもと META Muse が実装し、Windows（Python 3.15 / Tk 9）で動作確認しています。

English version: [CHANGELOG.md](CHANGELOG.md)

## フォーク リリース 1 — 2026-11-02

### 修正（Fixed）

- **設定が再起動で消える**: メニュー言語とウィンドウサイズが毎回初期値に戻っていました。設定ファイルの読み書きを直し、起動時に読み込んだ設定が破棄されないようにしました。（`pref_manager.py`、`main.py`）
- **Tk 9 ＋ 日本語メニューで起動時にクラッシュ**: 日本語ラベルのように英数字を含まないメニューでは Pmw のホットキー処理が Tk 9 で落ちました。BKChem 側でホットキーなしのメニューバーを使うようにしました。（`main.py`）
- **「Selected to clipboard as SVG」がテキストとして貼り付く**: MS Word に SVG のソースが文字列として貼られていました。Windows では `image/svg+xml` 形式の画像としてもクリップボードに登録するようにし、Word に「画像 (SVG)」としてベクター図で貼れるようになりました。（`paper.py`）
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

- **ファイルダイアログが前回のフォルダを記憶**: 開く / 保存 / インポート / エクスポート（および Molecular Descriptors / Fingerprints のファイル選択）が毎回 `C:\Windows\System32` から開いていました。再起動をまたいでも前回使ったフォルダで開くようになりました。（`main.py`、`descriptor_dialog.py`、`fingerprint_dialog.py`）
- **About ダイアログ**: Help → About の末尾にこのフォークのクレジットを追加しました。（`messages.py`）
- **Windows ポータブル版のビルド対応**: 起動用 `run_bkchem.py` と PyInstaller 用 `bkchem.spec` を追加し、フォルダ形式のポータブル実行ファイルを作れるようにしました（素朴なビルドでは Pmw の中で無言で失敗していました）。手順は README_JP.md を見てください。

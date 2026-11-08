# BKChem（Python 3 対応版）

**BKChem** はフリー（オープンソース）の 2D 分子描画プログラムです。もともと Beda Kosata によって開発され、長年にわたりオープンソースのケムインフォマティクス界で使われてきました。

このリポジトリは [vijaymasand/BKChem_python_3](https://github.com/vijaymasand/BKChem_python_3) の **ToyoSono によるフォーク**です。元リポジトリには **Python 3.10+** に対応し、現代の OS で安定動作するよう近代化された BKChem が収められており、このフォークはその上に一連のバグ修正と小さな機能追加を重ねたものです（ToyoSono の指示のもと META Muse が実装）。内容は下の「このフォークでの変更点」を見てください。

[English README](README.md) / [英語の変更履歴](CHANGELOG.md)

## Windows 版のダウンロード

Windows ユーザーは Python をインストールする必要はありません。[Releases ページ](https://github.com/ToyoSono/BKChem_python_3/releases)から **`BKChem-portable.zip`** をダウンロードし、任意の場所に展開して、中の **`BKChem.exe`** を実行してください。

- `BKChem.exe` は隣の `_internal` フォルダと一緒でないと起動しません。離さないでください。
- 実行ファイルにはコード署名がないため、初回起動時に Windows SmartScreen の警告が出ることがあります。「詳細情報」→「実行」の順にクリックすると起動できます。

## 主な機能

- **直感的な描画**: 結合・原子・複雑な分子構造を簡単に作成できます。
- **豊富なエクスポート形式**:
    - **ベクター**: SVG、PDF（Cairo / Piddle 経由）、PostScript、EPS
    - **ドキュメント**: OpenOffice / LibreOffice Draw（ODF）、LaTeX
    - **画像**: PNG（Cairo 経由）
- **化学的な整合性**: 原子の性質・同位体・構造検証を正しく扱います。
- **拡張性**: テンプレートとユーザー定義フラグメントのライブラリに対応します。
- **プラグインシステム**: エクスポーター / インポーターを拡張できます。

## このフォークでの変更点

フォーク後に行った修正・変更の概要です。

- **設定が保存されるようになりました**: メニュー言語、ウィンドウサイズ、Options → Standard の値が再起動後も残ります。Tk 9 ＋ 日本語メニューでの起動時クラッシュも直しました。
- **SVG コピーが画像として貼れるようになりました**: 「Selected to clipboard as SVG」は本物の `image/svg+xml` 画像をクリップボードに入れるようになり、MS Word などに SVG ソースの文字列ではなく、拡大縮小できるベクター図として貼れます。
- **不可能な置換を拒否します**: 原子の価数を超える基の置換や原子記号の変更（例: 環の炭素に COOH を付ける）は、実際には無い結合を表示する代わりに「Can not replace」メッセージで拒否します。Undo も確実に動くよう直しました。
- **壊れていた機能の修復**: ODF / OpenOffice Draw エクスポート、Align → Center（水平・垂直）、Chemistry → Check chemistry（以前は無言で常に「OK」でした）、＋記号の削除、Fragment overview のハイライト、マウスホイールズーム、3D 回転後の結合装飾の残像、など。
- **ファイルダイアログが前回のフォルダを記憶**: 開く / 保存 / インポート / エクスポートのダイアログが、毎回 `C:\Windows\System32` からではなく前回使ったフォルダで開くようになりました。
- **ポータブル版ビルド対応**: `run_bkchem.py` と `bkchem.spec` を同梱し、PyInstaller でポータブルな Windows 実行ファイルを作れるようにしました（手順は下記）。
- **Generate InChI が使えるようになりました**: Chemistry → Generate InChI で、選択した構造式の InChI と InChIKey（立体化学を含む）を生成できます。公式 InChI プログラムを使うため、初回のみ設定が必要です（下記の「Generate InChI について」参照）。

詳細は `CHANGELOG_JP.md` を見てください。（English: `CHANGELOG.md`）

なお、元リポジトリ側の近代化作業については [vijaymasand/BKChem_python_3](https://github.com/vijaymasand/BKChem_python_3) の履歴を見てください。

## Generate InChI について

Chemistry → Generate InChI は公式の InChI プログラムを外部実行する機能で、BKChem 本体には同梱されていません。[IUPAC-InChI の GitHub リリース](https://github.com/IUPAC-InChI/InChI/releases/latest)から InChI ソフトウェア（v1.07 以降、MIT ライセンス）をダウンロードしてください。`release_artifacts.zip` の中に `inchi-1.exe`（Windows)、`inchi-1`（Linux)、`inchi-1`（macOS）が入っています。自分の OS 用のプログラムを取り出し、BKChem の Options → InChI program path でそのファイルを指定すれば、構造式を選択したときに Generate InChI が使えるようになります。

## 動作要件

ソースから実行する場合に必要です（上のポータブル実行ファイルには不要）。Python 3.10 以上と以下のライブラリが必要です。

- **Tkinter**: （通常 Python に付属）
- **Pmw**（Python MegaWidgets）: `pip install Pmw`
- **Pillow**（PIL フォーク）: `pip install Pillow`
- **PyCairo**（任意、Cairo 系エクスポート用）: `pip install pycairo`
- **pyWin32**（win32clipboard.py 用、Windows のみ）: `pip install pywin32`
- **PyInstaller**（ポータブル実行ファイルを作る場合のみ）: `pip install PyInstaller`

## クイックスタート

1. **リポジトリを clone する**:
   ```bash
   git clone https://github.com/ToyoSono/BKChem_python_3
   cd BKChem_python_3
   ```

2. **依存ライブラリを入れる**:
   ```bash
   pip install Pmw Pillow pycairo pywin32
   ```

3. **BKChem を起動する**:
   ```bash
   python start_bkchem.py
   ```

## ポータブル Windows 実行ファイルの作り方

クイックスタートの 1〜2 の後に続けます。

4. **PyInstaller を入れる**:
   ```bash
   pip install PyInstaller
   ```

5. **`build` フォルダと `dist` フォルダがあれば削除する**（前回ビルドの残りです）。

6. **実行ファイルをビルドする**:
   ```bash
   python -m PyInstaller --noconfirm bkchem.spec
   ```
   補足: `bkchem.spec` は開発中は起動エラーが見えるようコンソール付き（`console=True`）になっています。公開用ビルドでは、先に `bkchem.spec` の `console=False` に変えてください。

7. 成果物は **`dist\BKChem`** フォルダにできます（`BKChem.exe` と `_internal` フォルダ）。この2つは常に一緒に扱ってください。配布する場合は `dist\BKChem` フォルダ全体を zip（`BKChem-portable.zip`）にして、GitHub の Release に添付します。

## サポート・コントリビューション

この近代化版 BKChem が役に立ったら、ぜひ:
- 🌟 GitHub で **Star** を付けてください（他の人が見つけやすくなります）。

## ドキュメント

詳しいドキュメント（古いものも含む）は `doc/` ディレクトリにあります。バッチモード、カスタムプラグイン、テンプレートのガイドなどです。

## ライセンス

BKChem は **GNU General Public License (GPL)** で公開されています。詳しくは `bkchem/import_checker.py` または元のプロジェクトのドキュメントを見てください。

---
*近代化とメンテナンス: Dr. Vijay Masand（インド・アムラバティ）、Gaurav Masand（インド・アムラバティ）、Krish Masand（インド・アムラバティ）*

*デバッグと修正: ToyoSono（日本）の指示のもと META Muse が実施*

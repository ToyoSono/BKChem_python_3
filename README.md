# BKChem (Python 3 Modernized)

**BKChem** is a free (open source) 2D molecular drawing program. It was originally developed by Beda Kosata and has been a staple in the open-source chemical informatics community for years.

This repository is **ToyoSono's fork** of [vijaymasand/BKChem_python_3](https://github.com/vijaymasand/BKChem_python_3), which contains a modernized version of BKChem, fully ported to **Python 3.10+** and stabilized for modern operating systems. The fork adds a series of bug fixes and small features on top of it, developed under ToyoSono's direction by META Muse. See [What Changed in This Fork](#what-changed-in-this-fork) below.

[日本語版 README はこちら](README_JP.md) / [日本語の変更履歴](CHANGELOG_JP.md)

## Download for Windows

Windows users do **not** need to install Python. Download **`BKChem-portable.zip`** from the [Releases page](https://github.com/ToyoSono/BKChem_python_3/releases), unzip it anywhere, and run **`BKChem.exe`** inside the unzipped folder.

- Keep `BKChem.exe` together with the `_internal` folder next to it — the program will not start without it.
- The executable is not code-signed, so Windows SmartScreen may show a warning on first run. Click "More info" and then "Run anyway" to start it.

## Key Features

- **Intuitive Drawing**: Easy creation of bonds, atoms, and complex molecular structures.
- **Rich Export Formats**:
    - **Vector**: SVG, PDF (via Cairo and Piddle), PostScript, EPS.
    - **Document**: OpenOffice/LibreOffice Draw (ODF), LaTeX.
    - **Image**: PNG (via Cairo).
- **Chemical Intelligence**: Correct handling of atom properties, isotopes, and structure validation.
- **Scalability**: Support for templates and user-defined fragment libraries.
- **Plugin System**: Extensible architecture for custom exporters and importers.

## What Changed in This Fork

Highlights of the fixes and changes made after forking:

- **Settings now persist**: the menu language, window size, and values set in Options → Standard survive a restart. A startup crash on Tk 9 with Japanese menus is also fixed.
- **Copy as SVG pastes as a picture**: "Selected to clipboard as SVG" now puts a real `image/svg+xml` image on the clipboard, so MS Word and similar applications paste a scalable vector figure instead of SVG source text.
- **Impossible replacements are refused**: group substitution and atom-symbol changes that would exceed an atom's valency (for example putting COOH on a ring carbon) are now refused with a "Can not replace" message instead of showing a bond that is not really there. Undo also works reliably again.
- **Broken features repaired**: ODF / OpenOffice Draw export, Align → Center horizontally/vertically, Chemistry → Check chemistry (it silently always reported "OK" before), deletion of plus signs, Fragment overview highlights, mouse-wheel zoom, and leftover bond decorations after 3D rotation.
- **File dialogs remember the last folder**: Open / Save / Import / Export dialogs reopen in the folder you used last time instead of always starting in `C:\Windows\System32`.
- **Portable build support**: `run_bkchem.py` and `bkchem.spec` are included so a portable Windows executable can be built with PyInstaller (see below).
- **Generate InChI works again**: Chemistry → Generate InChI produces the InChI and InChIKey for the selected structure (including stereochemistry), using the official InChI program — see [Generate InChI](#generate-inchi) below for the one-time setup.

For details, see `CHANGELOG.md`. (日本語版は `CHANGELOG_JP.md`)

The upstream version's own modernization work is described in the git history of [vijaymasand/BKChem_python_3](https://github.com/vijaymasand/BKChem_python_3).

## Generate InChI

Chemistry → Generate InChI uses the official InChI program, which is not bundled with BKChem. Download the InChI software (v1.07 or later, MIT license) from the [IUPAC-InChI GitHub releases](https://github.com/IUPAC-InChI/InChI/releases/latest): the `release_artifacts.zip` contains `inchi-1.exe` (Windows), `inchi-1` (Linux) and `inchi-1` (macOS). Extract the program for your OS, then in BKChem choose Options → InChI program path and select it. After that, Generate InChI becomes available whenever a structure is selected.

## Requirements

To run BKChem from source (for the portable executable above, none of this is needed), you need Python 3.10 or higher and the following libraries:

- **Tkinter**: (usually comes with Python)
- **Pmw** (Python MegaWidgets): `pip install Pmw`
- **Pillow** (PIL Fork): `pip install Pillow`
- **PyCairo** (Optional, for Cairo-based exports): `pip install pycairo`
- **pyWin32** (to use win32clipboard.py, Windows only): `pip install pywin32`
- **PyInstaller** (only if you want to build the portable executable): `pip install PyInstaller`

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ToyoSono/BKChem_python_3
   cd BKChem_python_3
   ```

2. **Install dependencies**:
   ```bash
   pip install Pmw Pillow pycairo pywin32
   ```

3. **Launch BKChem**:
   ```bash
   python start_bkchem.py
   ```

## Building the Portable Windows Executable

After steps 1–2 of Quick Start:

4. **Install PyInstaller**:
   ```bash
   pip install PyInstaller
   ```

5. **Remove the `build` and `dist` folders if they exist** (leftovers from a previous build).

6. **Build the executable**:
   ```bash
   python -m PyInstaller --noconfirm bkchem.spec
   ```
   Note: `bkchem.spec` builds with a console window (`console=True`) so that startup errors stay visible while developing. For a release build, set `console=False` in `bkchem.spec` first.

7. The result is in the **`dist\BKChem`** folder: `BKChem.exe` together with an `_internal` folder. Both must stay together — to distribute it, zip the whole `dist\BKChem` folder (as `BKChem-portable.zip`) and attach the zip to a GitHub Release.

## Support & Contribution

If you find this modernized version of BKChem helpful, please consider:
- 🌟 **Giving it a Star** on GitHub to help others find it.

## Documentation

Detailed documentation (though some of it legacy) can be found in the `doc/` directory, including guides on batch mode, custom plugins, and templates.

## License

BKChem is released under the **GNU General Public License (GPL)**. See the `bkchem/import_checker.py` or the original project documentation for more licensing details.

---
*Modernization and maintenance by Dr. Vijay Masand (Amravati, India), Gaurav Masand (Amravati, India), and Krish Masand (Amravati, India)*

*Debugged and modified by META Muse based on instructions of ToyoSono (Japan)*

<a href="https://alternativeto.net/software/bkchem-python-3-fork/about/?utm_source=badge&utm_medium=referral" target="_blank"><img src="https://alternativeto.net/static/badges/badge-compact-color.svg" alt="BKChem (Python 3 fork) | AlternativeTo" width="244" height="79" style="width: 244px; height: 79px;" /></a>
# BKChem (Python 3 Modernized)

**BKChem** is a free (open source) 2D molecular drawing program. It was originally developed by Beda Kosata and has been a staple in the open-source chemical informatics community for years.

This repository is **ToyoSono's fork** of [vijaymasand/BKChem_python_3](https://github.com/vijaymasand/BKChem_python_3), which contains a modernized version of BKChem, fully ported to **Python 3.10+** and stabilized for modern operating systems. The fork adds a series of bug fixes and small features on top of it, developed under ToyoSono's direction by META Muse. See [What Changed in This Fork](#what-changed-in-this-fork) below.

[日本語版 README はこちら](README_JP.md) / [日本語の変更履歴](CHANGELOG_JP.md)

## Portable Version

A portable version that requires **no** Python installation is provided. Please refer to the table below, then go to the [Releases page](https://github.com/ToyoSono/BKChem_python_3/releases) to download the archive file corresponding to the OS you want to install it on. After extracting the file, launch the executable file (**`BKChem`** or **`BKChem.exe`**) that appears.

| OS | Archive File Name | Notes |
|---|---|---|
| Windows (amd64) | **`BKChem-portable.zip`** | ToyoSono has verified that it launches and performs import/export operations on his own machine. Since the file is not digitally signed, a Windows SmartScreen warning may appear upon first launch. Click “More info” → “Run anyway” to launch the program.|
| Windows (amd64) | **`BKChem-portable-w-ob-inchi.zip`** |This archive includes the Windows version mentioned above, along with OpenBabel 3.1.1 and inchi-1.exe. Please place the executable file and the three folders in the same location while using them.|
| Linux |  **`BKChem-portable-linux.tar.gz`** | Built on Ubuntu 22.04; running it on later versions of the OS is recommended. If you are using an X11 environment, please install xclip; if you are using a Wayland environment, please install wl-clipboard. Operation on actual hardware has not been verified.|
| macOS (Arm version) | **`BKChem-portable-macos.tar.gz`** | Operation on physical devices has not been verified. Since the file is unsigned, you’ll need to right-click and select “Open” the first time you run it.|

Important Note (Applies to All Operating Systems): The executable file will not run unless it is located in the same directory as the adjacent `_internal` folder. Please do not move it.


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
- **Copy as SVG pastes as a picture**: "Selected to clipboard as SVG" puts a real `image/svg+xml` image on the clipboard, so MS Word and similar applications paste a scalable vector figure instead of SVG source text. The same works on Linux when the `xclip` (X11) or `wl-clipboard` (Wayland) helper is installed, and on macOS when `pyobjc-framework-Cocoa` is installed; without them, the SVG source is copied as text, as before.
- **Impossible replacements are refused**: group substitution and atom-symbol changes that would exceed an atom's valency (for example putting COOH on a ring carbon) are now refused with a "Can not replace" message instead of showing a bond that is not really there. Undo also works reliably again.
- **Broken features repaired**: ODF / OpenOffice Draw export, Align → Center horizontally/vertically, Chemistry → Check chemistry (it silently always reported "OK" before), deletion of plus signs, Fragment overview highlights, mouse-wheel zoom, and leftover bond decorations after 3D rotation.
- **File dialogs remember the last folder**: Open / Save / Import / Export dialogs reopen in the folder you used last time instead of always starting in `C:\Windows\System32`.
- **Portable build support**: `run_bkchem.py` and `bkchem.spec` are included so a portable executable can be built with PyInstaller (see below).
- **Generate InChI works again**: Chemistry → Generate InChI produces the InChI and InChIKey for the selected structure (including stereochemistry), using the official InChI program — see [Generate InChI](#generate-inchi) below for the one-time setup.

- **Read SMILES / Read InChI can use OpenBabel**: with Options → OpenBabel program path set to `obabel.exe` / `obabel`, both readers are handled by OpenBabel (parsing plus 2D coordinates), which generally draws more regular layouts. Without the setting, or if OpenBabel fails, BKChem falls back to its own reader — see [OpenBabel for reading SMILES and InChI](#openbabel-for-reading-smiles-and-inchi) below for the one-time setup.

- **The built-in SMILES / InChI reader keeps the generator's layout**: when BKChem's own reader is used, the drawing now keeps the coordinates exactly as the generator produced them; only atoms that land on top of each other are separated. (Details in the CHANGELOG.)

For details, see `CHANGELOG.md`. (日本語版は `CHANGELOG_JP.md`)

The upstream version's own modernization work is described in the git history of [vijaymasand/BKChem_python_3](https://github.com/vijaymasand/BKChem_python_3).

## Generate InChI

Chemistry → Generate InChI uses the official InChI program, which is not bundled with BKChem. Download the InChI software (v1.07 or later, MIT license) from the [IUPAC-InChI GitHub releases](https://github.com/IUPAC-InChI/InChI/releases/latest): the `release_artifacts.zip` contains `inchi-1.exe` (Windows), `inchi-1` (Linux) and `inchi-1` (macOS). Extract the program for your OS, then in BKChem choose Options → InChI program path and select it. After that, Generate InChI becomes available whenever a structure is selected.


## OpenBabel for reading SMILES and InChI

Chemistry → Read SMILES / Read InChI converts the entered string into a structure with BKChem's built-in reader. For structurally complex compounds, however, the resulting drawing can be strongly distorted, or the built-in reader may not be able to handle the input at all. If you run into trouble reading a compound from SMILES or InChI, linking BKChem with OpenBabel — a structure-file format converter — is recommended. In the `BKChem-portable-w-ob-inchi.zip` archive, the program is already included, so no setup is needed.

First, install OpenBabel. On Windows, download OpenBabel 3.1.1 from the [OpenBabel GitHub releases](https://github.com/openbabel/openbabel/releases/tag/openbabel-3-1-1) (`OpenBabel-3.1.1-x64.exe`, 38.7 MB) and install it. On other operating systems, install OpenBabel by the method appropriate for that OS.

Then, in BKChem, choose Options → OpenBabel program path and select the executable — on Windows, `C:\Program Files\OpenBabel-3.1.1\obabel.exe`. After that, SMILES / InChI are read through OpenBabel (parsing plus 2D coordinate generation via `--gen2d`). If the program is missing, the field is empty, or OpenBabel cannot read an input, BKChem silently falls back to its own reader.

Note: `pip install openbabel` does not work on Python 3.15 (the package provides wheels only up to Python 3.14). Unless you specifically need the OpenBabel Python package, installing the standalone program is recommended.

## Requirements

To run BKChem from source (for the portable executable above, none of this is needed), you need Python 3.10 or higher and the following libraries:

- **Tkinter**: (usually comes with Python)
- **Pmw** (Python MegaWidgets): `pip install Pmw`
- **Pillow** (PIL Fork): `pip install Pillow`
- **PyCairo** (Optional, for Cairo-based exports): `pip install pycairo`
- **pyWin32** (for the win32clipboard module, Windows only): `pip install pywin32`
- **xclip / wl-clipboard** (Linux only, optional; lets "Selected to clipboard as SVG" paste as a picture): `sudo apt install xclip` / `sudo apt install wl-clipboard`
- **PyObjC** (macOS only, optional; same purpose on macOS): `pip install pyobjc-framework-Cocoa`
- **PyInstaller** (only if you want to build the portable executable): `pip install PyInstaller`

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ToyoSono/BKChem_python_3
   cd BKChem_python_3
   ```

2. **Install dependencies**:
   ```bash
   pip install Pmw Pillow pycairo
   ```
   On Windows, also install pywin32:
   ```bash
   pip install pywin32
   ```
   On macOS, also install pyobjc-framework-Cocoa:
   ```bash
   pip install pyobjc-framework-Cocoa
   ```

   Note: On Linux, if you want to copy SVG through the clipboard, install xclip (X11) or wl-clipboard (Wayland) with your package manager.

3. **Launch BKChem**:
   ```bash
   python start_bkchem.py
   ```

## Building the Portable Executable

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
   Note: `bkchem.spec` is published on GitHub with `console=False` (no console window). If you need a console, change that line to `console=True` before building.

7. The output files are located in the **`dist\BKChem`** folder (the `BKChem` or `BKChem.exe` file and the `_internal` folder). Please always treat these two together.

   Note: We have started distributing portable versions of BKChem for Windows, Linux, and macOS via GitHub Releases.



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

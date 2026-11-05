# Changelog

Changes made in **ToyoSono's fork** after forking [vijaymasand/BKChem_python_3](https://github.com/vijaymasand/BKChem_python_3) (based on BKChem 0.14.0-pre2). Developed under ToyoSono's direction by META Muse, and verified on Windows (Python 3.15 / Tk 9).

日本語版は [CHANGELOG_JP.md](CHANGELOG_JP.md) を見てください。

## Fork release 4 — 2026-11-05

### Fixed

- **Molecular Descriptors silently omitted all "Group:" counts** (hydroxy group, benzene, carboxyl group, ...): five Python 3 breakages inside the bundled oasa substructure search made it fail, and the failure was swallowed, so the Group rows simply never appeared in the CSV. A sixth issue in BKChem's own atom class (the substructure search setting a drawing property on template atoms that have no coordinates) is fixed as well. (`bkchem/oasa/oasa/common.py`, `bkchem/oasa/oasa/molecule.py`, `bkchem/atom.py`)
- **CDXML import failed on files written by real applications** (verified with a ChemSketch export): font sizes written as fractions (e.g. `size="10.5"`) raised an error; ordinary hydrogenated labels such as "OH" crashed in the atom code (a Python 3 `dict_keys` leftover); a redraw during import crashed for atoms not yet on the paper; and a charge written with a typographic minus (en-dash, as ChemSketch writes "O–") was imported as a plain text label instead of a charged oxygen atom. (`bkchem/plugins/CDXML.py`, `bkchem/atom.py`)

## Fork release 3 — 2026-11-04

### Fixed

- **CDXML (ChemDraw XML) import failed**: files with a colour table raised an error while reading the colours, and files containing page text, plus symbols or arrows failed as well, so nothing was imported. All four spots are fixed. (`bkchem/plugins/CDXML.py`)
- **Portable build: Import menu was empty and Export showed only SVG**: the import/export plugins are loaded dynamically by name, so PyInstaller's static analysis did not include them in the executable. The build spec now lists the plugin modules explicitly. (`bkchem.spec`)

## Fork release 2 — 2026-11-03

### Fixed

- **Files containing shapes could not be reopened**: a saved file containing a rectangle, square, oval or circle failed to load with "object of type 'map' has no len()". (`graphics.py`)
- **Configure dialog did not show the current font**: in Object → Configure (right-click Properties), the Font tab's family chooser never showed the text's actual font family, and tabs could also appear for selections that have no such objects. (`dialogs.py`)

## Fork release 1 — 2026-11-02

### Fixed

- **Preferences were lost on restart**: the menu language and window size reverted every time. Loading/saving of the preference file was repaired, and the loaded preferences are no longer discarded at startup. (`pref_manager.py`, `main.py`)
- **Startup crash on Tk 9 with Japanese menus**: Pmw's menu hotkey handling crashed on Tk 9 when menu labels contain no alphanumeric characters (as in Japanese). BKChem now builds its menu bar without hotkeys. (`main.py`)
- **"Selected to clipboard as SVG" pasted as text**: MS Word received the SVG source as text. On Windows the selection is now also registered as an `image/svg+xml` clipboard image, so Word pastes a scalable vector figure ("画像 (SVG)"). (`paper.py`)
- **Group substitution showed bonds that were not really there**: replacing an atom with a group that cannot fit its valency (e.g. CHO on a ring carbon) displayed a bonded group while the internal data disagreed, and undo then failed or left the group on screen. Such replacements are now refused with a "Can not replace" error and nothing is changed; undo was also repaired (`inspect.getargspec` was removed in Python 3.11). (`context_menu.py`, `undo.py`, `group.py`, `export.py`, `marks.py`, `main.py`)
- **Options → Standard dialog did not work**: it crashed while opening (sorting a Python 3 dict view), and its Save button always failed (Python 2 `file()`), so personal standard values never persisted. Both are fixed. (`dialogs.py`, `paper.py`)
- **Mouse-wheel zoom crashed partway** when a scaled font size was missing from the tuning table, leaving text sizes inconsistent. (`tuning.py`)
- **COOH / COOCH3 could be attached to ring carbons** because the formula parser silently distorted the group to fit. Group substitution now refuses groups on atoms with occupied valency ≥ 2, and the parser itself was hardened to reject distorted parses at higher valencies. (`group.py`, `oasa/oasa/linear_formula.py`)
- **Atom symbols could exceed valency**: e.g. changing a ring carbon to oxygen produced an oxygen with three bonds. Symbol changes are now refused when no valid valency fits (charged species such as oxonium O+ and ammonium N+ remain allowed), including the query-atom fallback path. (`atom.py`, `queryatom.py`)
- **ODF and OpenOffice Draw export failed** with "object of type 'map' has no len()". (`plugins/odf.py`, `plugins/openoffice.py`)
- **Align → Center horizontally / Center vertically failed** with "module 'operator' has no attribute 'div'". (`paper.py`)
- **Chemistry → Check chemistry always reported "OK"**: the molecule validation never actually ran (unconsumed Python 3 `map()` calls). It now reports real findings. A follow-up crash (`ngettext` not defined on systems without a translation file) in the same dialog and in template saving was fixed as well. (`validator.py`, `interactors.py`)
- **Plus signs could not be deleted**, and deleted objects could linger in the internal stack; the Fragment overview's orange highlight marks were never removed from the canvas. (`paper.py`, `dialogs.py`)
- **3D rotation left ghost decorations**: hashed / dashed / dotted bond decorations from before a 3D rotation stayed on screen until the drawing was closed. (`bond.py`)

### Added / Changed

- **File dialogs remember the last used folder**: Open / Save / Import / Export (and the Molecular Descriptors / Fingerprints file pickers) used to always start in `C:\Windows\System32`. They now reopen in the last used folder, also across restarts. (`main.py`, `descriptor_dialog.py`, `fingerprint_dialog.py`)
- **About dialog**: added a credit line for this fork at the end of Help → About. (`messages.py`)
- **Portable Windows build**: added `run_bkchem.py` (entry point) and `bkchem.spec` (PyInstaller spec) so a one-folder portable executable can be built; a naive PyInstaller build silently failed inside Pmw before. See README.md for the build steps.

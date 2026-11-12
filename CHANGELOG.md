# Changelog

Changes made in **ToyoSono's fork** after forking [vijaymasand/BKChem_python_3](https://github.com/vijaymasand/BKChem_python_3) (based on BKChem 0.14.0-pre2). Developed under ToyoSono's direction by META Muse, and verified on Windows (Python 3.15 / Tk 9).

日本語版は [CHANGELOG_JP.md](CHANGELOG_JP.md) を見てください。

## Fork release 10 — 2026-11-12

### Added / Changed

- **"Copy selection as SVG to clipboard" now pastes as a picture on Linux and macOS too**: On Linux, when `xclip` (X11) or `wl-copy` (Wayland, from the wl-clipboard package) is installed, the SVG is handed to that helper and offered as `image/svg+xml`, so SVG-aware applications paste a picture instead of the SVG source text; the helper stays resident, so the content also survives BKChem exiting. On macOS, when `pyobjc-framework-Cocoa` is installed, the SVG is placed on the system pasteboard as both `public.svg-image` and `public.utf8-plain-text`, like the Windows path. Without these helpers the previous behaviour (Tk clipboard, text only) is unchanged. The X11 path is verified; the Wayland and macOS paths follow the documented interfaces of the same helpers but have not been verified on real machines yet. (`bkchem/paper.py`)
- **Modules that the application does not use are now marked as such**: `http_server.py`, `http_server2.py`, `svg_out.py`, `structure_database.py` and `name_database.py` carry a note at the top stating that the BKChem application itself does not use them, so readers no longer have to guess whether a feature exists. No behaviour change.

### Fixed

- **The oasa command-line converter works again**: `bkchem/oasa/convert.py` used the Python 2 builtins `file()` and `raw_input()` under bare `except` clauses, so every conversion failed with the misleading message "cannot open file ... for reading" (and exit code 0) even when the file existed. Verified: SMILES to MOL, SMILES round-trip and MOL to SMILES, including Brilliant Blue FCF (53 atoms, 57 bonds). (`bkchem/oasa/convert.py`)
- **A Python 2 comparison builtin left in oasa's common module is fixed**: `is_uniquely_sorted()` fell back to `cmp`, which Python 3 removed, so calling it without a sorting function raised `NameError`. The in-application callers (the CIP code) always pass a sorting function, so this was not reachable from the GUI. (`bkchem/oasa/oasa/common.py`)
- **oasa's standalone SVG writer works again**: `mol_to_svg()` in `svg_out.py` used `file()` and raised `NameError` whenever it was called. The BKChem application itself writes SVG through its own `xml_writer`, so this affected only direct users of the library function. (`bkchem/oasa/oasa/svg_out.py`)
- **oasa's subsearch data readers and generator work again**: `subsearch.py` used `file()` in six places, and its data generator wrote raw `map` objects into the generated `subsearch_data.py`; both are fixed. The readers are marked deprecated in the module itself, and the live group search in Molecular Descriptors, which reads the already-generated data, is unchanged. (`bkchem/oasa/oasa/subsearch.py`)

## Fork release 9 — 2026-11-10

### Added / Changed

- **The build of the portable releases is automated by GitHub Actions**: (`.github/workflows/build-portable.yml`)

### Fixed

- **The bugs in the experimental web server module are fixed**: The Python 2 code in `http_server.py` and `http_server2.py` was fixed so that they would pass the import and handler functionality tests. Note that the `start_server()` function in `main.py`—the only file that calls these scripts—has been commented out. (`bkchem/http_server.py`, `bkchem/http_server2.py`)
- **The final processing for Read SMILES / Read InChI is modified**: The final processing of the structural formula generation program within BKChem is modified to use a more conservative approach: only atoms that are virtually completely overlapping (less than 5% of the bond length) are separated to 0.6 bond lengths. While the conversion of compounds that are resistant to deformation, such as Phloxine B, has improved, compounds with longer carbon chains, such as α-Tocopherol acetate, sometimes result in entangled structures when converted. In such cases, reloading helps. However, using OpenBabel is recommended instead. (`bkchem/oasa_bridge.py`)
- **Structure database module is fixed**: This is a library feature that oasa silently disabled when the import failed, as there was no place in the BKChem menu to call this module. The now-deprecated external package `pysqlite2` has been replaced by the standard library’s `sqlite3`. Three instances within the same file (`file()`, opening a file in gzip text mode, and passing `dict.values()` to `sqlite3`) are also fixed. (`bkchem/oasa/oasa/structure_database.py`)
- **InChIKey generation is fixed**: `get_sha256()` passed a `str` to `hashlib`, which raises `TypeError` on Python 3, so the whole `inchi_key` module was unusable and oasa silently disabled it. The digest is now computed from UTF-8 bytes and decoded back with latin-1, so the existing `ord()`-based code sees the same characters as on Python 2. Verified against official keys for ethanol, water, benzene, acetic acid and methane (5/5 match). This is only the fallback used when the external InChI program returns no key — Generate InChI via `inchi-1.exe` is unaffected. (`bkchem/oasa/oasa/inchi_key.py`)

## Fork release 8 — 2026-11-09

### Added / Changed

- **Chemistry → Read SMILES and Read InChI can now use OpenBabel**: a new Options → OpenBabel program path setting points BKChem at `obabel.exe` / `obabel`; when set, both readers are handled by OpenBabel (parsing plus 2D coordinates via `--gen2d`, imported as MOL), which generally draws more regular layouts — ToyoSono's decision after comparing Phloxine B, where OpenBabel's bond lengths and angles were visibly more uniform. If the program is missing or cannot read an input, BKChem silently falls back to its own oasa reader, and leaving the path empty restores the previous behaviour exactly. One subtlety found in verification: OpenBabel's coordinates are y-up while BKChem's canvas is y-down, so the import flips y — without it every stereocentre inverted (9/48 on the stereo battery; 48/48 with the flip). Bonus on the OpenBabel path: multi-component (salt) InChI now loads (Brilliant Blue FCF, 53 atoms) and InChI stereo (/t) layers are drawn. Verified on Windows with OpenBabel 3.1.1 from the GitHub installer — the `pip install openbabel` package has no Python 3.15 wheel, so the installer, not pip, is the way to get `obabel.exe` (see "OpenBabel for reading SMILES and InChI" in the README). (`bkchem/oasa_bridge.py`, `bkchem/main.py`, `bkchem/interactors.py`)

### Fixed

- **Crowded molecules sometimes loaded badly distorted from SMILES**: the layout score only measured atom–atom distances, so a layout with an arm draped over the middle could score well while looking collapsed, and with only 6 candidates a good layout often was not even tried (Brilliant Blue FCF came out badly distorted in 3 of 12 loads). The score now also counts crowded pairs, atom-to-bond distances and atoms lying on bonds, and the candidate count rose from 6 to 12 (SMILES) and 3 to 8 (InChI). After the fix, 12 fresh loads of Brilliant Blue FCF were all clean; the five J-GLOBAL compounds and the 48/48 stereo battery are unchanged. The single cleanest orientation is still not guaranteed every time. (`bkchem/oasa_bridge.py`)
- **Python 3 incompatibilities left in unused legacy APIs fixed**: a `raise StopIteration` inside a generator in `periodic_table.py`, the same pattern plus a lambda passed to `sort()` in `graph.py`, and a `map(...).sort()` in a superseded function in `molecule.py`. None of these are called by any current feature, so there is no behavioural change. (`bkchem/oasa/oasa/periodic_table.py`, `bkchem/oasa/oasa/graph/graph.py`, `bkchem/oasa/oasa/molecule.py`)

## Fork release 7 — 2026-11-08

### Added / Changed

- **Chemistry → Generate InChI works again**: it always relied on the official InChI program, but on Python 3 it failed even with the program installed (the subprocess call passed text where bytes are required), and InChI 1.07 no longer accepts the legacy STDIO option dialect — the program is now called through temporary files, and a wrong program path shows the dedicated error dialog instead of "Unknown error". Setup: download the InChI software (v1.07 or later, MIT license) from the IUPAC-InChI GitHub releases and point Options → InChI program path at `inchi-1.exe` / `inchi-1` for your OS (see "Generate InChI" in the README). Verified against InChI 1.07.5 with ethanol, acetate, L-alanine (including its stereochemistry) and troxerutin. (`bkchem/oasa/oasa/inchi.py`)
- **CML import orientation now matches the other formats**: a CML file was drawn vertically mirrored compared with the same structure imported as MOL, and CML files BKChem exported opened mirrored in other editors. Import and export now flip the y coordinates symmetrically, and the CML2 importer reads Ketcher's `<bondStereo>` elements instead of silently dropping all wedge/hash bonds. Note: CML files exported by BKChem before this fix will now import mirrored. (`bkchem/plugins/CML.py`, `bkchem/plugins/CML2.py`)

### Fixed

- **Ketcher's MDL MOL V3000 files could not be imported**: oasa's molfile reader only understood V2000 and read a V3000 file as an empty molecule, which then crashed the import plugin. A V3000 reader (atom/bond blocks, charges, bond stereo) was added, and a file the reader cannot parse at all now gets the normal import error instead of a crash. (`bkchem/oasa/oasa/molfile.py`, `bkchem/plugins/molfile.py`)
- **CDXML export lost all bonds and element identity in other programs**: exported bonds carried no `id` attribute (ChemSketch silently drops id-less objects, so only isolated atoms appeared) and heteroatoms had no `Element` attribute, so other programs read every atom as carbon. The exporter now writes document-wide ids, `Element` / `NodeType`, explicit bond orders and charges; the importer also honours the `Element` attribute, so a flipped "HO" hydroxyl label no longer round-trips as holmium. (`bkchem/plugins/CDXML.py`)
- **Ketcher CML import crashed with `KeyError: 'name'`**: the importer only read old CML1-style child elements while Ketcher writes CML2 attributes; the graceful error path itself referenced a nonexistent field; and CML cis/trans bond stereo became unknown bond types that crashed drawing. All three are fixed, and wedge/hash stereo is preserved. (`bkchem/plugins/CML.py`)
- **oasa's CIP priority code was dead on Python 3** (built-in `cmp` and other removed idioms): the priority machinery works again — e.g. FC(Cl)(Br)I is recognised as chiral with priorities I > Br > Cl > F. No BKChem feature calls it yet; fixed as part of the Python 3 sweep. (`bkchem/oasa/oasa/atom.py`)
- **Ring SMILES writing**: oasa's `is_pure_ring()` compared a `filter()` object with a list, so on Python 3 it always answered "not a pure ring". (`bkchem/oasa/oasa/smiles.py`)
- **Two silent Python 3 leftovers**: a type check in the external-data module always passed (`filter()` objects are always truthy), so invalid values were accepted silently; and three dead helper functions in oasa's misc module raised NameError / TypeError if ever called. (`bkchem/external_data.py`, `bkchem/oasa/oasa/misc.py`)

## Fork release 6 — 2026-11-07

### Fixed

- **Chemistry → Read InChI now handles charged molecules**: acetate, formate and hydroxide used to be drawn as the wrong ion (charge +1 with one extra hydrogen — the sign was lost); methylammonium crashed; sulfur-containing molecules crashed even when neutral. 34 of 36 strict checks pass. Remaining limits: diborane and borohydride still fail cleanly (oasa valency model), nitrate still fails with the Localization error (oasa charge allocation), stereo (/t) layers are not yet reflected in the drawing, and multi-component (salt) InChI is still unsupported. (`bkchem/oasa/oasa/inchi.py`)
- **Large molecules drawn from SMILES / InChI overlapped and looked fused**: oasa's coordinate generator never checked for collisions, so in vitamin K, troxerutin and α-tocopherol acetate whole chain segments landed exactly on top of other atoms (distance 0.0). The generator itself is now collision-aware and the cleanest of several candidate layouts is chosen, so all five test compounds on both routes now have 0 overlaps and 0 bond crossings. Streptomycin's InChI also failed for a separate reason (an integer-division leftover) and now reads (40 atoms). Remaining limits: α-tocopherol acetate and troxerutin can still have 1–2 crossings on unlucky layouts; Brilliant Blue FCF's InChI (a multi-component salt) is still unsupported by oasa. (`bkchem/oasa/oasa/coords_generator.py`, `bkchem/oasa_bridge.py`, `bkchem/oasa/oasa/misc.py`)
- **Group substitution could place the new group on top of a neighbouring structure**: replacing a troxerutin hydroxy group with phenyl left a phenyl carbon 0.53 bond lengths from an atom of the neighbouring ring. After expansion, when a severe approach (below 0.6) exists, the new fragment is now rotated rigidly to a freer direction. In the reported example this moves 0.53 → 0.61, so the severe approach is gone — but it stays snug, because rotation alone cannot do better (a layout that reorients the whole molecule, as in the reference drawing, is beyond a local rotation). Substitutions without a clash are left exactly as before. (`bkchem/group.py`)
- **Molfile export wrote a blank line before "M  END"**: every exported .mol file contained a stray empty line in the property block (a Python 3 `filter()` object is always truthy, so the "no property lines" case still wrote a line). Readers tolerate it, so no data was lost, but the file was not what the format specifies. (`bkchem/oasa/oasa/molfile.py`)

## Fork release 5 — 2026-11-06

### Added / Changed

- **SMILES stereochemistry (chirality) support**: Chemistry → Read SMILES now reads `@` / `@@` and draws each tetrahedral centre with a wedge (forward) or hash (back) bond; for ring centres the wedge is placed on a bond pointing out of the ring, so rings stay flat. The reverse direction works too: Chemistry → Generate SMILES emits `@` / `@@` from drawn wedge/hash bonds (the oasa parser kept the stereochemistry, but the bridge code dropped it). Known limitation: for fused-ring systems such as α-Thujone, Generate SMILES can return the mirror image because of a pre-existing problem in oasa's SMILES writer. (`bkchem/oasa_bridge.py`)

### Fixed

- **Generate SMILES crashed on molecules with both a stereocentre and a double bond** (e.g. Pyrethrin II) with `TypeError: unhashable type: 'explicit_hydrogen'`: the class defines `__eq__` without `__hash__`, which Python 3 makes unhashable. (`bkchem/oasa/oasa/stereochemistry.py`)
- **Molfile export crashed for molecules containing a radical**: the radical atom numbers were still sorted with a Python 2 idiom. Export of ordinary molecules was unaffected. (`bkchem/oasa/oasa/molfile.py`)
- **Chemistry → Read InChI failed even for neutral molecules**: the conversion loop's success condition could never become true on Python 3, so it always ended with "Localization of bonds, charges or movable hydrogens failed". Neutral molecules without stereochemistry now import (charged InChI still fails for a separate reason). (`bkchem/oasa/oasa/inchi.py`)
- **Read SMILES crashed on a single-atom string** such as `C` or `O` (division by zero when a molecule has no bonds). (`bkchem/oasa_bridge.py`)

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

- **"Selected to clipboard as SVG" now also registers an image**: the SVG source used to be registered only as text. On Windows it is now also registered on the clipboard as an `image/svg+xml` image, so Word pastes it as a scalable vector figure ("画像 (SVG)"). (`paper.py`)
- **File dialogs remember the last used folder**: Open / Save / Import / Export (and the Molecular Descriptors / Fingerprints file pickers) used to always start in `C:\Windows\System32`. They now reopen in the last used folder, also across restarts. (`main.py`, `descriptor_dialog.py`, `fingerprint_dialog.py`)
- **About dialog**: added a credit line for this fork at the end of Help → About. (`messages.py`)
- **Portable Windows build**: added `run_bkchem.py` (entry point) and `bkchem.spec` (PyInstaller spec) so a one-folder portable executable can be built; a naive PyInstaller build silently failed inside Pmw before. See README.md for the build steps.

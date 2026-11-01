#!/usr/bin/env python3
"""Entry point for BKChem - for plain Python and for PyInstaller builds.

Why not freeze start_bkchem.py or bkchem/bkchem.py directly?

* bkchem/bkchem.py puts the splash screen, myapp.initialize() and
  myapp.deiconify() inside ``if __name__ == '__main__':`` - that block
  only runs when bkchem.py itself is the main script.  Frozen as an
  entry point (or imported), the module takes its ``else`` branch:
  the application is created and initialized, but nobody runs the
  Tk main loop there.
* start_bkchem.py does call Store.app.mainloop(), but a PyInstaller
  build made from it *without the data files* (pixmaps, templates,
  locale, plugins - see bkchem.spec) dies during startup, and with
  --windowed the traceback is invisible, so it looks like "the exe
  starts and nothing happens".

This launcher keeps the one flow that works in both worlds:
import bkchem.bkchem (which creates, initializes and shows the app
through its import branch) and then run the main loop.
"""

import os
import sys


if __name__ == '__main__':
    # When frozen with PyInstaller, data files are extracted to
    # sys._MEIPASS and the bkchem package resolves its resources
    # (pixmaps, templates, ../images, ../plugins, ../locale) relative
    # to its own __file__, which PyInstaller points into that same
    # extraction directory - so no path patching is needed as long as
    # the .spec file ships those directories, as bkchem.spec does.
    import bkchem.bkchem  # noqa: F401  (importing creates the app)
    from bkchem.singleton_store import Store
    Store.app.mainloop()

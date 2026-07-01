"""
interfaceextension — thin TD wrapper over the standalone `theme` API.

All tokens live in `theme.py` (pure Python, no TD deps). This extension
just exposes them on the component and adds TD-only conveniences:
font-path resolution, a dependable Revision, and Table-DAT export.

    parent.interface.Colors['topbar_bg'].r
    parent.interface.Col('cyan').rgba
    parent.interface.Fonts['mono']          # resolved absolute path

Help: search "Extensions" in wiki
"""

import TDFunctions as TDF

import theme


class interfaceextension:
    """Design-token provider for the NABATELE winch-control UI."""

    # Re-export the token tables verbatim.
    Colors   = theme.COLORS
    Type     = theme.TYPE
    Tracking = theme.TRACKING
    Metrics  = theme.METRICS
    Radii    = theme.RADII
    Icons    = theme.ICONS

    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self._active_tab = tdu.Dependency('Preview')
        # Bump to force token-watching ops to refresh (e.g. on theme edit).
        TDF.createProperty(self, 'Revision', value=1, dependable=True,
                           readOnly=False)

    # ---- TD-only conveniences ---------------------------------------- #
    @property
    def Fonts(self):
        """Font map with the mono path resolved against project.folder."""
        f = dict(theme.FONTS)
        f['mono'] = f'{project.folder}/{f["mono"]}'
        return f

    def Col(self, name):
        """Color instance by role, with a helpful error on a bad key."""
        return theme.col(name)

    def ToTable(self, dat):
        """Dump the palette into a Table DAT: name | hex | r | g | b | a."""
        dat.clear()
        dat.appendRow(['name', 'hex', 'r', 'g', 'b', 'a'])
        for row in theme.palette_rows():
            dat.appendRow(row)
        return dat
    
    @property
    def ActiveTab(self):
        return self._active_tab.val
    
    @ActiveTab.setter
    def ActiveTab(self, value):
        self._active_tab.val = value
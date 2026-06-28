"""
output_table_callbacks — List COMP callbacks for the Output tab.

Renders the 12-winch table from the inputdata extension, themed entirely
from `theme` tokens (no hard-coded colours). Layout per data row:

    col 0  idx        "01"          right-aligned, faint
    col 1  label      "A" / "NE"    EDITABLE  (1 click)  -> SetLabel
    col 2  kind       MAIN / SIDE   pill
    col 3  ip         10.0.1.11     EDITABLE  (1 click)  -> SetIP
    col 4  channels   "1-6"         dim
    col 5  bound      * bound       green dot + text

Section header rows ("MAIN TETHERS ..." / "SIDE TETHERS ...") are injected
between groups and span the whole width.

Wiring (set these as the DAT's first lines or via custom pars):
    IN   = op.NABATELE.op('inputdata')      # inputdataextension host
    THEME = op.NABATELE.op('interface')     # interfaceextension host
Adjust the two paths below to your network.
"""

# --- network references ------------------------------------------------ #
IN = parent.nabatele.InputData       # the comp hosting inputdataextension
THEME = parent.interface     # the comp hosting interfaceextension

NUM_COLS = 6
COL = dict(idx=0, label=1, kind=2, ip=3, channels=4, bound=5)

# Column widths (px). label / ip stretch a touch; the rest are fixed.
COL_W = {0: 44, 1: 96, 2: 62, 3: 168, 4: 70, 5: 96}

ROW_H = 48
HEADER_H = 30


# --- token helpers ----------------------------------------------------- #
def _c(name):
    """theme Color -> rgba tuple."""
    return THEME.Colors[name].rgba


def _t(name):
    return THEME.Type[name]


# --- row model: interleave section headers with winch rows ------------- #
def _layout():
    """Return a flat list describing every visual row.

    Each entry is one of:
        ('header', text)
        ('winch',  data_index, row_dict)
    """
    rows = IN.Rows()
    out = []
    seen_main = seen_side = False
    for di, r in enumerate(rows):
        if r['is_main'] and not seen_main:
            out.append(('header', 'MAIN TETHERS \u00b7 PONTOON'))
            seen_main = True
        if (not r['is_main']) and not seen_side:
            out.append(('header', 'SIDE TETHERS \u00b7 COMPASS SPLAY'))
            seen_side = True
        out.append(('winch', di, r))
    return out


def _store():
    """Cache the layout on the comp for this build pass."""
    L = _layout()
    me.parent().store('_outlayout', L)
    return L


def _get_layout():
    L = me.parent().fetch('_outlayout', None)
    return L if L is not None else _store()


# --- table shape ------------------------------------------------------- #
def onInitTable(comp, attribs):
    L = _store()
    comp.par.rows = len(L)
    comp.par.cols = NUM_COLS
    attribs.bgColor = _c('bg')
    return


def onInitCol(comp, col, attribs):
    attribs.colWidth = COL_W.get(col, 100)
    attribs.colStretch = (col in (COL['ip'],))   # ip column eats slack
    return


def onInitRow(comp, row, attribs):
    L = _get_layout()
    if row >= len(L):
        return
    kind = L[row][0]
    if kind == 'header':
        attribs.rowHeight = HEADER_H
    else:
        attribs.rowHeight = ROW_H
    return


# --- cell painting ----------------------------------------------------- #
def onInitCell(comp, row, col, attribs):
    L = _get_layout()
    if row >= len(L):
        return
    entry = L[row]

    # Defaults shared by every cell.
    attribs.bgColor = _c('bg')
    attribs.fontFace = 'mono'
    attribs.fontFile = THEME.Fonts['mono']
    attribs.fontSizeX = _t('table_cell')
    attribs.textColor = _c('ink')
    attribs.editable = 0
    attribs.textJustify = JustifyType.CENTERLEFT
    attribs.textOffsetX = 14

    # bottom hairline divider on every row
    attribs.bottomBorderInColor = _c('line')

    # ---------------- section header row ----------------------------- #
    if entry[0] == 'header':
        attribs.bgColor = _c('topbar_bg')
        attribs.text = entry[1] if col == 0 else ''
        attribs.textColor = _c('ink_dim')
        attribs.fontSizeX = _t('eyebrow')
        attribs.textOffsetX = 14
        # span: only col 0 shows text; others stay blank on same bg
        attribs.topBorderInColor = _c('line')
        return

    # ---------------- winch data row --------------------------------- #
    _, di, r = entry

    # zebra: keep flat (mockup is flat), but tint slightly on odd winch idx
    if int(r['idx']) % 2 == 0:
        attribs.bgColor = _c('panel_alt_bg')

    if col == COL['idx']:
        attribs.text = r['idx']
        attribs.textColor = _c('ink_faint')
        attribs.textJustify = JustifyType.CENTERRIGHT
        attribs.textOffsetX = -14

    elif col == COL['label']:
        attribs.text = r['label']
        attribs.textColor = _c('ink')
        attribs.fontSizeX = _t('readout')
        attribs.editable = 1
        attribs.bgColor = _c('input_bg')
        attribs.textJustify = JustifyType.CENTER
        attribs.textOffsetX = 0
        # boxed input look
        for side in ('left', 'right', 'top', 'bottom'):
            setattr(attribs, f'{side}BorderInColor', _c('line_bright'))

    elif col == COL['kind']:
        main = (r['kind'] == 'MAIN')
        attribs.text = r['kind']
        attribs.fontSizeX = _t('cap')
        attribs.fontBold = True
        attribs.textJustify = JustifyType.CENTER
        attribs.textOffsetX = 0
        if main:
            attribs.bgColor = _c('pill_main_bg')
            attribs.textColor = _c('amber')
            for s in ('left', 'right', 'top', 'bottom'):
                setattr(attribs, f'{s}BorderInColor', _c('pill_main_border'))
        else:
            attribs.bgColor = _c('pill_side_bg')
            attribs.textColor = _c('cyan')
            for s in ('left', 'right', 'top', 'bottom'):
                setattr(attribs, f'{s}BorderInColor', _c('pill_side_border'))

    elif col == COL['ip']:
        attribs.text = r['ip']
        attribs.textColor = _c('ink')
        attribs.editable = 1
        attribs.bgColor = _c('input_bg')
        attribs.textOffsetX = 12
        for side in ('left', 'right', 'top', 'bottom'):
            setattr(attribs, f'{side}BorderInColor', _c('line_bright'))

    elif col == COL['channels']:
        attribs.text = r['channels']
        attribs.textColor = _c('ink_dim')

    elif col == COL['bound']:
        if r['bound']:
            attribs.text = '\u25cf  bound'
            attribs.textColor = _c('green')
        else:
            attribs.text = '\u25cb  unbound'
            attribs.textColor = _c('ink_faint')
    return


# --- interaction ------------------------------------------------------- #
def onEdit(comp, row, col, val):
    L = _get_layout()
    if row >= len(L) or L[row][0] != 'winch':
        return
    _, di, _r = L[row]

    if col == COL['label']:
        IN.SetLabel(di, val)
    elif col == COL['ip']:
        ok = IN.SetIP(di, val)
        if not ok:
            # reject: leave model untouched, just rebuild so the cell reverts
            pass

    # rebuild layout + repaint
    _store()
    comp.par.reset.pulse() if hasattr(comp.par, 'reset') else None
    comp.cook(force=True)
    return


def onRollover(comp, row, col, coords, prevRow, prevCol, prevCoords):
    return


def onSelect(comp, startRow, startCol, startCoords,
             endRow, endCol, endCoords, start, end):
    return


def onRadio(comp, row, col, prevRow, prevCol):
    return


def onFocus(comp, row, col, prevRow, prevCol):
    return
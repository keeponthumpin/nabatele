# me is this DAT.
#
# comp is the List Component that holds this panel (panel size 1452x1000).
# row / col is the cell being updated.
#
# Data source: op('script1') — header row (WinchID, WinchType, WinchName,
# WinchX, WinchY, WinchZ, WinchIP) + one row per winch, built by
# scriptcallbacks.py off InputDataExt.
#
# Styled to match setuplistcallbacks.py (Output tab): mono font, 14px
# text inset, hairline row dividers, pill-tinted type column, boxed
# editable IP.

THEME = parent.interface
IN = parent.nabatele.InputDataExt
DATA_SRC = 'script1'

HEADER_ROW = 0
COL = dict(id=0, type=1, name=2, x=3, y=4, z=5, ip=6)
NUM_COLS = 7

# Fixed widths for id/type/name/x/y/z; ip is stretch and eats the rest.
# 70 + 130 + 110 + 190*3 = 880 fixed -> ip stretches to fill remaining
# width of the 1452px panel.
COL_W = {0: 70, 1: 130, 2: 110, 3: 190, 4: 190, 5: 190, 6: 190}

# Alignment per column, shared by header and data rows so labels sit
# directly above their values.
ALIGN = {
	COL['id']:   (JustifyType.CENTERRIGHT, -14),
	COL['type']: (JustifyType.CENTER, 0),
	COL['name']: (JustifyType.CENTER, 0),
	COL['x']:    (JustifyType.CENTERRIGHT, -14),
	COL['y']:    (JustifyType.CENTERRIGHT, -14),
	COL['z']:    (JustifyType.CENTERRIGHT, -14),
	COL['ip']:   (JustifyType.CENTER, 0),
}

HEADER_H = 40
ROW_H = 80  # 40 + 12*80 = 1000px panel height, exact fit


def _source():
	return op(DATA_SRC)


def _c(name):
	return THEME.Colors[name].rgba


def _t(name):
	return THEME.Type[name]


# called when Reset parameter is pulsed, or on load

def onInitTable(comp, attribs):
	source = _source()
	comp.par.rows = source.numRows
	comp.par.cols = NUM_COLS
	attribs.bgColor = _c('bg')
	attribs.textJustify = JustifyType.CENTERLEFT
	attribs.bottomBorderOutColor = _c('line')
	return


def onInitCol(comp, col, attribs):
	attribs.colWidth = COL_W.get(col, 100)
	attribs.colStretch = (col == COL['ip'])  # ip eats slack to fill 1452px
	return


def onInitRow(comp, row, attribs):
	attribs.rowHeight = HEADER_H if row == HEADER_ROW else ROW_H
	return


def onInitCell(comp, row, col, attribs):
	source = _source()

	# defaults shared by every cell
	attribs.text = source[row, col].val
	attribs.bgColor = _c('bg')
	attribs.fontFace = 'mono'
	attribs.fontFile = THEME.Fonts['mono']
	attribs.fontSizeX = _t('table_cell')
	attribs.textColor = _c('ink')
	attribs.editable = 0
	attribs.textOffsetX = 14
	attribs.bottomBorderInColor = _c('line')

	# ---------------- header row --------------------------------- #
	if row == HEADER_ROW:
		attribs.bgColor = _c('topbar_bg')
		attribs.textColor = _c('ink_dim')
		attribs.fontSizeX = _t('eyebrow')+1
		justify, offset = ALIGN.get(col, (JustifyType.CENTER, 14))
		attribs.textJustify = justify
		attribs.textOffsetX = offset
		return

	# ---------------- data row ------------------------------------ #
	data_row = row - 1
	if data_row % 2 == 0:
		attribs.bgColor = _c('panel_alt_bg')

	if col == COL['id']:
		attribs.textColor = _c('ink_faint')
		attribs.textJustify, attribs.textOffsetX = ALIGN[COL['id']]

	elif col == COL['type']:
		is_main = (attribs.text == 'WAHLBERG_100')
		attribs.text = 'MAIN' if is_main else 'SIDE'
		attribs.fontSizeX = _t('cap')
		attribs.fontBold = True
		attribs.textJustify, attribs.textOffsetX = ALIGN[COL['type']]
		if is_main:
			attribs.bgColor = _c('pill_main_bg')
			attribs.textColor = _c('amber')
			for s in ('left', 'right', 'top', 'bottom'):
				setattr(attribs, f'{s}BorderInColor', _c('pill_main_border'))
		else:
			attribs.bgColor = _c('pill_side_bg')
			attribs.textColor = _c('cyan')
			for s in ('left', 'right', 'top', 'bottom'):
				setattr(attribs, f'{s}BorderInColor', _c('pill_side_border'))

	elif col == COL['name']:
		attribs.textJustify, attribs.textOffsetX = ALIGN[COL['name']]

	elif col in (COL['x'], COL['y'], COL['z']):
		attribs.textColor = _c('ink_dim')
		attribs.textJustify, attribs.textOffsetX = ALIGN[col]

	elif col == COL['ip']:
		bound = (attribs.text != '0.0.0.0')
		attribs.textColor = _c('ink') if bound else _c('ink_faint')
		attribs.editable = 1
		attribs.bgColor = _c('input_bg')
		attribs.textJustify, attribs.textOffsetX = ALIGN[COL['ip']]
		for s in ('left', 'right', 'top', 'bottom'):
			setattr(attribs, f'{s}BorderInColor', _c('line_bright'))
	return


# called during specific events
#
# coords is a named tuple containing the following members: x, y, u, v

def onRollover(comp, row, col, coords, prevrow, prevcol, prevcoords):
	if row != prevrow:
		if row > HEADER_ROW:
			comp.rowAttribs[row].bgColor = _c('winch_hover_fill')
		if prevrow > HEADER_ROW:
			data_row = prevrow - 1
			base = _c('panel_alt_bg') if data_row % 2 == 0 else _c('bg')
			comp.rowAttribs[prevrow].bgColor = base
	return


def onSelect(comp, startrow, startcol, startcoords, endrow, endcol, endcoords, start, end):
	return


def onRadio(comp, row, col, prevrow, prevcol):
	return


def onFocus(comp, row, col, prevrow, prevcol):
	return


def onEdit(comp, row, col, val):
	if row <= HEADER_ROW or col != COL['ip']:
		return
	data_row = row - 1  # winch index == source row - 1 (header offset)
	ok = IN.SetIP(data_row, val)
	if ok:
		_source().cook(force=True)
		comp.cook(force=True)
	return


# return True if interested in this drop event, False otherwise
def hover(comp, row, col, coords, prevrow, prevcol, prevcoords, dragItems):
	return False


def drop(comp, row, col, coords, prevrow, prevcol, prevcoords, dragItems):
	return False
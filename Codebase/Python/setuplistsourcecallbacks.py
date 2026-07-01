"""
Script DAT Callbacks

me - this DAT

scriptOp - the OP which is cooking
"""

# press 'Setup Parameters' in the OP to call this function to re-create the
# parameters.
def onSetupParameters(scriptOp: scriptDAT):
	"""
	Called to setup custom parameters for the Script DAT.
	"""
	page = scriptOp.appendCustomPage('Custom')
	p = page.appendFloat('Valuea', label='Value A')
	p = page.appendFloat('Valueb', label='Value B')
	return

def onPulse(par: Par):
	"""
	Called when a custom pulse parameter is pushed.
	
	Args:
		par: The parameter that was pulsed
	"""
	return

def onCook(scriptOp: scriptDAT):
	winches = parent.nabatele.InputDataExt
	scriptOp.clear()
	scriptOp.appendRow(['WinchID', 'WinchType', 'WinchName', 'WinchX', 'WinchY', 'WinchZ', 'WinchIP'])
	for w in winches:
		p = w.position
		scriptOp.appendRow([
			w.winch_id,
			w.winch_type.name if w.winch_type else '',
			w.winch_name,
			f'{p.x:.0f}',
			f'{p.y:.0f}',
			f'{p.z:.0f}',
			w.address.ip_as_str,
		])
	return

def onGetCookLevel(scriptOp: scriptDAT) -> CookLevel:
	"""
	Sets the scriptOp's cook level, the conditions necessary to cause a cook.

	Return one of the following:
		CookLevel.AUTOMATIC - inputs changed and output being used. TD default
							  behavior.
		CookLevel.ON_CHANGE - inputs changed, output used or not.
		CookLevel.WHEN_USED - every frame when output is being used
		CookLevel.ALWAYS - every frame
	"""

	return CookLevel.AUTOMATIC
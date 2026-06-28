# me is this DAT.
#
# scriptOp is the OP which is cooking.
#
# Winch geometry: one point per winch at its dock-edge position (mm; scene
# scale is 1 unit = 1 mm, so positions go in unchanged). Type + addressing
# ride along as custom point attributes for downstream use.
#
# Point attributes:
#   winchtype  int    0=unassigned, 1=Winch 50, 2=Winch 100
#   dmx        int    DMX channel within universe
#   net        int    Art-Net net
#   subnet     int    Art-Net subnet
#   universe   int    Art-Net universe
#   idx        int    winch index (0-based)
#   ip_0..ip_3 int    node IP octets (a.b.c.d) for GLSL packing


def setupParameters(scriptOp):
	page = scriptOp.appendCustomPage('Winches')
	page.appendPulse('Rebuild')
	return


def onPulse(par):
	if par.name == 'Rebuild':
		par.owner.cook(force=True)
	return


def cook(scriptOp):
	scriptOp.clear()

	records = parent.nabatele.InputData.BuildWinches()

	# Declare custom point attributes once, with typed defaults.
	# IP is emitted as 4 numeric octets (ip_0..ip_3) so a GLSL POP can read
	# them and pack DMXFixtureNetAddress — string attributes aren't readable
	# in shaders.
	scriptOp.pointAttribs.create('winchtype', 0)
	scriptOp.pointAttribs.create('dmx', 0)
	scriptOp.pointAttribs.create('net', 0)
	scriptOp.pointAttribs.create('subnet', 0)
	scriptOp.pointAttribs.create('universe', 0)
	scriptOp.pointAttribs.create('idx', 0)
	scriptOp.pointAttribs.create('ip_0', 0)
	scriptOp.pointAttribs.create('ip_1', 0)
	scriptOp.pointAttribs.create('ip_2', 0)
	scriptOp.pointAttribs.create('ip_3', 0)

	for i, r in enumerate(records):
		octets = [int(o) for o in r['ip'].split('.')]
		if len(octets) != 4:
			octets = [0, 0, 0, 0]
		p = scriptOp.appendPoint()
		p.x = r['px']
		p.y = r['py']
		p.z = r['pz']
		p.winchtype = r['winchtype']
		p.dmx = r['dmx_address']
		p.net = r['net']
		p.subnet = r['subnet']
		p.universe = r['universe']
		p.idx = i
		p.ip_0 = octets[0]
		p.ip_1 = octets[1]
		p.ip_2 = octets[2]
		p.ip_3 = octets[3]

	return
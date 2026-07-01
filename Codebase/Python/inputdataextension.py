from winches import Winch, WinchType, Address, Position
from typing import Any
import tdu


# Default rig layout (mm, scene space). Indices 0-3 are pontoon mains
# (Winch 100); 4-11 are side winches (Winch 50), in left/right pairs
# stepped along z. Labels follow the §7c mockup.
DEFAULT_POINTS = [
    (4000, 0, 4000),
    (4000, 0, -4000),
    (-4000, 0, -4000),
    (-4000, 0, 4000),
    (-15000, 0.0015298986, 35000),
    (15000, 0.0015298986, 35000),
    (-15000, 0.00050996616, 11666.666),
    (15000, 0.00050996616, 11666.666),
    (-15000, -0.0005099663, -11666.668),
    (15000, -0.0005099663, -11666.668),
    (-15000, -0.0015298986, -35000),
    (15000, -0.0015298986, -35000),
]
DEFAULT_LABELS = ['A', 'B', 'C', 'D',
                  'NE', 'ENE', 'SE', 'SSE', 'SW', 'WSW', 'NW', 'NNW']
NUM_MAINS = 4


def _seed_defaults() -> list[Winch]:
    """Build the default 12-winch rig from DEFAULT_POINTS."""
    winches = []
    for i, (x, y, z) in enumerate(DEFAULT_POINTS):
        wt = WinchType.WAHLBERG_100 if i < NUM_MAINS else WinchType.WAHLBERG_50
        winches.append(Winch(
            winch_type=wt,
            winch_id=i,
            winch_name=DEFAULT_LABELS[i],
            position=Position(x, y, z),
            address=Address(),
        ))
    return winches


class inputdataextension:
    """Holds the collection of Winch objects for this comp."""

    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self._winches = tdu.Dependency(_seed_defaults())

    def __repr__(self):
        winches = self._winches.val
        lines = [f"<{type(self).__name__} {len(winches)} winches>"]
        for w in winches:
            kind = "MAIN" if w.winch_type is WinchType.WAHLBERG_100 else "SIDE"
            p = w.position
            lines.append(
                f"  [{w.winch_id:02d}] {w.winch_name:<4} {kind}  "
                f"({p.x:.0f}, {p.y:.0f}, {p.z:.0f})  {w.address.ip_as_str}"
            )
        return "\n".join(lines)

    def __len__(self):
        return len(self._winches.val)

    def __iter__(self):
        return iter(self._winches.val)

    def __getitem__(self, index):
        return self._winches.val[index]

    # ---- edit commit from the List COMP ------------------------------- #
    def SetIP(self, index: int, text: str) -> bool:
        """Parse + store a dotted-decimal IP. Returns True on success."""
        parts = text.strip().split(".")
        if len(parts) != 4:
            return False
        try:
            octets = tuple(int(p) for p in parts)
        except ValueError:
            return False
        if not all(0 <= o <= 255 for o in octets):
            return False
        if 0 <= index < len(self._winches.val):
            self._winches.val[index].address.ip = octets  # type: ignore
            self._winches.modified()
            return True
        return False

    # ---- script-SOP feed ---------------------------------------------- #
    def BuildWinches(self) -> list[dict[str, Any]]:
        """Flat per-winch records for the Script SOP to write as points."""
        records: list[dict[str, Any]] = []
        for w in self._winches.val:
            a = w.address
            records.append({
                "px": w.position.x,
                "py": w.position.y,
                "pz": w.position.z,
                "winchtype": w.winch_type.value if w.winch_type else 0,
                "dmx_address": a.dmx_address,
                "net": a.net,
                "subnet": a.subnet,
                "universe": a.universe,
                "idx": w.winch_id,
                "ip": a.ip,
            })
        return records
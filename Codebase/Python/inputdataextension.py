from winches import Winch, WinchType, Address, Position
from typing import Any
import tdu


# DMX channels consumed per winch node (drives the "1-6 / 7-12 ..." column).
CHANNELS_PER_WINCH = 6

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


class inputdataextension:
    """Holds and manages the collection of Winch objects for this comp."""

    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self._winches = tdu.Dependency([])
        self._labels = tdu.Dependency([])
        self.SeedDefaults()
    # ---- seeding ----------------------------------------------------- #


    def __repr__(self):
        winches = self._winches.val
        labels = self._labels.val
        lines = [f"<{type(self).__name__} {len(winches)} winches>"]
        for i, w in enumerate(winches):
            label = labels[i] if i < len(labels) else ""
            kind = "MAIN" if w.winch_type is WinchType.WAHLBERG_100 else "SIDE"
            p = w.position
            lines.append(
                f"  [{i:02d}] {label:<4} {kind}  "
                f"({p.x:.0f}, {p.y:.0f}, {p.z:.0f})  {w.address.ip_as_str}"
            )
        return "\n".join(lines)

    def __len__(self):
        return len(self._winches.val)

    def __iter__(self):
        return iter(self._winches.val)

    def __getitem__(self, index):
        return self._winches.val[index]
        
    def Clear(self):
            """Drop all winches and labels."""
            self._winches.val = []
            self._labels.val = []
            self._winches.modified()
            self._labels.modified()

    def SeedDefaults(self):
        """Populate the default 12-winch rig from DEFAULT_POINTS.

        Idempotent: clears first, then builds 4 mains (Winch 100) and
        8 sides (Winch 50). Addresses left at 0 (nodes are IP-addressed).
        """
        self.Clear()
        for i, (x, y, z) in enumerate(DEFAULT_POINTS):
            wt = (WinchType.WAHLBERG_100 if i < NUM_MAINS
                  else WinchType.WAHLBERG_50)
            self._add_winch(
                Winch(winch_type=wt,
                      position=Position(x, y, z),
                      address=Address()),
                label=DEFAULT_LABELS[i])
        return self.Count

    # ---- mutation ---------------------------------------------------- #
    def _add_winch(self, winch: Winch, label: str = ""):
        self._winches.val = self._winches.val + [winch]
        self._labels.val = self._labels.val + [label]
        self._winches.modified()
        self._labels.modified()

    def _get_winch(self, index: int) -> Winch:
        return self._winches.val[index]

    def _remove_winch(self, index: int):
        if 0 <= index < len(self._winches.val):
            new_w = self._winches.val.copy()
            new_l = self._labels.val.copy()
            del new_w[index]
            del new_l[index]
            self._winches.val = new_w
            self._labels.val = new_l
            self._winches.modified()
            self._labels.modified()

    # ---- script-SOP feed (unchanged) --------------------------------- #
    def _build_winches(self) -> list[dict[str, Any]]:
        """Flat per-winch records for the Script SOP to write as points."""
        records: list[dict[str, Any]] = []
        for winch in self._winches.val:
            a = winch.address
            records.append({
                "px": winch.position.x,
                "py": winch.position.y,
                "pz": winch.position.z,
                "winchtype": winch.winch_type.value if winch.winch_type else 0,
                "dmx_address": a.dmx_address,
                "net": a.net,
                "subnet": a.subnet,
                "universe": a.universe,
                "ip": '2.0.0.1',
            })
        return records

    def BuildWinches(self):
        """Per-winch records for the Script SOP. Returns the list directly."""
        return self._build_winches()

    # ---- outputs-table model ----------------------------------------- #
    @property
    def Count(self) -> int:
        return len(self._winches.val)

    def Label(self, index: int) -> str:
        try:
            return self._labels.val[index]
        except IndexError:
            return ""

    def Rows(self) -> list[dict[str, Any]]:
        """Display-ready rows for the Output List COMP.

        One dict per winch (already in winch order):
            idx        1-based row number, zero-padded string ("01")
            label      editable ID ("A", "NE", ...)
            kind       "MAIN" | "SIDE"  (pill text)
            ip         editable dotted IP string
            channels   DMX span string ("1-6")
            bound      True when the node has a non-zero IP
            is_main    convenience bool for section grouping
        """
        rows: list[dict[str, Any]] = []
        for i, w in enumerate(self._winches.val):
            is_main = (w.winch_type is WinchType.WAHLBERG_100)
            a = w.address
            start = a.dmx_address or (1 + i * CHANNELS_PER_WINCH)
            rows.append({
                "idx":      f"{i + 1:02d}",
                "label":    self.Label(i),
                "kind":     "MAIN" if is_main else "SIDE",
                "ip":       a.ip_as_str,
                "channels": f"{start}\u2013{start + CHANNELS_PER_WINCH - 1}",
                "bound":    a.ip != (0, 0, 0, 0),
                "is_main":  is_main,
            })
        return rows

    # ---- edit commit from the List COMP ------------------------------ #
    def SetLabel(self, index: int, text: str):
        if 0 <= index < len(self._labels.val):
            new_l = self._labels.val.copy()
            new_l[index] = text.strip()
            self._labels.val = new_l
            self._labels.modified()

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
    
    @property
    def Winches(self):
        return self._winches.val
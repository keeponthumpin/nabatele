from winches import Winch, WinchType, Address, Position, WinchStore
from typing import Any
import tdu

SETTINGS_FILENAME = 'settings.json'
SETTINGS_PATH = f'{project.folder}/{SETTINGS_FILENAME}'


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

# Side-winch Art-Net IPs proposed by Torben (Wahlberg, 29 Jun email) —
# 10.0.0.101-108, sequential over the NE..NNW splay order above.
# ⚠️ Still UNCONFIRMED (open item: "confirm 10.0.0.101-108 acceptable").
# Mains are DMX-only via a node, no IP -> left at Address() default (0.0.0.0).
DEFAULT_SIDE_IPS = {
    'NE':  (10, 0, 0, 101),
    'ENE': (10, 0, 0, 102),
    'SE':  (10, 0, 0, 103),
    'SSE': (10, 0, 0, 104),
    'SW':  (10, 0, 0, 105),
    'WSW': (10, 0, 0, 106),
    'NW':  (10, 0, 0, 107),
    'NNW': (10, 0, 0, 108),
}


def _seed_defaults() -> list[Winch]:
    """Build the default 12-winch rig from DEFAULT_POINTS. Used only as
    the fallback when SETTINGS_PATH is missing or corrupt — see
    WinchStore.load_or_bootstrap in winches.py."""
    winches = []
    for i, (x, y, z) in enumerate(DEFAULT_POINTS):
        wt = WinchType.WAHLBERG_100 if i < NUM_MAINS else WinchType.WAHLBERG_50
        label = DEFAULT_LABELS[i]
        winches.append(Winch(
            winch_type=wt,
            winch_id=i,
            winch_name=label,
            position=Position(x, y, z),
            address=Address(ip=DEFAULT_SIDE_IPS.get(label, (0, 0, 0, 0))),
        ))
    return winches


class inputdataextension:
    """Holds the collection of Winch objects for this comp.

    TD-facing only: owns the tdu.Dependency and exposes the methods the
    network's List COMPs / Script SOP call. All serialization/persistence
    logic lives in WinchStore (winches.py), which this class delegates to.
    """

    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self._winches = tdu.Dependency(
            WinchStore.load_or_bootstrap(SETTINGS_PATH, _seed_defaults())
        )

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

    # ---- save / load (delegates to WinchStore) ------------------------- #
    def Serialize(self) -> str:
        """Dump the current rig (layout + addressing) to a JSON string."""
        return WinchStore.to_json(self._winches.val)

    def Deserialize(self, text: str) -> bool:
        """Rebuild the winch list from JSON produced by Serialize().

        Replaces the current rig wholesale on success. Returns False (and
        leaves the current rig untouched) on any malformed input.
        """
        winches = WinchStore.from_json(text)
        if winches is None:
            return False
        self._winches.val = winches
        self._winches.modified()
        return True

    def Save(self, path: str = SETTINGS_PATH) -> bool:
        """Write the current rig to disk as JSON (default: settings.json
        in the project folder). Returns True on success."""
        return WinchStore.save(self._winches.val, path)

    def Load(self, path: str = SETTINGS_PATH) -> bool:
        """Load a rig from disk. Returns True on success, leaves the
        current rig untouched on any read/parse failure."""
        winches = WinchStore.load(path)
        if winches is None:
            return False
        self._winches.val = winches
        self._winches.modified()
        return True
from dataclasses import dataclass, field
from enum import Enum
import json


@dataclass
class Position:
    """A 3D position in scene space, expressed in millimetres.

    Mirrors the TD scene convention (`uUnitsPerMetre = 1000.0`, Y-up).
    All coordinates default to the origin.

    Attributes:
        x: Lateral position (mm).
        y: Vertical position (mm), Y-up.
        z: Depth position (mm).
    """
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Address:
    """DMX / Art-Net addressing for a single winch node.

    Holds both the Art-Net port-address components (net / subnet /
    universe) and the in-universe DMX channel, plus the node IP supplied
    by Wahlberg during the addressing handshake.

    Attributes:
        dmx_address: DMX channel within the universe (1-512).
        net: Art-Net net (0-127).
        subnet: Art-Net subnet (0-15).
        universe: Art-Net universe (0-15).
        ip: Node IP as a 4-octet tuple.
    """
    dmx_address: int = 0
    net: int = 0
    subnet: int = 0
    universe: int = 0
    ip: tuple[int, int, int, int] = (0, 0, 0, 0)

    @property
    def ip_as_str(self) -> str:
        """The IP rendered as a dotted-decimal string, e.g. "192.168.0.10"."""
        return ".".join(str(octet) for octet in self.ip)


class WinchType(Enum):
    """Wahlberg winch models used on the rig.

    Members:
        WAHLBERG_50: Wahlberg Winch 50.
        WAHLBERG_100: Wahlberg Winch 100 (~25 m max travel).
    """
    WAHLBERG_50 = 1
    WAHLBERG_100 = 2


@dataclass
class Winch:
    """A single physical winch and its control metadata.

    Bundles the winch model, its dock-edge position (from the CAD lookup
    table), and its DMX/Art-Net address.

    Attributes:
        winch_type: The Wahlberg model, or None if unassigned.
        position: Dock-edge position in mm. Defaults to a fresh origin
            Position per instance.
        address: DMX/Art-Net addressing. Defaults to a fresh Address per
            instance.
    """
    winch_type: WinchType | None = None
    winch_id: int = field(default_factory=int)
    winch_name: str = field(default_factory=str)
    position: Position = field(default_factory=Position)
    address: Address = field(default_factory=Address)


class WinchStore:
    """Serialization + persistence for a `list[Winch]`.

    Pure Python, no TD dependencies (importable + testable anywhere, same
    spirit as `theme.py`). Deliberately ignorant of `tdu.Dependency`,
    `ownerComp`, etc. — that TD-facing plumbing belongs in
    `inputdataextension.py`, which just delegates here.

        WinchStore.to_json(winches)                  -> str
        WinchStore.from_json(text)                    -> list[Winch] | None
        WinchStore.save(winches, path)                -> bool
        WinchStore.load(path)                          -> list[Winch] | None
        WinchStore.load_or_bootstrap(path, fallback)  -> list[Winch]
    """

    @staticmethod
    def to_json(winches: list[Winch]) -> str:
        """Dump a rig (layout + addressing) to a JSON string."""
        payload = {
            "version": 1,
            "winches": [
                {
                    "winch_id": w.winch_id,
                    "winch_name": w.winch_name,
                    "winch_type": w.winch_type.name if w.winch_type else None,
                    "position": {"x": w.position.x, "y": w.position.y, "z": w.position.z},
                    "address": {
                        "dmx_address": w.address.dmx_address,
                        "net": w.address.net,
                        "subnet": w.address.subnet,
                        "universe": w.address.universe,
                        "ip": list(w.address.ip),
                    },
                }
                for w in winches
            ],
        }
        return json.dumps(payload, indent=2)

    @staticmethod
    def from_json(text: str) -> list[Winch] | None:
        """Parse JSON produced by `to_json`. Returns None on any malformed
        input rather than raising, so callers can fail soft."""
        try:
            rows = json.loads(text)["winches"]
        except (ValueError, KeyError, TypeError):
            return None

        winches: list[Winch] = []
        try:
            for r in rows:
                wt_name = r["winch_type"]
                p, a = r["position"], r["address"]
                winches.append(Winch(
                    winch_type=WinchType[wt_name] if wt_name else None,
                    winch_id=r["winch_id"],
                    winch_name=r["winch_name"],
                    position=Position(p["x"], p["y"], p["z"]),
                    address=Address(
                        dmx_address=a["dmx_address"],
                        net=a["net"],
                        subnet=a["subnet"],
                        universe=a["universe"],
                        ip=tuple(a["ip"]),
                    ),
                ))
        except (KeyError, TypeError):
            return None  # partial/malformed row -> reject the whole load
        return winches

    @classmethod
    def save(cls, winches: list[Winch], path: str) -> bool:
        """Write a rig to disk as JSON. Returns True on success."""
        try:
            with open(path, 'w') as f:
                f.write(cls.to_json(winches))
            return True
        except OSError:
            return False

    @classmethod
    def load(cls, path: str) -> list[Winch] | None:
        """Read a rig from disk. Returns None on any read/parse failure."""
        try:
            with open(path, 'r') as f:
                text = f.read()
        except OSError:
            return None
        return cls.from_json(text)

    @classmethod
    def load_or_bootstrap(cls, path: str, fallback: list[Winch]) -> list[Winch]:
        """Load `path`; if it's missing or corrupt, use `fallback` and
        write it out to `path` so the file self-bootstraps for next run.
        The write is best-effort — a failure here isn't fatal, it just
        means no bootstrap file this session."""
        winches = cls.load(path)
        if winches is None:
            winches = fallback
            cls.save(winches, path)
        return winches
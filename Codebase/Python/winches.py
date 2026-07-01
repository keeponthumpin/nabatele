from dataclasses import dataclass, field
from enum import Enum


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
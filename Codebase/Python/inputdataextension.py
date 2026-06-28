from winches import Winch
from typing import Any
import tdu


class inputdataextension:
    """Holds and manages the collection of Winch objects for this comp."""

    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self._winches = tdu.Dependency([])

    def _add_winch(self, winch: Winch):
        self._winches.val = self._winches.val + [winch]
        self._winches.modified()

    def _get_winch(self, index: int) -> Winch:
        return self._winches.val[index]

    def _remove_winch(self, index: int):
        if 0 <= index < len(self._winches.val):
            new_list = self._winches.val.copy()
            del new_list[index]
            self._winches.val = new_list
            self._winches.modified()



    def _build_winches(self) -> list[dict[str, Any]]:
        """Flat per-winch records for the Script SOP to write as points."""
        records: list[dict[str, Any]] = []
        for winch in self._winches.val:
            a = winch.address
            records.append({
                # position (mm — Script SOP divides by uUnitsPerMetre)
                "px": winch.position.x,
                "py": winch.position.y,
                "pz": winch.position.z,
                # type
                "winchtype": winch.winch_type.value if winch.winch_type else 0,
                # address
                "dmx_address": a.dmx_address,
                "net": a.net,
                "subnet": a.subnet,
                "universe": a.universe,
                "ip": a.ip_as_str,          # string attr
            })
        return records

    def BuildWinches(self):
        return self._build_winches
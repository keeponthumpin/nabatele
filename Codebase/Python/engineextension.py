import tdu
from TDStoreTools import StorageManager
import TDFunctions as TDF

from winddriver import WindDriver


class engineextension:
    def __init__(self, ownerComp):
        self._ownerComp = ownerComp

        api_key = self._ownerComp.par.Windyapikey.eval()  # or wherever you store it
        self._wind = WindDriver(api_key)
        self._glsl_engine = self._ownerComp.op("glsl_engine")

        # cache so any cook can read the latest without re-fetching
        self.WindVector = tdu.Vector(0, 0, 0)
        self.WindSpeed = 0.0

    def UpdateWind(self):
        """Call once per ~10 frames. Refreshes WindVector / WindSpeed."""
        self.WindVector, self.WindSpeed = self._wind.Fetch()
        self._glsl_engine.par.vec1valuex = self.WindVector.x
        self._glsl_engine.par.vec1valuey = self.WindVector.y
        self._glsl_engine.par.vec1valuez = self.WindVector.z
        self._glsl_engine.par.vec1valuew = self.WindSpeed
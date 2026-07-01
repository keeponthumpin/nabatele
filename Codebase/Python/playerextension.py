import tdu
from TDStoreTools import StorageManager
import TDFunctions as TDF



class playerextension:
	def __init__(self, ownerComp):
		self._ownerComp = ownerComp
		self._single_winch_output = self._ownerComp.op("single_winch_output_null")
		self._pattern_winch_output = self._ownerComp.op("pattern_winch_output_null")

@property
def SingleWinchOutput(self):
	return self._single_winch_output
	
@property
def PatternWinchOutput(self):
	return self._pattern_winch_output
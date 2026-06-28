import tdu
from TDStoreTools import StorageManager
import TDFunctions as TDF

class nabateleextension:
	"""
	nabateleextension description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self._ownerComp = ownerComp
		self._codebase: td.baseCOMP = self._ownerComp.op("codebase")
		self._interface = self._ownerComp.op("interface")
		self._input_data = self._ownerComp.op("input_data")

	
	@property
	def Codebase(self):
		return self._codebase

	@property
	def Interface(self):
		return self._interface.extensions[0]

	@property
	def InputData(self):
		return self._input_data.extensions[0]
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

	
	@property
	def Codebase(self):
		return self._codebase


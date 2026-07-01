import tdu
class oscoutextension:
	"""
	oscoutextension description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self._out_port = tdu.Dependency(7000)
		self._local_address = tdu.Dependency('')
		self._network_address = tdu.Dependency('localhost')

	@property
	def OutPort(self):
		return self._out_port.val
	
	@OutPort.setter
	def OutPort(self, value):
		self._out_port.val = value
	
	@property
	def LocalAddress(self):
		return self._local_address.val
	
	@LocalAddress.setter
	def LocalAddress(self, value):
		self._local_address.val = value

	@property
	def NetworkAddress(self):
		return self._network_address.val

	@NetworkAddress.setter
	def NetworkAddress(self, value):
		self._network_address.val = value
	
	def _get_channels_names(self, amount):
		return [f'winch{i}/value/' for i in range(amount)]


	def GetChannelNames(self):
		return self._get_channels_names(len(self.ownerComp.parent.nabatele.InputDataExt))



from Products.CMFDefault.interfaces.portal_membership \
		import portal_membership as BaseInterface


class portal_membership(BaseInterface):
	""" Declare product-specific APIs for Plinn's tool.
	"""

	def getCandidateLocalRoles(self, obj) :
		""" What local roles can I assign?
			If I am a manager I can assign every portal roles
			If I am a simple member, I can assign my roles or 'possible_local_roles'
			from Plinn type information patch
		"""

	def getMemberFullNameById(self, userid) :
		""" Return	the best formated representation of user fullname.
			
			Return NAME Surname or 
			NAME or Surname or userid
		 """
	
	def getMembers(self, users) :
		""" Return wraped users """
	
	def getOtherMembers(self, users) :
		""" Return the complement of global members set """
############ TRANSLATOR DESCRIPTION ###########

#PROJECT: HETERNET DEPLOYMENT
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vinicius@inf.ufpr.br

#A SIMPLE TRANSLATION STRUCT TO MAKE IT SIMPLER
#MANAGE DICTIONARIES IN THE PROGRAM.

###############################################

############## TRANSLATOR BEGIN ###############

class Translator:
	
	__from_to = None
	__to_from = None

	def __init__(self, from_to):

		self.__from_to = from_to
		self.__to_from = {}
		for i in self.__from_to:
			self.__to_from[self.__from_to[i]] = i


	def from_to(self, key):

		try:
			return self.__from_to[key]
		except:
			return None


	def to_from(self, key):

		try:
			return self.__to_from[key]
		except:
			return None


	def get_from_to(self):
		return self.__from_to


	def get_to_from(self):
		return self.__to_from

###############################################
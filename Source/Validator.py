######## VALIDATOR CLASS DESCRIPTION ########

#PROJECT: HETERNET DEPLOYMENT
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vinicius@inf.ufpr.br

#RECEIVES A YAML REQUEST FILE WITH THE SFC
#DESCRIPTION AND THE REQUESTED OPERATIONS
#FOR EXECUTING AN NFV RESOURCE ALLOCATION.

#THE CODE ATTRIBUTE INDICATE ITS OPERATIONS
#RESULTS CODES:

#NORMAL CODES ->
#0: VALIDATION NOT COMPLETED
#1: VALID REQUEST

#ERROR CODES ->
#-1: INVALID FILE PATH PROVIDED
#-2: INVALID YAML DATA PROVIDED
#-3: INVALID MAIN KEY INCLUDED IN THE REQUEST FILE
#-4: MAIN KEY MISSING IN THE REQUEST FILE
#-5: INVALID TOPOLOGY DATA STRUCT PROVIDED (LIST EXPECTED)
#-6: DEPENDENCY DOES NOT HAVE ANY FUNCTION REFERENCE
#-7: MALFORMED DOMAIN DEPENDENCY
#-8: MALFORMED DOMAIN TYPE DEPENDENCY
#-9: MALFORMED ORCHESTRATOR DEPENDENCY
#-10: REPEATED ENTRY OF VNF ID
#-11: COST MISSING IN A DOMAIN
#-12: ORCH MISSING IN A DOMAIN
#-13: TYPE MISSING IN A DOMAIN
#-14: TRANSITION MISSING IN A DOMAIN
#-15: WRONG DATA TYPE FOR COST (FLOAT EXPECTED)
#-16: WRONG DATA TYPE FOR ORCH (LIST EXPECTED)
#-17: WRONG DATA TYPE FOR TYPE (STRING EXPECTED)
#-18: WRONG DATA TYPE FOR TRANSITION (DICT EXPECTED)
#-19: WRONG DATA TYPE FOR DEFINING ORCHESTRATORS AVAILABLE (STRING EXPECTED)
#-20: TRANSITION TO AN INVALID DOMAIN
#-21: WRONG DATA TYPE FOR DEFINING A DOMAIN TRANSITION (DICT EXPECTED)
#-22: INVALID OR MISSING KEY IN A DOMAIN TRANSITION DICTIONARY
#-23: WRONG DATA TYPE FOR LAT OR BDW (FLOAT EXPECTED)
#-24: INVALID VALUE DEFINED FOR LAT OR BDW (>= 0 EXPECTED)
#-25: INVALID OR DUPLICATED REQUIREMENT DEFINED
#-26: WRONG DATA TYPE FOR SPECIFYING A REQUIREMENT (LIST EXPECTED)
#-27: WRONG DATA TYPE FOR DEFINING A REQUIREMENT EXPRESSION (STR EXPECTED)
#-28: INVALID EXPRESSION DEFINED FOR A REQUIREMENT (>, >=, <, <=, ==, != EXPECTED)
#-29: INVALID FORMAT FOR DEFINING A REQUIREMENT EXPRESSION
#-30: INVALID VALUE DEFINED FOR A REQUIREMENT EXPRESSION (FLOAT EXPECTED)
#-31: MISSING TYPE OF REQUIREMENT

###############################################

############ VALIDATOR CLASS BEGIN ############

import os
import yaml

class Validator:

	__file_path = None
	__yaml_data = None
	__yaml_proc = None
	__status = None

	def __init__(self, request_path):

		if (self.load_yaml(request_path)):
			self.validate_yaml()


	def load_yaml(self, request_path):
		
		self.__file_path = request_path
		if not os.path.isfile(self.__file_path):
			self.__status = -1
			return False

		raw_file = open(self.__file_path, "r")
		raw_data = raw_file.read()
		raw_file.close()

		try:
			self.__yaml_data = yaml.safe_load(raw_data)
		except Exception as e:
			self.__status = -2
			return False

		self.__status = 0
		return True


	def validate_yaml(self):
		
		#MAIN KEYS VALIDATION
		key_list = ["TOPOLOGY", "DOMAINS", "REQUIREMENTS"]
		for key in self.__yaml_data:
			try:
				key_list.remove(key)
			except Exception as e:
				self.__status = -3
				return False
		if len(key_list):
			self.__status = -4
			return False

		#TOPOLOGY VALIDATION
		if not isinstance(self.__yaml_data["TOPOLOGY"], list):
			self.__status = -5
			return False

		network_functions = {}
		network_service = []
		previous_function = None
		for element in self.__yaml_data["TOPOLOGY"]:
			symbol_flag = False
			for symbol in [("<", ">", -7, 0), ("@", "@", -8, 1), ("!", "!", -9, 2)]:	
				if element.startswith(symbol[0]):
					if previous_function == None:
						self.__status = -6
						return False
					element = element.split(" ")
					if element[-1] != symbol[1] or len(element) != 3:
						self.__status = symbol[2]
						return False
					network_functions[previous_function][symbol[3]] = element[1]
					symbol_flag = True
					break
			if symbol_flag:
				continue

			if element in network_functions:
				self.__status = -10
				return False
			network_functions[element] = [None, None, None]
			network_service.append(element)
			previous_function = element
	
		#DOMAINS VALIDATION
		available_domains = list(self.__yaml_data["DOMAINS"].keys())
		for domain in available_domains:
			for symbol in [("COST", -11, float, -15), ("ORCH", -12, list, -16), ("TYPE", -13, str, -17), ("TRANSITION", -14, dict, -18)]:
				if not symbol[0] in self.__yaml_data["DOMAINS"][domain]:
					self.__status = symbol[1]
					return False
				if not isinstance(self.__yaml_data["DOMAINS"][domain][symbol[0]], symbol[2]):
					self.__status = symbol[3]
					return False

			for orchestrator in self.__yaml_data["DOMAINS"][domain]["ORCH"]:
				if not isinstance(orchestrator, str):
					self.__status = -19
					return False

			for connection in self.__yaml_data["DOMAINS"][domain]["TRANSITION"]:
				if not connection in available_domains:
					self.__status = -20
					return False

				if not isinstance(self.__yaml_data["DOMAINS"][domain]["TRANSITION"][connection], dict):
					self.__status = -21
					return False

				key_list = ["LAT", "BDW"]
				for key in self.__yaml_data["DOMAINS"][domain]["TRANSITION"][connection]:
					if not key in key_list:
						self.__status = -22
						return False
					key_list.remove(key)

					if not isinstance(self.__yaml_data["DOMAINS"][domain]["TRANSITION"][connection][key], float):
						self.__status = -23
						return False
					if self.__yaml_data["DOMAINS"][domain]["TRANSITION"][connection][key] < 0:
						self.__status = -24
						return False

		#REQUIREMENTS VALIDATION
		key_list = ["COST", "LAT", "BDW"]
		for requirement in self.__yaml_data["REQUIREMENTS"]:
			if not requirement in key_list:
				self.__status = -25
				return False
			key_list.remove(requirement)

			if not isinstance(self.__yaml_data["REQUIREMENTS"][requirement], list):
				self.__status = -26
				return False

			for expression in self.__yaml_data["REQUIREMENTS"][requirement]:
				if not isinstance(expression, str):
					self.__status = -27
					return False
				if not expression.startswith(">") and not expression.startswith(">=") and not expression.startswith("<") and not expression.startswith("<=") and not expression.startswith("==") and not expression.startswith("!="):
					self.__status = -28
					return False
				segments = expression.split(" ")
				if len(segments) != 2:
					self.__status = -29
					return False
				try:
					segments[1] = float(segments[1])
				except Exception as e:
					self.__status = -30
					return False

		if len(key_list) > 0:
			self.__status = -31
			return False

		self.__status = 1
		return True


	def get_file_path(self):
		return self.__file_path


	def get_yaml_data(self):
		return self.__yaml_data


	def get_status(self):
		return self.__status

###############################################
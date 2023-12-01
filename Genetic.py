
################ COMMON IMPORTS ###############

import local_platypus

###############################################


######## GENERATOR CLASS DESCRIPTION ##########

#PROJECT: HETERNET DEPLOYMENT
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vinicius@inf.ufpr.br

#RECEIVES A VALIDATED REQUEST AND ESTABLI-
#SHES THE REQUIRED DOMAIN DEPENDENCIES FOR
#KEEPING INDIVIDUALS VALID DURING THE OP-
#TIMIZATION PROCESS.

#IT ALSO DEFINES A SIMPLE ROUTINE FOR GE-
#NERATING RANDOM VALID INDIVIDUALS.

###############################################

class Generator(local_platypus.Generator):

	__dependencies = None

	def __init__(self, request):
		super(Generator, self).__init__()
		#adjust here

	def generate(self, problem):
		solution = Solution(problem)
		solution.variables = [x.rand() for x in problem.types]
		#adjust here
		return solution

###############################################


######### PROBLEM CLASS DESCRIPTION ###########

#PROJECT: HETERNET DEPLOYMENT
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vinicius@inf.ufpr.br

#RECEIVES A VALIDATED REQUEST AND ESTABLI-
#SHES THE REQUIRED PARAMETERS FOR EXECUT-
#ING A GENETIC ALGORITHM WITH IT.

#IT ALSO DEFINES BASIC OPERATIONS TO BE
#USED TOGETHER WITH THE STANDARD GENETIC
#STRATEGIES. FOR EXAMPLE, THE MANNERS TO
#EVALUATE A CANDIDATE.

###############################################

############# PROBLEM CLASS BEGIN #############

class Problem(local_platypus.Problem):

	__penalty = None
	__domains = None
	__service = None
	__indexed_service = None
	__constraints = None

	def __prepare(self, request):

		self.__constraints = [len(request["REQUIREMENTS"]["COST"]), len(request["REQUIREMENTS"]["LAT"]), len(request["REQUIREMENTS"]["BDW"])]
		self.__service = {}
		self.__indexed_service = {}

		index = 0
		previous = None
		marks = ("<", "@", "!")
		for element in request["TOPOLOGY"]:
			if element[0] in marks:
				self.__service[previous][marks.index(element[0])] = element[2:-2]
			else:
				self.__service[element] = [None, None, None]
				self.__indexed_service[index] = element
				previous = element
				index += 1

		self.__domains = request["DOMAINS"].items()
		self.__penalty = [float('inf'), float('inf'), float('-inf')]

	def __init__(self, request):

		self.__prepare(request)

		super(Problem, self).__init__(len(self.__service), 3, len(request["REQUIREMENTS"]["COST"]) + len(request["REQUIREMENTS"]["LAT"]) + len(request["REQUIREMENTS"]["BDW"]))
		self.types[:] = [local_platypus.Integer(0, len(request["DOMAINS"])-1)] * len(self.__service)
		self.directions[:] = [local_platypus.Problem.MINIMIZE, local_platypus.Problem.MINIMIZE, local_platypus.Problem.MAXIMIZE]
		self.constraints[:] = [i.replace(" ", "") for i in request["REQUIREMENTS"]["COST"] + request["REQUIREMENTS"]["LAT"] + request["REQUIREMENTS"]["BDW"]] + ["==1"]
		

	def evaluate(self, solution):

		genome = solution.variables[:]
		evaluation = [0,0,0]

		total_latency = 0
		total_bandwidth = 0
		total_cost = 0

		#GARANTIR QUE A POPULAÇÃO INICIAL OBSERVE AS LIMITAÇÕES DE ALOCAÇÃO EM DOMÍNIOS ESPECÍFICOS

		previous_domain = -1
		for allele in range(len(genome)):
			
			if self.__service[self.__indexed_service[allele]][1] != None:
				if self.__service[self.__indexed_service[allele]][1] != self.__domains[genome[allele]][1]["TYPE"]:
					solution.constraints[:] = [0 for i in range(len(self.__constraints))]
					solution.objectives[:] = self.__penalty
					return
			elif self.__service[self.__indexed_service[allele]][2] != None:
				if not self.__service[self.__indexed_service[allele]][1] in self.__domains[genome[allele]][1]["ORCH"]:
					solution.constraints[:] = [0 for i in range(len(self.__constraints))]
					solution.objectives[:] = self.__penalty
					return

			evaluation[0] += self.__domains[genome[allele]][1]["COST"]
			if previous_function != genome[allele]:
				evaluation[1] += self.__domains[genome[allele]][1][previous_domain]["LAT"]
				evaluation[2] += self.__domains[genome[allele]][1][previous_domain]["BDW"]
			previous_function = genome[allele]

		solution.constraints[:] = [evaluation[0] for i in range(self.__constraints[0])] + [evaluation[1] for i in range(self.__constraints[1])] + [evaluation[2] for i in range(self.__constraints[2])] + [1]
		solution.objectives[:] = evaluation

	def get_penalty(self):
		return self.__penalty

	def get_domains(self):
		return self.__domains

	def get_service(self):
		return self.__service

	def get_indexed_service(self):
		return self.__indexed_service

	def get_constraints(self):
		return self.__constraints

###############################################


########## GENETIC CLASS DESCRIPTION ##########

#PROJECT: HETERNET DEPLOYMENT
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vinicius@inf.ufpr.br

#

#THE CODE ATTRIBUTE INDICATE ITS OPERATIONS
#RESULTS CODES:

#NORMAL CODES ->

#ERROR CODES ->

###############################################

class Mapping:

	__request = None
	__problem = None
	__generator = None
	__selector = None
	__crossover = None
	__mutator = None 
	__algorithm = None
	

	def __init__(self, request, population_size, crossover_rate, mutation_rate):

		self.__problem = Problem(request)
		#self.__generator = local_platypus.operators.RandomGenerator()
		#self.__selector = local_platypus.operators.TournamentSelector()
		#self.__crossover = local_platypus.operators.SBX(probability = float(crossover_rate))
		#self.__mutator = local_platypus.operators.UM(probability = float(mutation_rate))
		#self.__algorithm = local_platypus.NSGAII(self.__problem, population_size = population_size, generator = self.__generator, selector = self.__selector, variator = local_platypus.operators.GAOperator(self.__crossover, self.__mutation))


################ COMMON IMPORTS ###############

import copy
import random
import local_platypus
import Translator

###############################################


######### MUTATOR CLASS DESCRIPTION ###########

#PROJECT: HETERNET DEPLOYMENT
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vinicius@inf.ufpr.br

#A MODIFIED UM MUTATOR. IT CONSIDERS THAT WE MAY
#HAVE SOME GENES THAT SHOULD NOT BE MUATATED.

###############################################

############# MUTATOR CLASS BEGIN #############

class Mutator(local_platypus.Mutation):

	def __init__(self, probability = 1.0, dependencies = {}):
		super(Mutator, self).__init__()
		self.probability = probability
		self.dependencies = dependencies

	def mutate(self, parent):
		result = copy.deepcopy(parent)
		problem = result.problem

		for index in range(problem.nvars):
			if random.uniform(0.0, 1.0) <= self.probability:
				permutation = result.variables[index]
				i = random.randrange(len(permutation))
				j = random.randrange(len(permutation))

				if i in self.dependencies or j in self.dependencies:
					continue

				if len(permutation) > 1:
					while i == j:
						j = random.randrange(len(permutation))

				permutation[i], permutation[j] = permutation[j], permutation[i]
				result.evaluated = False

		return result

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

	def __init__(self, dependencies = {}):
		super(Generator, self).__init__()
		self.dependencies = dependencies

	def generate(self, problem):
		solution = local_platypus.Solution(problem)
		solution.variables = [x.rand() for x in problem.types]

		for i in self.dependencies:
			solution.variables[i] = problem.types[i].encode(self.dependencies[i])

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
	__constraints = None

	__domains_translator = None
	__service_translator = None

	def __prepare(self, request):

		self.__constraints = [len(request["REQUIREMENTS"]["COST"]), len(request["REQUIREMENTS"]["LAT"]), len(request["REQUIREMENTS"]["BDW"])]
		self.__service = {}
		
		indexed_service = {}
		index = 0
		previous = None
		marks = ("<", "@", "!")
		for element in request["TOPOLOGY"]:
			if element[0] in marks:
				self.__service[previous][marks.index(element[0])] = element[2:-2]
			else:
				self.__service[element] = [None, None, None]
				indexed_service[index] = element
				previous = element
				index += 1

		self.__domains = list(request["DOMAINS"].items())
		self.__penalty = [float('inf'), float('inf'), float('-inf')]

		self.__service_translator = Translator.Translator(indexed_service)
		self.__domains_translator = Translator.Translator({i:self.__domains[i][0] for i in range(len(self.__domains))})

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

		previous_domain = -1
		for allele in range(len(genome)):
			
			if self.__service[self.__service_translator.from_to(allele)][1] != None:
				if self.__service[self.__service_translator.from_to(allele)][1] != self.__domains[genome[allele]][1]["TYPE"]:
					solution.constraints[:] = [0 for i in range(len(self.__constraints))]
					solution.objectives[:] = self.__penalty
					return
			elif self.__service[self.__service_translator.from_to(allele)][2] != None:
				if not self.__service[self.__service_translator.from_to(allele)][1] in self.__domains[genome[allele]][1]["ORCH"]:
					solution.constraints[:] = [0 for i in range(len(self.__constraints))]
					solution.objectives[:] = self.__penalty
					return
			#analisar se as transições são válidas

			evaluation[0] += self.__domains[genome[allele]][1]["COST"]
			if previous_function != genome[allele]:
				evaluation[1] += self.__domains[genome[allele]][1][previous_domain]["LAT"]
				evaluation[2] += self.__domains[genome[allele]][1][previous_domain]["BDW"]
			previous_function = genome[allele]

		solution.constraints[:] = [evaluation[0] for i in range(self.__constraints[0])] + [evaluation[1] for i in range(self.__constraints[1])] + [evaluation[2] for i in range(self.__constraints[2])] + [1]
		solution.objectives[:] = evaluation

	
	def get_translated_dependencies(self):
		
		dependencies = {}
		for function in self.__service:
			if self.__service[function][0] != None:
				dependencies[self.__service_translator.to_from(function)] = self.__domains_translator.to_from(self.__service[function][0])
		return dependencies 

	
	def get_penalty(self):
		return self.__penalty

	def get_domains(self):
		return self.__domains

	def get_domains_translator(self):
		return self.__domains_translator

	def get_service(self):
		return self.__service

	def get_service_translator(self):
		return self.__service_translator

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

		self.__request = request
		self.__problem = Problem(self.__request)
		self.__generator = Generator(dependencies = self.__problem.get_translated_dependencies())
		self.__selector = local_platypus.operators.TournamentSelector()
		self.__crossover = local_platypus.operators.SBX(probability = float(crossover_rate))
		self.__mutator = Mutator(probability = float(mutation_rate), dependencies = self.__problem.get_translated_dependencies())
		self.__algorithm = local_platypus.NSGAII(self.__problem, population_size = population_size, generator = self.__generator, selector = self.__selector, variator = local_platypus.operators.GAOperator(self.__crossover, self.__mutator))

		#falta analisar se as transições são validas
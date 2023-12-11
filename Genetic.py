
################ COMMON IMPORTS ###############

import time
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

#RECEIVES A SET OF DEPENDENCIES TO BE 
#CONSIDERED WHEN GENERATING NEW CANDI-
#DATES TO SOLVE THE OPTIMIZATION PRO-
#BLEM. IT CAN ALSO RECEIVE A PREDEFI-
#NED POPULATION TO BE INJECTED IN A
#GENERATED POPULATION.

#IT ALSO DEFINES A SIMPLE ROUTINE FOR GE-
#NERATING RANDOM VALID INDIVIDUALS.

class Generator(local_platypus.Generator):

	def __init__(self, dependencies = {}, solutions = []):
		super(Generator, self).__init__()
		self.dependencies = dependencies
		self.solutions = solutions

		for solution in solutions:
			self.solutions.append(copy.deepcopy(solution))

	def generate(self, problem):
		if len(self.solutions) > 0:
			return self.solutions.pop()
		else:
			solution = local_platypus.Solution(problem)
			solution.variables = [x.rand() for x in problem.types]

			for i in self.dependencies:
				solution.variables[i] = problem.types[i].encode(self.dependencies[i])

			return solution

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

		super(Problem, self).__init__(len(self.__service), 3, len(request["REQUIREMENTS"]["COST"]) + len(request["REQUIREMENTS"]["LAT"]) + len(request["REQUIREMENTS"]["BDW"]) + 1)
		self.types[:] = [local_platypus.Integer(0, len(request["DOMAINS"])-1)] * len(self.__service)
		self.directions[:] = [local_platypus.Problem.MINIMIZE, local_platypus.Problem.MINIMIZE, local_platypus.Problem.MAXIMIZE]
		self.constraints[:] = [i.replace(" ", "") for i in (request["REQUIREMENTS"]["COST"] + request["REQUIREMENTS"]["LAT"] + request["REQUIREMENTS"]["BDW"])] + ["==1"]

	def evaluate(self, solution):

		genome = solution.variables
		evaluation = [0,0,0]

		total_latency = 0
		total_bandwidth = 0
		total_cost = 0

		previous_domain = genome[0]
		for gene in range(len(genome)):
			
			allele = genome[gene]

			if self.__service[self.__service_translator.from_to(gene)][1] != None:
				if self.__service[self.__service_translator.from_to(gene)][1] != self.__domains[allele][1]["TYPE"]:
					solution.constraints = [0 for i in range(sum(self.__constraints))] + [0]
					solution.objectives[:] = self.__penalty
					solution.evaluated = True
					return
			if self.__service[self.__service_translator.from_to(gene)][2] != None:
				if not self.__service[self.__service_translator.from_to(gene)][1] in self.__domains[allele][1]["ORCH"]:
					solution.constraints = [0 for i in range(sum(self.__constraints))] + [0]
					solution.objectives[:] = self.__penalty
					solution.evaluated = True
					return

			evaluation[0] += self.__domains[allele][1]["COST"]
			if previous_domain != allele:

				if not self.__domains_translator.from_to(allele) in self.__domains[previous_domain][1]["TRANSITION"]:
					solution.constraints = [0 for i in range(sum(self.__constraints))] + [0]
					solution.objectives[:] = self.__penalty
					solution.evaluated = True
					return

				#== Tunneling costs ==
				evaluation[0] += self.__domains[previous_domain][1]["COST"]
				evaluation[0] += self.__domains[allele][1]["COST"]
				#=====================

				evaluation[1] += self.__domains[previous_domain][1]["TRANSITION"][self.__domains_translator.from_to(allele)]["LAT"]
				evaluation[2] += self.__domains[previous_domain][1]["TRANSITION"][self.__domains_translator.from_to(allele)]["BDW"]

			previous_domain = allele
		
		solution.constraints = [evaluation[0] for i in range(self.__constraints[0])] + [evaluation[1] for i in range(self.__constraints[1])] + [evaluation[2] for i in range(self.__constraints[2])] + [1]
		solution.objectives[:] = evaluation
		solution.evaluated = True
	
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

	def get_integer_translator(self):
		return self.__integer_translator

###############################################


########## GENETIC CLASS DESCRIPTION ##########

#PROJECT: HETERNET DEPLOYMENT
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vinicius@inf.ufpr.br

#AN ORGANIZATION CLASS TO ALLOCATE ALL THE
#REQUIRED RESOURCES FOR EXECUTING THE GENE-
#TIC ALGORITHM. THE SAME SETUP CAN BE USED
#FOR EXECUTING DEPLOYMENT AND REDEPLOYMENT
#OPERATIONS.

#THE CODE ATTRIBUTE INDICATE ITS OPERATIONS
#RESULTS CODES:

#NORMAL CODES ->
#1: READY TO EXECUTE

#ERROR CODES ->
#-1: 
#-2: 
#-3: 
#-4: 
#-5: 
#-6: 
#-7: 
#-8: 
#-9: 
#-10: 
#-11: 
#-12: 
#-13: 

###############################################

class Mapping:

	__request = None
	__problem = None
	__generator = None
	__selector = None
	__crossover = None
	__mutator = None 
	__algorithm = None
	__status = None

	def __format_pareto(self):

		formatted_pareto = []
		service = self.__problem.get_service_translator()
		domains = self.__problem.get_domains_translator()
		translator = local_platypus.Integer(0, len(self.__problem.get_domains())-1)
		
		for candidate in local_platypus.nondominated(self.__algorithm.result):
			deploy_map = [(service.from_to(0), domains.from_to(translator.decode(candidate.variables[0])))]
			for index in range(1, len(candidate.variables)):
				if candidate.variables[index-1] != candidate.variables[index]:
					deploy_map += [("TF", domains.from_to(translator.decode(candidate.variables[index-1]))), ("TF", domains.from_to(translator.decode(candidate.variables[index])))]
				deploy_map.append((service.from_to(index), domains.from_to(translator.decode(candidate.variables[index]))))
			formatted_pareto.append({"MAP": deploy_map, "RESULT":{"COST":candidate.objectives[0], "LAT":candidate.objectives[1], "BDW":candidate.objectives[2]}})

		return formatted_pareto


	def __init__(self, request, population_size, crossover_rate, mutation_rate):

		self.deployment_setup(request, population_size, crossover_rate, mutation_rate)


	def deployment_setup(self, request, population_size, crossover_rate, mutation_rate, input_population = []):
		
		if not isinstance(request, dict):
			self.__status = -1
			return

		try:
			population_size = int(population_size)
		except:
			self.__status = -2
			return

		try:
			crossover_rate = float(crossover_rate)
		except:
			self.__status = -3
			return

		try:
			mutation_rate = float(mutation_rate)
		except:
			self.__status = -4
			return

		if population_size < 2:
			self.__status = -5
			return

		if crossover_rate < 0 or crossover_rate > 1:
			self.__status = -6
			return

		if mutation_rate < 0 or mutation_rate > 1:
			self.__status = -7
			return

		if not isinstance(input_population, list):
			self.__status = -8
			return

		for candidate in input_population:
			if not isinstance(candidate, local_platypus.Solution):
				self.__status = -9
				return
			candidate.evaluated = False

		self.__request = request
		self.__problem = Problem(self.__request)
		self.__generator = Generator(dependencies = self.__problem.get_translated_dependencies(), solutions = input_population)
		self.__selector = local_platypus.operators.TournamentSelector()
		self.__crossover = local_platypus.operators.SBX(probability = float(crossover_rate))
		self.__mutator = Mutator(probability = float(mutation_rate), dependencies = self.__problem.get_translated_dependencies())
		self.__algorithm = local_platypus.NSGAII(self.__problem, population_size = population_size, generator = self.__generator, selector = self.__selector, variator = local_platypus.operators.GAOperator(self.__crossover, self.__mutator))

		self.__status = 1


	def execute_generations(self, generations):

		if self.__status != 1:
			return -10

		try:
			generations = int(generations)
		except:
			return -11

		if generations < 1:
			return -11

		self.__algorithm.nfe = False
		self.__algorithm.run(generations)

		return self.__format_pareto()


	def execute_time(self, seconds):
	
		if self.__status != 1:
			return -10

		if not isinstance(seconds, int) or seconds < 1:
			return -12

		self.__algorithm.nfe = False
		self.__algorithm.run(local_platypus.MaxTime(seconds))
		
		return self.__format_pareto()


	def convergence_test(self, step):

		if self.__status != 1:
			return -10

		if not isinstance(step, int) or step < 1:
			return -13

		self.__algorithm.nfe = False

		start_time = time.time()
		for i in range(step):
			self.__algorithm.step()
		pareto_set = [self.__format_pareto()]

		while (True):
			for i in range(step):
				self.__algorithm.step()
			pareto_set.append(self.__format_pareto())

			if pareto_set[-2] == pareto_set[-1]:
				break
		pareto_set.append(time.time() - start_time)

		return pareto_set


	def get_status(self):
		return self.__status

	def get_current_pareto(self):
		return local_platypus.nondominated(self.__algorithm.result)
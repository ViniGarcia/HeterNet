############## MAIN DESCRIPTION ##############

#PROJECT: HETERNET DEPLOYMENT
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vinicius@inf.ufpr.br

#MAIN ROUTINES FOR EXECUTING THE MAPPING AND
#RE-MAPPING OF A NETWORK SERVICE IN A MULTI-
#SFC CONTEXT.

###############################################

################ COMMON IMPORTS ###############

import numpy

import Genetic
import Validator

###############################################


############### COMMON FUNCTIONS ##############

def pareto(aggregations):

	aggregations = numpy.array(aggregations)
	i_dominates_j = numpy.all(aggregations[:,None] >= aggregations, axis=-1) & numpy.any(aggregations[:,None] > aggregations, axis=-1)
	remaining = numpy.arange(len(aggregations))
	fronts = numpy.empty(len(aggregations), int)
	frontier_index = 0

	while remaining.size > 0:
		dominated = numpy.any(i_dominates_j[remaining[:,None], remaining], axis=0)
		fronts[remaining[~dominated]] = frontier_index
		remaining = remaining[dominated]
		frontier_index += 1

	return fronts.tolist()


def prepare(population):

	if len(population) == 0:
		return

	max_cost = population[0]["RESULT"]["COST"]
	min_cost = population[0]["RESULT"]["COST"]
	max_lat = population[0]["RESULT"]["LAT"]
	min_lat = population[0]["RESULT"]["LAT"]
	max_bdw = population[0]["RESULT"]["BDW"]
	min_bdw = population[0]["RESULT"]["BDW"]

	for candidate in population[1:]:
		if candidate["RESULT"]["COST"] > max_cost:
			max_cost = candidate["RESULT"]["COST"]
		elif candidate["RESULT"]["COST"] < min_cost:
			min_cost = candidate["RESULT"]["COST"]

		if candidate["RESULT"]["LAT"] > max_lat:
			max_lat = candidate["RESULT"]["LAT"]
		elif candidate["RESULT"]["LAT"] < min_lat:
			min_lat = candidate["RESULT"]["LAT"]

		if candidate["RESULT"]["BDW"] > max_bdw:
			max_bdw = candidate["RESULT"]["BDW"]
		elif candidate["RESULT"]["BDW"] < min_bdw:
			min_bdw = candidate["RESULT"]["BDW"]

	var_cost = max_cost - min_cost
	var_lat = max_lat - min_lat
	var_bdw = max_bdw - min_bdw

	aggregations = []
	for candidate in population:
		aggregations.append([1-(candidate["RESULT"]["COST"] - min_cost)/var_cost if var_cost > 0 else 1.0, 1-(candidate["RESULT"]["LAT"] - min_lat)/var_lat if var_lat > 0 else 1.0, (candidate["RESULT"]["BDW"] - min_bdw)/var_bdw if var_bdw > 0 else 1.0])

	print(pareto(aggregations))


def compare(results):

	pass

###############################################


################# MAIN BEGIN ##################

teste = Validator.Validator("Model.yaml")
test2 = Genetic.Mapping(teste.get_yaml_data(), 30, 0, 0)
res = test2.execute_generations(10)

prepare(res)

###############################################
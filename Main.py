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
import sys
import os

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

	return aggregations


def compare(results):

	general = []
	for result_set in results:
		general += result_set
	evaluations = pareto(general)

	index = 0
	pareto_sets = []
	for result_set in results:
		pareto_sets.append([])
		for subindex in range(index, index + len(result_set)):
			pareto_sets[-1].append(evaluations[subindex])
		index += len(result_set)

	return pareto_set


def usage():

	print("================== Service Mapping on Heterogeneous Networks (HeterNet) ==================")
	print("USAGE: *.py request_file [FLAGS]")
	print("FLAGS: ")
	print("\t-p population_size: 0 < population_size < +n (std: 50)")
	print("\t-c crossover_probability: 0 <= crossover_probability <= 1 (std: 1.0)")
	print("\t-m mutation_probability: 0 <= crossover_probability <= 1 (std: 0.1)")
	print("\t-g generations: 0 < generations < +n")
	print("\t-t time: 0 < time < +n")
	print("\t-o output: output file name (std: None)")
	print("==========================================================================================")


###############################################


################# MAIN BEGIN ##################

p = 50
c = 1.0
m = 0.1
g = None
t = None
o = None

if len(sys.argv) < 2:
	usage()
	exit()

for index in range(2, len(sys.argv), 2):
	if sys.argv[index] == "-p":
		p = sys.argv[index+1]
	elif sys.argv[index] == "-c":
		c = sys.argv[index+1]
	elif sys.argv[index] == "-m":
		m = sys.argv[index+1]
	elif sys.argv[index] == "-g":
		g = sys.argv[index+1]
	elif sys.argv[index] == "-t":
		t = sys.argv[index+1]
	elif sys.argv[index] == "-o":
		o = sys.argv[index+1]

if not os.path.isfile(sys.argv[1]):
	print("ERROR: FILE DOES NOT EXIST!!\n")
	exit()

validator = Validator.Validator(sys.argv[1])
if validator.get_status() != 1:
	print("ERROR: COULD NOT VALIDATE THE PROVIDED REQUEST (", validator.get_status(), ")")
	exit()

mapper = Genetic.Mapping(validator.get_yaml_data(), p, c, m)
if mapper.get_status() != 1:
	print("ERROR: COULD NOT CREATE THE MAPPER ELEMENT (", mapper.get_status(), ")")
	exit()

if g == None and t == None:
	print("ERROR: NO STOP CRITERIA DEFINED")
	exit()

if g != None and t != None:
	print("ERROR: MULTIPLE STOP CRITERIA DEFINED")
	exit()

if g != None:
	pareto_front = mapper.execute_generations(g)
elif t != None:
	pareto_front = mapper.execute_time(t)

output = open(o, 'w') if o else sys.stdout

if g != None or t != None:
	output.write("[\n")
	for candidate in pareto_front:
		for index in range(len(candidate["MAP"])):
			candidate["MAP"][index] = list(candidate["MAP"][index])
		output.write(str(candidate) + ",\n")
	output.write("]\n")

###############################################
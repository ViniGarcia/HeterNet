############## MAIN DESCRIPTION ##############

#PROJECT: HETERNET DEPLOYMENT
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vinicius@inf.ufpr.br

#MAIN ROUTINES FOR EXECUTING THE MAPPING AND
#RE-MAPPING OF A NETWORK SERVICE IN A MULTI-
#SFC CONTEXT.

###############################################

################ COMMON IMPORTS ###############

import statistics
import time
import copy
import sys
import os

sys.path.insert(0, "./Source/")

import Genetic
import Validator

###############################################

def usage():

	print("================== Service Mapping on Heterogeneous Networks (HeterNet) ==================")
	print("USAGE: *.py request_file [FLAGS]")
	print("FLAGS: ")
	print("\t-p population_size: 0 < population_size < +n (std: 50)")
	print("\t-c crossover_probability: 0 <= crossover_probability <= 1 (std: 1.0)")
	print("\t-m mutation_probability: 0 <= crossover_probability <= 1 (std: 0.1)")
	print("\t-g generations: 0 < generations < +n")
	print("\t-t time: 0 < time < +n")
	print("\t-ec step: 0 < step < +n")
	print("\t-er step: 0 < step < +n")
	print("\t\t -f next_request")
	print("\t-o output: output file name (std: None)")
	print("==========================================================================================")


###############################################

def comparing_experiment(main_mapper, comparing_mapper, execution_time):

	experiment_reps = 30
	
	main_fronts = []
	comparing_fronts = []
	for index in range(experiment_reps):
		main_fronts.append(main_mapper.execution_time(execution_time))
		comparing_fronts.append(comparing_mapper.execute_time(execution_time))
		if isinstance(main_fronts[-1], int) or isintance(comparing_fronts[-1], int):
			return ([],[])

	return (main_fronts, comparing_fronts)

def redeployment_experiment(main_validator, main_mapper, redeployment_requests, population_size, crossover_rate, mutation_rate, generation_step):

	experiment_reps = 30
	raw_pareto = []

	deployment_fronts = []
	for index in range(experiment_reps):
		deployment_fronts.append(main_mapper.execute_generations(generation_step))
		raw_pareto.append(main_mapper.get_current_pareto())

	experiment_fronts = []
	for request in redeployment_requests:

		if main_validator.load_yaml(request):
			if not main_validator.validate_yaml():
				print("REDEPLOYMENT REQUEST", request, "IS NOT VALID (ERROR ", main_validator.get_status(), ")")
		else:
			print("REDEPLOYMENT REQUEST", request, "IS NOT VALID (ERROR ", main_validator.get_status(), ")")

		deployment = []
		redeployment = []
		for index in range(experiment_reps):
			main_mapper.deployment_setup(main_validator.get_yaml_data(), population_size, crossover_rate, mutation_rate)
			deployment.append(main_mapper.execute_generations(generation_step))
			main_mapper.deployment_setup(main_validator.get_yaml_data(), population_size, crossover_rate, mutation_rate, raw_pareto[index])
			redeployment.append(main_mapper.execute_generations(generation_step))
			raw_pareto[index] = main_mapper.get_current_pareto()

		experiment_fronts.append((deployment, redeployment))

	return (deployment_fronts, experiment_fronts)

def timing_experiment(mapper, step, generations):

	try:
		step = int(step)
	except:
		print("ERROR: INVALID STEP SIZE PROVIDED!!")
		exit()

	try:
		generations = int(generations)
	except:
		print("ERROR: INVALID MAXIMUM NUMBER OF GENERATIONS PROVIDED")
		exit()

	executing_steps = step
	experiment_reps = 30
	
	timing_results = []
	while executing_steps <= generations:
		current_timing = []
		for _ in range(experiment_reps):
			time_init = time.time()
			mapper.execute_generations(executing_steps)
			current_timing.append(time.time() - time_init)
		timing_results.append(current_timing)
		executing_steps *= 2

	for index in range(len(timing_results)):
		timing_results[index] = (pow(2, index) * step, statistics.mean(timing_results[index]), statistics.stdev(timing_results[index]))

	return timing_results

################# MAIN BEGIN ##################

p = 50
c = 1.0
m = 0.1
g = None
t = None
ec = None
er = None
erl = None
et = None
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
	elif sys.argv[index] == "-ec":
		ec = sys.argv[index+1]
	elif sys.argv[index] == "-er":
		er = sys.argv[index+1]
		erl = []
	elif sys.argv[index] == "-f":
		if erl == None:
			print("ERROR: NEXT REQUEST DEFINED WITHOUT A REDEPLOYMENT REQUIREMENT!!\n")
			exit()
		erl.append(sys.argv[index + 1])
	elif sys.argv[index] == "-et":
		et = sys.argv[index+1]
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

if g == None and t == None and ec == None and er == None:
	print("ERROR: NO STOP CRITERIA DEFINED")
	exit()

if [g, t, ec, er].count(None) != 3:
	print("ERROR: MULTIPLE STOP CRITERIA DEFINED")
	exit()

if et != None:
	if g == None:
		print("ERROR: A MAXIMUM NUMBER OF GENERATIONS WAS NOT DEFINED!!")
		exit()
	timing_results = timing_experiment(mapper, et, g)
elif g != None:
	pareto_front = mapper.execute_generations(g)
elif t != None:
	pareto_front = mapper.execute_time(t)
elif ec != None:
	steps_front = mapper.convergence_experiment(ec)
else:
	for request in erl:
		if not os.path.isfile(request):
			print("ERROR: REDEPLOYMENT FILE DOES NOT EXIST!!\n")
			exit()
	experiment_front = redeployment_experiment(validator, mapper, erl, p, c, m, er)

output = open(o, 'w') if o else sys.stdout

if (g != None and et == None) or t != None:
	extra_info = {'COST':[float('inf'), None], 'LAT':[float('inf'), None], "BDW":[float('-inf'), None]}
	output.write("[\n[\n")
	for candidate in pareto_front:
		for index in range(len(candidate["MAP"])):
			candidate["MAP"][index] = list(candidate["MAP"][index])
		output.write("\t" + str(candidate) + ",\n")
		if candidate["RESULT"]["COST"] < extra_info["COST"][0]:
			extra_info["COST"][0] = candidate["RESULT"]["COST"]
			extra_info["COST"][1] = candidate
		if candidate["RESULT"]["LAT"] < extra_info["LAT"][0]:
			extra_info["LAT"][0] = candidate["RESULT"]["LAT"]
			extra_info["LAT"][1] = candidate
		if candidate["RESULT"]["BDW"] > extra_info["BDW"][0]:
			extra_info["BDW"][0] = candidate["RESULT"]["BDW"]
			extra_info["BDW"][1] = candidate
	output.write("],\n")
	output.write("{\n")
	output.write("\tBEST_COST: " + str(extra_info["COST"][1]) + ",\n")
	output.write("\tBEST_LAT: " + str(extra_info["LAT"][1]) + ",\n")
	output.write("\tBEST_BDW: " + str(extra_info["BDW"][1]) + "\n")
	output.write("}\n]\n")
elif ec != None:
	front_compare = Genetic.compare(steps_front[:-1])
	output.write("{\n")
	for index in range(len(front_compare)):
		output.write(str(index) + ":\n\t{\n\tMEAN: " + str(round(statistics.fmean(front_compare[index]),2)) + ",\n\tMAX: " + str(max(front_compare[index])) + ",\n\tMIN: " + str(min(front_compare[index])) + ",\n\tLEN: " + str(len(front_compare[index])) + "\n\t},\n")
	output.write("}\n")
elif er != None:
	every_result = copy.copy(experiment_front[0])
	for tuple_results in experiment_front[1]:
		every_result += tuple_results[0] + tuple_results[1]
	pareto_results = Genetic.compare(every_result)
	
	index = len(experiment_front[0])
	summary = [pareto_results[:len(experiment_front[0])]]
	for tuple_results in experiment_front[1]:
		summary.append(pareto_results[index:index+len(tuple_results[0])])
		index += len(tuple_results[0])
		summary.append(pareto_results[index:index+len(tuple_results[1])])
		index += len(tuple_results[1])

	output.write("{\n")
	statistic_data = sum(summary[0], [])
	output.write("\t" + sys.argv[1] + ": {MEAN_PARETO: " + str(round(statistics.fmean(statistic_data), 2)) + ", MAX_PARETO: " + str(max(statistic_data)) + ", MIN_PARETO: " + str(min(statistic_data)) + ", STDEV_PARETO: " + str(round(statistics.stdev(statistic_data),2)) + "},\n")
	for index in range(len(erl)):
		output.write("\t" + erl[index] + "-" + str(index+1) + ": {\n")
		statistic_data = sum(summary[index*2 + 1], [])
		output.write("\t\tDEPLOY: {MEAN_PARETO: " + str(round(statistics.fmean(statistic_data), 2)) + ", MAX_PARETO: " + str(max(statistic_data)) + ", MIN_PARETO: " + str(min(statistic_data)) + ", STDEV_PARETO: " + str(round(statistics.stdev(statistic_data),2)) + "},\n")
		statistic_data = sum(summary[index*2 + 2], [])
		output.write("\t\tREDEPLOY: {MEAN_PARETO: " + str(round(statistics.fmean(statistic_data), 2)) + ", MAX_PARETO: " + str(max(statistic_data)) + ", MIN_PARETO: " + str(min(statistic_data))  + ", STDEV_PARETO: " + str(round(statistics.stdev(statistic_data),2)) + "},\n")
		output.write("\t},\n")
	output.write("}\n")
elif et != None:
	output.write("{\n")
	for result_set in timing_results:
		output.write("\t" + str(result_set[0]) + ": {MEAN_TIME: " + str(round(result_set[1], 4)) + ", STDEV_TIME: " + str(round(result_set[2], 4)) + "},\n")
	output.write("}\n")

###############################################
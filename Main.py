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
import sys
import os

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

def redeployment_experiment(main_validator, main_mapper, redeployment_requests, population_size, crossover_rate, mutation_rate, generation_step):

	experiment_reps = 30
	raw_pareto = []

	deployment_fronts = []
	for index in range(experiment_reps):
		deployment_fronts.append(mapper.execute_generations(generation_step))
		raw_pareto.append(mapper.get_current_pareto())

	experiment_fronts = []
	for request in redeployment_requests:

		if main_validator.load_yaml(request):
			if not main_validator.validate_yaml():
				print("REDEPLOYMENT REQUEST", request, "IS NOT VALID (ERROR ", main_validator.get_status(), ")")
		else:
			print("REDEPLOYMENT REQUEST", request, "IS NOT VALID (ERROR ", main_validator.get_status(), ")")
		main_mapper.deployment_setup(validator.get_yaml_data(), population_size, crossover_rate, mutation_rate)

		deployment = []
		redeployment = []
		for index in range(experiment_reps):
			mapper.set_generator([])
			deployment.append(mapper.execute_generations(generation_step))
			mapper.set_generator(raw_pareto[index])
			redeployment.append(mapper.execute_generations(generation_step))
			raw_pareto[index] = mapper.get_current_pareto()

		experiment_fronts.append((deployment, redeployment))

	#prepare visualization

################# MAIN BEGIN ##################

p = 50
c = 1.0
m = 0.1
g = None
t = None
ec = None
er = None
erl = None
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

if g != None:
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
	redeployment_experiment(validator, mapper, erl, p, c, m, er)

output = open(o, 'w') if o else sys.stdout

if g != None or t != None:
	output.write("[\n")
	for candidate in pareto_front:
		for index in range(len(candidate["MAP"])):
			candidate["MAP"][index] = list(candidate["MAP"][index])
		output.write(str(candidate) + ",\n")
	output.write("]\n")
if ec != None:
	front_compare = Genetic.compare(steps_front[:-1])
	output.write("{\n")
	for index in range(len(front_compare)):
		output.write(str(index) + ":\n\t{\n\tMEAN: " + str(statistics.fmean(front_compare[index])) + ",\n\tLEN: " + str(len(front_compare[index])) + "\n\t},\n")
	output.write("}")

###############################################
import random
import yaml

def adapt_values(yaml_data, action):

	probability = 20
	action_select = [0.8, 1.2]

	for domain in yaml_data["DOMAINS"]:
		for transition in yaml_data["DOMAINS"][domain]["TRANSITION"]:
			if random.randrange(1,100) <= probability:
				yaml_data["DOMAINS"][domain]["TRANSITION"][transition]["LAT"] *= action_select[action]

#=====================================================

file_path = "../Experiments/150x5.yaml"

raw_file = open(file_path, "r")
raw_data = raw_file.read()
raw_file.close()

yaml_data = yaml.safe_load(raw_data)

adapt_values(yaml_data, 0)

file = open("150x5-improved.yaml", "w+")
file.write(yaml.dump(yaml_data))
file.close()

adapt_values(yaml_data, 1)

file = open("150x5-damaged.yaml", "w+")
file.write(yaml.dump(yaml_data))
file.close()
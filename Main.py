############## MAIN DESCRIPTION ##############

#PROJECT: HETERNET DEPLOYMENT
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vinicius@inf.ufpr.br

#MAIN ROUTINES FOR EXECUTING THE MAPPING AND
#RE-MAPPING OF A NETWORK SERVICE IN A MULTI-
#SFC CONTEXT.

###############################################

################# MAIN BEGIN ##################

import Validator
import Genetic

teste = Validator.Validator("Model.yaml")
test2 = Genetic.Mapping(teste.get_yaml_data(), 30, 0, 0)
test2.execute_generations(1)

###############################################
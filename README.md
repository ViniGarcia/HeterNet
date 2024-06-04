Service Mapping Expedient for Networked Traffic and Environments (SeMENTE)
========================================================

### What is SeMENTE?

A Service Function Chain (SFC) defines a virtualized network service by chaining together multiple virtualized functions. The Multi-SFC [1], in turn, enables the composition of distributed services across various clouds, domains, and orchestrators within the Network Function Virtualization (NFV) paradigm. This approach overcomes the limitations of traditional deployments, where all Virtual Network Functions (VNFs) in an SFC belong to a single domain or point of presence. However, allocating resources in a Multi-SFC scenario for optimized SFC deployment is a challenging task. Thus, SeMENTE consists of a bioinspired strategy for mapping SFCs in the Multi-SFC context.

SeMENTE optimization aims to minimize overall deployment financial costs, minimize interdomain latency, and maximize interdomain bandwidth.

### How to use the SeMENTE mapper?

SeMENTE receives a YAML file as input, which defines the service topology, network domains, and mapping requirements. Currently, the SeMENTE application supports only linear service chains, which are defined as a simple YAML list with the network function IDs in order. For example, consider a linear topology with three network functions (NF1 -> NF2 -> NF3 -> NF4 -> NF5), where NF1 must be deployed in a domain with Tacker support, NF2 must be pinned to D0, and NF3 must be allocated in a cloud domain:

```
TOPOLOGY:
  - NF1
  - "! TACKER !"
  - NF2
  - "< D0 >"
  - NF3
  - "@ CLOUD @"
  - NF4
  - NF5 
```

The domain definition requires a unique ID, the domain cost (float), the available orchestrators (list of strings), the domain type (string), and the available transitions, which indicate connections/links with other domains (using the ID) and metrics to evaluate such connections/links by latency (float) and available interdomain bandwidth (float). Here is an example with three fully connected domains (D0, D1, and D2):

```
DOMAINS:
  'D0':
    COST: 10.0 
    ORCH: ["TACKER"]
    TYPE: "EDGE"
    TRANSITION:
      'D1':
        LAT: 100.0
        BDW: 10000.0
      'D2':
        LAT: 250.0
        BDW: 20000.0
  'D1':
    COST: 5.0
    ORCH: ["TACKER", "VINES", "OSM"]
    TYPE: "CLOUD"
    TRANSITION:
      'D0':
        LAT: 100.0
        BDW: 10000.0
      'D2':
        LAT: 300.0
        BDW: 20000.0
  'D2':
    COST: 25.0
    ORCH: ["TACKER", "VINES", "OSM"]
    TYPE: "EDGE"
    TRANSITION:
      'D0':
        LAT: 250.0
        BDW: 20000.0
      'D2':
        LAT: 300.0
        BDW: 20000.0 
```

Finally, policies and general requirements can be defined as a list of strings for each metric evaluated. Such requirements are relational expressions. For example, the following policies define that the mapping process should return results with costs less than or equal to 100, latency less than 550, and bandwidth greater than or equal to 10000:

```
REQUIREMENTS:           #ALLOWS >, >=, <, <=, ==, != REQUIREMENTS
  COST: ["<= 100"]
  LAT: ["< 550"]
  BDW: [">= 10000"]
 ```

After defining the YAML file that describes the optimization to be performed, it is possible to execute the SeMENTE program by tuning the genetic algorithm configurations:

```
================== Service Mapping Expedient for Networked Traffic and Environments (SeMENTE) ==================
	USAGE: *.py request_file [FLAGS]
	FLAGS: 
		-p population_size: 0 < population_size < +n (std: 50)
		-c crossover_probability: 0 <= crossover_probability <= 1 (std: 1.0)
		-m mutation_probability: 0 <= crossover_probability <= 1 (std: 0.1)
		-g generations: 0 < generations < +n
		-t time: 0 < time < +n
		-ec step: 0 < step < +n
		-er step: 0 < step < +n
		 -f next_request
		-o output: output file name (std: None)
=================================================================================================================
```

The results will be presented in the prompt, and cosists of the candidates located at the Pareto Frontier defined in the last generation created by the algoriothm (the mapping may include extra network function to enable tunnels between different domains):

```
{'MAP': [['NF1', 'D0'], ['NF2', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF3', 'D1'], ['NF4', 'D1'], ['NF5', 'D1']], 'RESULT': {'COST': 50.0, 'LAT': 100.0, 'BDW': 10000.0}},
{'MAP': [['NF1', 'D1'], ['NTF', 'D1'], ['NTF', 'D0'], ['NF2', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF3', 'D1'], ['NTF', 'D1'], ['NTF', 'D0'], ['NF4', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF5', 'D1']], 'RESULT': {'COST': 95.0, 'LAT': 400.0, 'BDW': 40000.0}},
{'MAP': [['NF1', 'D1'], ['NTF', 'D1'], ['NTF', 'D0'], ['NF2', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF3', 'D1'], ['NF4', 'D1'], ['NTF', 'D1'], ['NTF', 'D0'], ['NF5', 'D0']], 'RESULT': {'COST': 80.0, 'LAT': 300.0, 'BDW': 30000.0}},
{'MAP': [['NF1', 'D1'], ['NTF', 'D1'], ['NTF', 'D0'], ['NF2', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF3', 'D1'], ['NF4', 'D1'], ['NF5', 'D1']], 'RESULT': {'COST': 60.0, 'LAT': 200.0, 'BDW': 20000.0}},
{'MAP': [['NF1', 'D0'], ['NF2', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF3', 'D1'], ['NF4', 'D1'], ['NF5', 'D1']], 'RESULT': {'COST': 50.0, 'LAT': 100.0, 'BDW': 10000.0}},
{'MAP': [['NF1', 'D0'], ['NF2', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF3', 'D1'], ['NF4', 'D1'], ['NF5', 'D1']], 'RESULT': {'COST': 50.0, 'LAT': 100.0, 'BDW': 10000.0}},
{'MAP': [['NF1', 'D1'], ['NTF', 'D1'], ['NTF', 'D0'], ['NF2', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF3', 'D1'], ['NTF', 'D1'], ['NTF', 'D0'], ['NF4', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF5', 'D1']], 'RESULT': {'COST': 95.0, 'LAT': 400.0, 'BDW': 40000.0}},
{'MAP': [['NF1', 'D1'], ['NTF', 'D1'], ['NTF', 'D0'], ['NF2', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF3', 'D1'], ['NTF', 'D1'], ['NTF', 'D0'], ['NF4', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF5', 'D1']], 'RESULT': {'COST': 95.0, 'LAT': 400.0, 'BDW': 40000.0}},

BEST_COST: {'MAP': [['NF1', 'D0'], ['NF2', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF3', 'D1'], ['NF4', 'D1'], ['NF5', 'D1']], 'RESULT': {'COST': 50.0, 'LAT': 100.0, 'BDW': 10000.0}},
BEST_LAT: {'MAP': [['NF1', 'D0'], ['NF2', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF3', 'D1'], ['NF4', 'D1'], ['NF5', 'D1']], 'RESULT': {'COST': 50.0, 'LAT': 100.0, 'BDW': 10000.0}},
BEST_BDW: {'MAP': [['NF1', 'D1'], ['NTF', 'D1'], ['NTF', 'D0'], ['NF2', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF3', 'D1'], ['NTF', 'D1'], ['NTF', 'D0'], ['NF4', 'D0'], ['NTF', 'D0'], ['NTF', 'D1'], ['NF5', 'D1']], 'RESULT': {'COST': 95.0, 'LAT': 400.0, 'BDW': 40000.0}}
```

### Support

Contact us towards git issues requests or by the e-mail vinicius@inf.ufpr.br.

### Publications

Fulber-Garcia, V. and Flauzino, J. amd Huff, A. and Venâncio, G. and Duarte Jr., E. P.. Uma Estratégia Bioinspirada para Alocação Dinâmica de SFCs em Múltiplos Domínios, Nuvens e Orquestradores NFV. Simpósio Brasileiro de Redes de Computadores e Sistemas Distribuídos (SBRC). 2024. 

### References

[1] Huff, A.; Souza, G. V. d.; Fulber-Garcia, V.; Duarte Jr., E. P.. Building Multi-domain Service Function Chains Based on Multiple NFV Orchestrators. Conference on Network Function Virtualization and Software Defined Networks (NFV-SDN). 2020.
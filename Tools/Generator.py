import networkx
import copy
import random
import yaml

class RequestGenerator:

	__metrics = None
	__status = None

	def __defineService(self, service, stype):
		skeleton = {"TOPOLOGY":[]}

		index = 0
		limit = len(service)
		inBranch = False
		outBranch = False

		for function in service:

			if inBranch:
				skeleton["TOPOLOGY"].append("{")
				skeleton["TOPOLOGY"].append(function)
				skeleton["TOPOLOGY"].append("/")
				inBranch = False
				outBranch = True
			elif outBranch:
				skeleton["TOPOLOGY"].append(function)
				skeleton["TOPOLOGY"].append("}")
				outBranch = False
				stype = "LINEAR"
			else:
				skeleton["TOPOLOGY"].append(function)
			index += 1	

			if stype == "BRANCHED" and not outBranch:
				if index != 0 and limit - index == 3:
					inBranch = True
				else:
					if random.randrange(1, 10) >= 6:
						inBranch = True

		return skeleton

	def __defineMetrics(self, graph):
		orchestrators = ["TACKER", "OSM", "VINES", "OPENBATON"]
		types = ["EDGE", "CLOUD", "FOG"]
		domains = {"DOMAINS":{}}
		m_skeleton = {"TRANSITION":{}}

		for e_node in graph:
			t_skeleton = copy.deepcopy(graph[e_node])
			l_skeleton = copy.deepcopy(m_skeleton)

			quantity = random.randint(1, len(orchestrators)-1)
			l_skeleton["ORCH"] = random.sample(orchestrators, quantity)
			l_skeleton["TYPE"] = random.sample(types, 1)[0]

			for metric in self.__metrics["LOCAL"]:
				if self.__metrics["LOCAL"][metric]["TYPE"] == "INT":
					if self.__metrics["LOCAL"][metric]["BEGIN"] != self.__metrics["LOCAL"][metric]["END"]:
						l_skeleton[metric] = float(random.randrange(self.__metrics["LOCAL"][metric]["BEGIN"], self.__metrics["LOCAL"][metric]["END"]))
					else:
						l_skeleton[metric] = float(self.__metrics["LOCAL"][metric]["BEGIN"])
				else:
					l_skeleton[metric] = random.uniform(float(self.__metrics["LOCAL"][metric]["BEGIN"]), float(self.__metrics["LOCAL"][metric]["END"]))

			for i_node in t_skeleton:
				for metric in self.__metrics["TRANSITION"]:
					if self.__metrics["TRANSITION"][metric]["TYPE"] == "INT":
						if self.__metrics["TRANSITION"][metric]["BEGIN"] != self.__metrics["TRANSITION"][metric]["END"]:
							t_skeleton[i_node][metric] = float(random.randrange(self.__metrics["TRANSITION"][metric]["BEGIN"], self.__metrics["TRANSITION"][metric]["END"]))
						else:
							t_skeleton[i_node][metric] = float(self.__metrics["TRANSITION"][metric]["BEGIN"])
					else:
						t_skeleton[i_node][metric] = random.uniform(float(self.__metrics["TRANSITION"][metric]["BEGIN"]), float(self.__metrics["TRANSITION"][metric]["END"]))

			t_skeleton = {str(k):v for k,v in t_skeleton.items()}
			l_skeleton["TRANSITION"] = t_skeleton
			domains["DOMAINS"][e_node] = l_skeleton

		domains["DOMAINS"] = {str(k):v for k,v in domains["DOMAINS"].items()}
		return domains

	def __init__(self, metrics):

		if not isinstance(metrics, dict):
			self.__status = -1
			return

		if not "LOCAL" in metrics or not "TRANSITION" in metrics:
			self.__status = -2
			return

		if not isinstance(metrics["LOCAL"], dict) or not isinstance(metrics["TRANSITION"], dict):
			self.__status = -3
			return

		for request in metrics["LOCAL"]:
			if not "BEGIN" in metrics["LOCAL"][request]:
				self.__status = -4
				return
			if not "END" in metrics["LOCAL"][request]:
				self.__status = -5
				return

			if not isinstance(metrics["LOCAL"][request]["BEGIN"], int):
				if not isinstance(metrics["LOCAL"][request]["BEGIN"], float):
					self.__status = -6
					return
				else:
					metrics["LOCAL"][request]["TYPE"] = "FLOAT"
			else:
				metrics["LOCAL"][request]["TYPE"] = "INT"

			if not isinstance(metrics["LOCAL"][request]["END"], int):
				if not isinstance(metrics["LOCAL"][request]["END"], float):
					self.__status = -7
					return
				elif metrics["LOCAL"][request]["TYPE"] == "INT":
					metrics["LOCAL"][request]["TYPE"] = "FLOAT"

			if metrics["LOCAL"][request]["BEGIN"] > metrics["LOCAL"][request]["END"]:
				self.__status = -8
				return

		for request in metrics["TRANSITION"]:
			if not "BEGIN" in metrics["TRANSITION"][request]:
				self.__status = -9
				return
			if not "END" in metrics["TRANSITION"][request]:
				self.__status = -10
				return

			if not isinstance(metrics["TRANSITION"][request]["BEGIN"], int):
				if not isinstance(metrics["TRANSITION"][request]["BEGIN"], float):
					self.__status = -11
					return
				else:
					metrics["TRANSITION"][request]["TYPE"] = "FLOAT"
			else:
				metrics["TRANSITION"][request]["TYPE"] = "INT"

			if not isinstance(metrics["TRANSITION"][request]["END"], int):
				if not isinstance(metrics["TRANSITION"][request]["END"], float):
					self.__status = -12
					return
				elif metrics["TRANSITION"][request]["TYPE"] == "INT":
					metrics["TRANSITION"][request]["TYPE"] = "FLOAT"

			if metrics["TRANSITION"][request]["BEGIN"] > metrics["TRANSITION"][request]["END"]:
				self.__status = -13
				return

		self.__metrics = metrics
		self.__status = 1

	def completeGraph(self, nodes):
		if not isinstance(nodes, int):
			self.__status = -1
			return -1
		if nodes <= 1:
			self.__status = -2
			return -2

		return self.__defineMetrics(networkx.to_dict_of_dicts(networkx.complete_graph(nodes)))

	def barbellGraph(self, nodes, connection):
		if not isinstance(nodes, int):
			self.__status = -1
			return -1
		if nodes <= 1:
			self.__status = -2
			return -2
		if not isinstance(connection, int):
			self.__status = -22
			return -22
		if connection <= 0:
			self.__status = -24
			return-24

		return self.__defineMetrics(networkx.to_dict_of_dicts(networkx.barbell_graph(nodes, connection)))

	def cycleGraph(self, nodes):
		if not isinstance(nodes, int):
			self.__status = -1
			return -1
		if nodes <= 1:
			self.__status = -2
			return -2

		return self.__defineMetrics(networkx.to_dict_of_dicts(networkx.cycle_graph(nodes)))

	def grid2dGraph(self, x_nodes, y_nodes):
		if not isinstance(x_nodes, int) or not isinstance(y_nodes, int):
			self.__status = -1
			return -1
		if x_nodes <= 1 or y_nodes <= 1:
			self.__status = -2
			return -2

		return self.__defineMetrics(networkx.to_dict_of_dicts(networkx.grid_2d_graph(x_nodes, y_nodes)))

	def starGraph(self, nodes):
		if not isinstance(nodes, int):
			self.__status = -1
			return -1
		if nodes <= 1:
			self.__status = -2
			return -2

		return self.__defineMetrics(networkx.to_dict_of_dicts(networkx.star_graph(nodes)))

	def wheelGraph(self, nodes):
		if not isinstance(nodes, int):
			self.__status = -1
			return -1
		if nodes <= 1:
			self.__status = -2
			return -2

		return self.__defineMetrics(networkx.to_dict_of_dicts(networkx.wheel_graph(nodes)))

	def serviceGraph(self, functions, stype):

		if not isinstance(functions, list):
			self.__status = -25
			return -25
		for item in functions:
			if not isinstance(item, str):
				self.__status = -26
				return -26

		if not isinstance(stype, str):
			self.__status = -34
			return -34

		if not stype in ["LINEAR", "BRANCHED"]:
			self.__status = -35
			return -35

		if stype == "BRANCHED" and len(functions) < 4:
			self.__status = -36
			return -36

		return self.__defineService(functions, stype)

	def requestDocument(self, path, service, network):

		fullDictionary = service
		fullDictionary.update(network)
		fullDictionary.update({"REQUIREMENTS":{"COST":[], "LAT":[], "BDW":[]}})

		file = open(path, "w+")
		file.write(yaml.dump(fullDictionary))
		file.close()

	def getStatus(self):
		return self.__status


test = RequestGenerator({"LOCAL":{"COST":{"BEGIN":50, "END":1000}}, "TRANSITION":{"LAT":{"BEGIN":15, "END": 200}, "BDW":{"BEGIN":1000, "END":40000}}})
network = test.completeGraph(150)
service = test.serviceGraph(["F1", "F2", "F3", "F4", "F5"], "LINEAR")
test.requestDocument("150x5.yaml", service, network)
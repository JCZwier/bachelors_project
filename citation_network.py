import random
import itertools
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt     # !!! replace?
from collections import Counter

n = 250			# total number of papers in the network
c = 30				# number of papers that a paper cites on average
a = 1				# ground state (paper initially only cites itself)
p_pref = c / (a+c)	# probability of citing a paper based on preferential attachment (1-p is the probability of citing a random paper)

# !!! combine with the function createCitationNetwork()?
def randomizeCitationNetwork(dg, n, c):
	randomized_dg = nx.DiGraph()
	in_degrees_left = [dg.in_degree(node) for node in dg]
	
	for i in range(n):
		randomized_dg.add_node(i)
		
		if i == 0:
			continue
		elif i == 1:
			dg.add_edge(1, 0)
		elif i > 1:
			for j in range(min(i-1, c)):
				cited_paper = None
				
				# !!! do this more efficiently?
				while cited_paper == None or cited_paper == i or cited_paper in randomized_dg.successors(i) or in_degrees_left[cited_paper] == 0:	# exclude the nodes that do not have any indegrees left
					cited_paper = random.choice(list(randomized_dg.nodes()))
					print(cited_paper)
				
				randomized_dg.add_edge(i, cited_paper)
				print("(", i, " to ", cited_paper, ")")
				in_degrees_left[cited_paper] = in_degrees_left[cited_paper]-1
				print(in_degrees_left)
			
	print(in_degrees_left)
	
	return randomized_dg

def countCoCitations(dg, n):
	co_citations = []
	
	for i in range(n):
		for subset in itertools.combinations(dg.successors(i), 2):
			co_citations.append(subset)
			
	return Counter(tuple(sorted(t)) for t in co_citations)
	
def createCitationNetwork(n):	# with preferential attachment
	dg = nx.DiGraph()
	
	for i in range(n):
		dg.add_node(i)
		
		if i == 0:
			continue
		elif i == 1:
			dg.add_edge(1, 0)
		elif i > 1:
			for j in range(min(i-1, c)):
				# !!! maybe do this differently
				cited_paper = None
				p = random.uniform(0, 1)
				while cited_paper == None or cited_paper == i or cited_paper in dg.successors(i):
					if p <= p_pref:	# citing a paper based on preferential attachment
						cited_paper = random.choices(list(dg.nodes), [val+1 for (node, val) in dg.in_degree()])[0]	# +1 because a paper always cites itself
					else:	# citing a random paper
						cited_paper = random.choice(list(dg.nodes))
				dg.add_edge(i, cited_paper)
				
	return dg

cn = createCitationNetwork(n)
cc_count = countCoCitations(cn, n)
# ~ randomized_cn = randomizeCitationNetwork(cn, n, c)
randomized_cn = nx.directed_edge_swap(cn)

# ~ for value, count in cc_count.most_common(1000):
	# ~ print(value, count)

print(sorted(cn.in_degree))
print(sorted(randomized_cn.in_degree))
print(cn.edges(37))
print(randomized_cn.edges(37))

print("Amount of co-citation pairs: ", len(cc_count))

# ~ fig, ax = plt.subplots()
# ~ ax.plot(sorted((val for (key, val) in cc_count.items()), reverse=True))
# ~ plt.show()

# ~ fig, ax = plt.subplots()
# ~ ax.plot(sorted((val for (node, val) in cn.in_degree), reverse=True))
# ~ plt.show()

plt.figure(figsize=(100,100))
nx.draw_networkx(cn, pos = nx.random_layout(cn))
plt.savefig("citation_network.png")

plt.figure(figsize=(100,100))
nx.draw_networkx(randomized_cn, pos = nx.random_layout(randomized_cn))
plt.savefig("citation_network_randomized.png")

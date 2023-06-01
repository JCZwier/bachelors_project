import random
import networkx as nx

import matplotlib.pyplot as plt     # !!! REPLACE

n = 5000			# total number of papers in the network
c = 30				# number of papers that a paper cites on average
a = 1				# ground state (paper initially only cites itself)
p_pref = c / (a+c)	# probability of citing a paper based on preferential attachment (1-p is the probability of citing a random paper)
	
def countCoCitations(dg):
	pass
	
def createCitationNetwork(n):	# with preferential attachment
	dg = nx.DiGraph()
	
	for i in range(n):
		dg.add_node(i)
		
		if i == 0:
			continue
		elif i == 1:
			dg.add_edge(1, 0)
		elif i > 1:
			citations = []
			for j in range(min(dg.number_of_nodes()-1, c)):
				while citations[j] == None or citations[j] == i or citations[j] in citations:	# !!! use two while statements?
					if random.uniform(0,1) <= p_pref:	# citing a paper based on preferential attachment
						citations[j] = random.choices(list(dg.nodes), [val+1 for (node, val) in dg.in_degree()])[0]	# +1 because a paper always cites itself
					else:	# citing a random paper
						citations[j] = random.choice(list(dg.nodes))
			dg.add_edges_from(citations)
				
	return dg

cn = createCitationNetwork(n)

print(sorted(cn.in_degree, key=lambda x: x[1], reverse=True))

fig, ax = plt.subplots()
ax.plot(sorted((val for (node, val) in cn.in_degree), reverse=True))
plt.show()

# ~ plt.figure(figsize=(100,100))
# ~ nx.draw_networkx(dg, pos = nx.random_layout(cn))
# ~ plt.savefig("graph.png")

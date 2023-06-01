import random
import networkx as nx

import matplotlib.pyplot as plt     # REPLACE

n_init = 250		# initial number of papers
n = 2000			# additional number of papers added with preferential attachment
c = 15				# number of papers that a paper cites on average
a = 1				# ground state (paper initially only cites itself)
t = 0				# time of publication
p_pref = c / (a+c)	# probability of citing a paper based on preferential attachment ((1-p) is the probability of citing a random paper)
ind_cit_factor = 1.5	# probability increase for indirect citations 

dg = nx.DiGraph()
# ~ pos = {}	# necessary?

def initializeNodes(n_init, c):
	dg.add_nodes_from(range(0, n_init), time = 0)
	
	for i in range(0, n_init):
		cited_papers = random.sample(list(dg.nodes), min(len(list(dg.nodes)), c))
		dg.add_edges_from([(i, j) for j in cited_papers])
	
def indirectPrefAttachment(node, in_degrees, citation_weights):
	indirect_citations = dg.successors(node)
	
	for i in indirect_citations:
		citation_weights[i] = ind_cit_factor * citation_weights[i]	
		
	return citation_weights	
	
def addNodes(n, t):
	for i in range(n_init, n_init+n):
		dg.add_node(i, time = t)
		# ~ citation_weights = [val for (node, val) in dg.in_degree()]
		# ~ pos[i] = i, t
		
		for j in range(0, c):
			if random.uniform(0,1) <= p_pref:    # citing a paper based on preferential attachment
				cited_paper = random.choices(list(dg.nodes), [val for (node, val) in dg.in_degree()])
				# ~ cited_paper = random.choices(list(dg.nodes), citation_weights)
				dg.add_edge(i, cited_paper[0])
				# ~ citation_weights = indirectPrefAttachment(cited_paper[0], dg.in_degree(), citation_weights)
			else:   # citing a random paper
				cited_paper = random.choice(list(dg.nodes))
				dg.add_edge(i, cited_paper)
				# ~ citation_weights = indirectPrefAttachment(cited_paper, dg.in_degree(), citation_weights)
		
		t += random.randint(0, 10)

initializeNodes(n_init, c)
addNodes(n, t)

print(sorted(dg.in_degree, key=lambda x: x[1], reverse=True))
fig, ax = plt.subplots()
print(sorted((val for (node, val) in dg.in_degree), reverse=True))
ax.plot(sorted((val for (node, val) in dg.in_degree), reverse=True))
plt.show()
# ~ plt.figure(figsize=(100,100))
# ~ nx.draw_networkx(dg, pos = nx.random_layout(dg))
# ~ plt.savefig("graph.png")

import random
import itertools
import time
import numpy as np
import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt     # !!! replace?
import seaborn as sns
from collections import Counter

sns.set_theme()

n = 5000			# total number of papers in the network
c = 15				# number of papers that a paper cites on average
a = 1				# ground state (paper initially only cites itself)
p_pref = c / (a+c)	# probability of citing a paper based on preferential attachment (1-p is the probability of citing a random paper)
n_null = 10			# number of null models used for the computation of z-scores

def countCoCitationPairs(dg):
	cc_pairs_count = []		# !!! list might not be necessary
	
	for node in dg.nodes():
		for subset in itertools.combinations(dg.successors(node), 2):
			cc_pairs_count.append(subset)
			
	return Counter(tuple(sorted(t)) for t in cc_pairs_count)
	
def createNullModels(dg, n_instances):
	null_models = []
	
	for i in range(n_instances):
		null_models.append(nx.directed_configuration_model([val for (node, val) in dg.in_degree], [val for (node, val) in dg.out_degree]))
		
	return null_models
	
def computeZScores(dg, cc_count, cc_counts_null, n_null):
	cc_counts_null_distributions = []
	z_scores = {}
	
	for i in range(len(cc_count)):
		pair = list(cc_count.keys())[i]
		value = list(cc_count.values())[i]
		
		cc_counts_null_distributions.append([])
		
		for j in range(n_null):
			if pair in cc_counts_null[j].keys():
				cc_counts_null_distributions[i].append(cc_counts_null[j].get(pair))
			else:
				cc_counts_null_distributions[i].append(0)
				
		exp = np.mean(cc_counts_null_distributions[i])		
		std = np.std(cc_counts_null_distributions[i])
		
		if std == 0:
			z = None
		else:	
			z = (value - exp) / std
			
		z_scores[pair] = z
	
	return z_scores
	
def createZDistributions(dg, z_scores):
	for node in dg.nodes():
		dg.nodes[node]["z_score_dist"] = []
		for subset in itertools.combinations(dg.successors(node), 2):
			dg.nodes[node]["z_score_dist"].append(z_scores.get(subset))
	
def createCitationNetwork(n_nodes):	# with preferential attachment
	dg = nx.DiGraph()
	
	for i in range(n_nodes):
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
					if p <= p_pref:		# citing a paper based on preferential attachment
						cited_paper = random.choices(list(dg.nodes), [val+1 for (node, val) in dg.in_degree()])[0]	# +1 because a paper always cites itself
					else:	# citing a random paper
						cited_paper = random.choice(list(dg.nodes))
				dg.add_edge(i, cited_paper)
				
	return dg

start = time.time()

cn = createCitationNetwork(n)
cc_pairs_count = countCoCitationPairs(cn)

null_models = createNullModels(cn, n_null)

cc_pairs_counts_null = []
for i in range(n_null):
	cc_pairs_counts_null.append(countCoCitationPairs(null_models[i]))
	
z_scores = computeZScores(cn, cc_pairs_count, cc_pairs_counts_null, n_null)
createZDistributions(cn, z_scores)

# !!! temporary measure to remove the None values from the z-scores plot
while(None in z_scores):
    z_scores.remove(None)

z_medians = []
z_10th_percentiles = []
for node in cn.nodes():
	if cn.nodes[node]["z_score_dist"] and not all(z is None for z in cn.nodes[node]["z_score_dist"]):
		z_medians.append(np.median([z for z in cn.nodes[node]["z_score_dist"] if z is not None]))
		z_10th_percentiles.append(np.percentile([z for z in cn.nodes[node]["z_score_dist"] if z is not None], 1))

end = time.time()
print("Time elapsed: ", end - start)

# Plot z-scores of all co-citation pairs
# ~ plt.figure()
# ~ fig, ax = plt.subplots()
# ~ ax.plot(sorted([z for z in z_scores.values() if z is not None]))
# ~ plt.show()

# Plot a histogram of the medians of z-distributions of all nodes
plt.figure()
fig, ax = pyplot.subplots(figsize=(20, 20))
sns.kdeplot(data = z_medians).set(xlabel = "Z-score", title = "Medians of z-distributions of individual nodes (N = 5000)")
plt.savefig("z_medians_density.png")

# Plot a histogram of the 10th percentiles of z-distributions of all nodes
plt.figure()
fig, ax = pyplot.subplots(figsize=(20, 20))
sns.kdeplot(data = z_10th_percentiles).set(xlabel = "Z-score", title = "10th percentiles of z-distributions of individual nodes (N = 5000)")
plt.savefig("z_10th_percentiles_density.png")

# Plot frequency of co-citation pairs
# ~ plt.figure()
# ~ fig, ax = plt.subplots()
# ~ ax.plot(sorted((val for (key, val) in cc_pairs_count.items()), reverse=True))
# ~ plt.show()

# Plot amount of indegrees of all nodes
# ~ plt.figure()
# ~ fig, ax = plt.subplots()
# ~ ax.plot(sorted((val for (node, val) in cn.in_degree), reverse=True))
# ~ plt.show()

# ~ # Draw the citation network and save it as an image file
# ~ plt.figure()
# ~ fig, ax = plt.subplots()
# ~ plt.figure(figsize=(50, 50))
# ~ nx.draw_networkx(cn, pos = nx.random_layout(cn), edgelist = [], node_size = [val * 200 for node, val in cn.in_degree])
# ~ plt.savefig("citation_network.png")

# Draw the first null model and save it as an image file
# ~ plt.figure()
# ~ fig, ax = plt.subplots()
# ~ plt.figure(figsize=(100, 100))
# ~ nx.draw_networkx(null_models[0], pos = nx.random_layout(null_models[0]))
# ~ plt.savefig("citation_network_randomized.png")

import random
import itertools
import time
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt     # !!! replace?
import seaborn as sns
from collections import Counter

sns.set_theme()

n = 1000			# number of papers in the initial network
c = 30				# number of papers that a paper cites on average
a = 1				# ground state (paper initially only cites itself)
p_pref = c / (a+c)	# probability of citing a paper based on preferential attachment (1-p is the probability of citing a random paper)
n_null = 100		# number of null models used for the computation of z-scores
batch_size = 100	# size of batches of nodes when batching is enabled

def countCoCitationPairs(dg):
	cc_pairs_count = []
	
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
			
def assignNoveltyScores(dg, z_scores):
	for node in dg.nodes():
		z_scores_dist = []
		for subset in itertools.combinations(dg.successors(node), 2):
			z_scores_dist.append(z_scores.get(subset))
		if z_scores_dist and not all(z is None for z in z_scores_dist):
			dg.nodes[node]["novelty_score"] = np.median([z for z in z_scores_dist if z is not None]) # !!! or 10th percentiles?
		else:
			dg.nodes[node]["novelty_score"] = None
		
def computeBibliographicCoupling(dg):
	bibliographic_scoring = []
	for node in dg.nodes:
		max_common_references_count = 0
		most_similar_node = None
		max_common_references = []
		for other_node in dg.nodes:
			if other_node is not node:
				common_references = set(dg.successors(node)) & set(dg.successors(other_node))
				if len(common_references) > max_common_references_count:
					most_similar_node = other_node
					max_common_references = common_references
					max_common_references_count = len(common_references)
				
		bibliographic_scoring.append(max_common_references_count)
		
def citePapers(dg, pref_attachment, time_factor, batched, novelty_pref):
	new_papers = [node for node in dg.nodes if dg.out_degree(node) == 0]
	
	for citing_paper in new_papers:
		if citing_paper == 0:
			continue
		elif citing_paper == 1:
			dg.add_edge(1, 0)
		else:
			if not pref_attachment:
				for citation in range(c):
					cn.add_edge(citing_paper, random.choice(list(new_papers)))			
			else:
				for citation in range(min(citing_paper - 1, c)):
					cited_paper = None
					p = random.uniform(0, 1)
					
					while cited_paper is None or cited_paper is citing_paper or cited_paper in dg.successors(citing_paper):
						if p <= p_pref:		# citing a paper based on preferential attachment
							if time_factor:
								weight_list = [pow(1 - ((citing_paper - node) / n), 2) * (val + 1) for (node, val) in dg.in_degree()]	# (val + 1) because a paper always cites itself
							else:
								weight_list = [(val + 1) for (node, val) in dg.in_degree()]
							cited_paper = random.choices(list(dg.nodes), weight_list)[0]
						else:	# citing a random paper
							cited_paper = random.choice(list(dg.nodes))
					
					dg.add_edge(citing_paper, cited_paper)
		
start = time.time()

cn = nx.DiGraph()
	
# normal network with preferential attachment only
for i in range(n):
	cn.add_node(i)
	citePapers(cn, pref_attachment = True, time_factor = False, batched = False, novelty_pref = False)
	
# network with preferential attachment and batched release of papers (!!! make citing papers in pre-publication impossible)
for i in range(n):
	cn.add_node(i)
	citePapers(cn, pref_attachment = True, time_factor = False, batched = True, novelty_pref = False)
	
	if i >= batch_size and (batch_size % n) == 0:
		cn.add_nodes_from(range(batch_size))
		i += batch_size
		citePapers(cn, pref_attachment = True, time_factor = False, batched = True, novelty_pref = False)
				
cc_pairs_count = countCoCitationPairs(cn)
null_models = createNullModels(cn, n_null)

cc_pairs_counts_null = []
for i in range(n_null):
	cc_pairs_counts_null.append(countCoCitationPairs(null_models[i]))
	
z_scores = computeZScores(cn, cc_pairs_count, cc_pairs_counts_null, n_null)
assignNoveltyScores(cn, z_scores)

# Plot an ECDF of the medians of z-distributions of all nodes
# ~ plt.figure()
# ~ fig, ax = plt.subplots(figsize=(10, 10))
# ~ sns.ecdfplot(data = z_medians).set(title = "Papers' median z-scores (N = 1000)", xlabel = "Z-score")
# ~ plt.savefig("z_medians.png")

# Plot number of times cited for all nodes
# ~ plt.figure()
# ~ fig, ax = plt.subplots()
# ~ ax.plot(sorted((val for (node, val) in cn.in_degree), reverse = True))
# ~ ax.set(xlabel = "Node", ylabel = "Number of times cited")
# ~ plt.savefig("number_of_citations.png")

# Plot z-scores of all co-citation pairs
# ~ plt.figure()
# ~ fig, ax = plt.subplots()
# ~ ax.plot(sorted([z for z in z_scores.values() if z is not None]))
# ~ plt.show()

# Plot frequency of co-citation pairs
# ~ plt.figure()
# ~ fig, ax = plt.subplots()
# ~ ax.plot(sorted((val for (key, val) in cc_pairs_count.items()), reverse = True))
# ~ plt.show()

# ~ # Draw the citation network and save it as an image file
# ~ plt.figure()
# ~ fig, ax = plt.subplots(figsize=(50, 50), dpi=300)
# ~ ax.axis('off')
# ~ nx.draw_networkx(cn, pos = nx.random_layout(cn))
# ~ plt.savefig("citation_network.png")

end = time.time()
print("Time elapsed: ", end - start)

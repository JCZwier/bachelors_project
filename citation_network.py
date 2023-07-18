import random
import itertools
import time
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

sns.set_theme()

n = 1000			# number of papers in the initial network
c = 30				# number of papers that a paper cites on average !!! VARY THIS PARAMETER
p_pref = c / (1+c)	# probability of citing a paper based on preferential attachment (1-p_pref is the probability of citing a random paper)
n_null = 100		# number of null models used for the computation of z-scores
batch_size = 100	# size of batches of nodes when batching is enabled

def countCoCitationPairs(dg):
	cc_pairs_count = []
	
	for node in dg.nodes:
		for subset in itertools.combinations(dg.successors(node), 2):
			cc_pairs_count.append(subset)
			
	return Counter(tuple(sorted(t)) for t in cc_pairs_count)
	
def createNullModels(dg, n_instances):
	null_models = []
	
	for i in range(n_instances):
		null_models.append(nx.directed_configuration_model([val for (node, val) in dg.in_degree], [val for (node, val) in dg.out_degree]))
		
	return null_models
	
def computeZScores(dg, cc_count, cc_counts_null, n_null):
	cc_counts_null_distributions = {}
	z_scores = {}
	
	for pair in cc_count.keys():
		value = cc_count[pair]
		cc_counts_null_distributions[pair] = []
		
		for model in range(n_null):
			if pair in cc_counts_null[model]:
				cc_counts_null_distributions[pair].append(cc_counts_null[model][pair])
			else:
				cc_counts_null_distributions[pair].append(0)
				
		exp = np.mean(cc_counts_null_distributions[pair])		
		std = np.std(cc_counts_null_distributions[pair])
		
		if std == 0:
			z = None
		else:
			z = (value - exp) / std
			
		z_scores[pair] = z
		
	return z_scores
			
def computeNoveltyScores(dg):
	cc_pairs_count = countCoCitationPairs(dg)
	null_models = createNullModels(dg, n_null)

	cc_pairs_counts_null = []
	for i in range(n_null):
		cc_pairs_counts_null.append(countCoCitationPairs(null_models[i]))
		
	z_scores = computeZScores(dg, cc_pairs_count, cc_pairs_counts_null, n_null)
	
	for node in dg.nodes:
		z_scores_dist = []
		for subset in itertools.combinations(dg.successors(node), 2):
			z_scores_dist.append(z_scores.get(subset))
		if z_scores_dist and not all(z is None for z in z_scores_dist):
			# ~ dg.nodes[node]["novelty_score"] = np.percentile([z for z in z_scores_dist if z is not None], 10)
			dg.nodes[node]["novelty_score"] = np.median([z for z in z_scores_dist if z is not None])
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
		print("Node ", node, "has ", max_common_references_count, "citations in common with node ", most_similar_node, ": ", max_common_references)
		
	print(bibliographic_scoring)
	
def citePapers(dg, mode):
	new_papers = [node for node in dg.nodes if node != 0 and dg.out_degree(node) == 0]
	
	for citing_paper in new_papers:		
		if citing_paper == 1:
			dg.add_edge(1, 0)
		else:
			# prevent papers from citing papers in the same batch
			if mode == "batched":
				dg.nodes[citing_paper]["pre_publication"] = True			
			else:
				for citation in range(min(citing_paper - 1, c)):
					cited_paper = None
					
					if mode != "no_pref_attachment":
						p = random.uniform(0, 1)
						if mode == "pref_attachment":
							weight_list = [(val + 1) for (node, val) in dg.in_degree()]		# (val + 1) because a paper always cites itself
						if mode == "age_factor":
							weight_list = [(1 - ((citing_paper - node) / n)) * (val + 1) for (node, val) in dg.in_degree()]
						elif mode == "novelty_pref":
							weight_list = [(val + 1) for (node, val) in dg.in_degree()]
							novelty_scores = nx.get_node_attributes(dg, "novelty_score")
							for i in range(len(novelty_scores)):
								if novelty_scores[i] is None:
									continue
								elif novelty_scores[i] < 0:
									weight_list[i] = -1 * (weight_list[i] * (1 + novelty_scores[i]))
								elif novelty_scores[i] > 0:
									weight_list[i] = weight_list[i] / (1 + novelty_scores[i])
					
					while cited_paper is None or cited_paper is citing_paper or cited_paper in dg.successors(citing_paper) or "pre_publication" in dg.nodes[cited_paper]:
						if mode == "no_pref_attachment":
							cited_paper = random.choice(list(dg.nodes))
						else:
							if p <= p_pref:		# citing a paper based on preferential attachment
								cited_paper = random.choices(list(dg.nodes), weight_list)[0]
							else:	# citing a random paper
								cited_paper = random.choice(list(dg.nodes))
					
					dg.add_edge(citing_paper, cited_paper)
					

# network without preferential attachment
cn_no_pref_attachment = nx.DiGraph()

for i in range(n):
	cn_no_pref_attachment.add_node(i)
	citePapers(cn_no_pref_attachment, "no_pref_attachment")
	
computeNoveltyScores(cn_no_pref_attachment)


# normal network with preferential attachment only
cn = nx.DiGraph()

for i in range(n):
	cn.add_node(i)
	citePapers(cn, "pref_attachment")
	
computeNoveltyScores(cn)


# normal network with preferential attachment and age factor
cn_age_factor = nx.DiGraph()

for i in range(n):
	cn_age_factor.add_node(i)
	citePapers(cn_age_factor, "age_factor")
	
computeNoveltyScores(cn_age_factor)


# network with preferential attachment and novelty preference
cn_novelty_pref = nx.DiGraph()

for i in range(0, int(n / 2)):	# !!! change the hardcoded n / 2
	cn_novelty_pref.add_node(i)
	citePapers(cn_novelty_pref, "pref_attachment")
	
computeNoveltyScores(cn_novelty_pref)

for i in range(int(n / 2), n):
	cn_novelty_pref.add_node(i)
	citePapers(cn_novelty_pref, "novelty_pref")

computeNoveltyScores(cn_novelty_pref)


# ~ # network with preferential attachment and batched release of papers
cn_batched = nx.DiGraph()

for i in range(batch_size):
	cn_batched.add_node(i)
	citePapers(cn_batched, "pref_attachment")
	
nodes_created = batch_size

while nodes_created != n:
	if n - nodes_created < batch_size:
		cn_batched.add_nodes_from(range(nodes_created, n))
		break
	else:
		cn_batched.add_nodes_from(range(nodes_created, nodes_created + batch_size))
		nodes_created += batch_size
		
	citePapers(cn_batched, "batched")
	
computeNoveltyScores(cn_batched)


# Plot an ECDF of the medians of z-distributions of all nodes (novelty scores)
fig, ax = plt.subplots(figsize=(10, 10))
sns.ecdfplot(data = nx.get_node_attributes(cn_no_pref_attachment, "novelty_score"))
sns.ecdfplot(data = nx.get_node_attributes(cn, "novelty_score"))
sns.ecdfplot(data = nx.get_node_attributes(cn_age_factor, "novelty_score"))
sns.ecdfplot(data = nx.get_node_attributes(cn_batched, "novelty_score"))
sns.ecdfplot(data = nx.get_node_attributes(cn_novelty_pref, "novelty_score"))
plt.legend(labels = ["No preferential attachment", "Preferential attachment", "Preferential attachment and age factor", "Preferential attachment and batched papers", "Preferential attachment and novelty preference"], loc='lower right')
plt.xlabel("Z-score")
plt.savefig("../Thesis/img/z_scores_all_modes_medians.eps", format="eps")

# Plot number of times cited for all nodes
# ~ fig, ax = plt.subplots()
# ~ ax.plot(sorted((val for (node, val) in cn.in_degree), reverse = True))
# ~ ax.set(xlabel = "Node", ylabel = "Number of times cited")
# ~ plt.show()

# Plot z-scores of all co-citation pairs
# ~ fig, ax = plt.subplots()
# ~ ax.plot(sorted([z for z in z_scores.values() if z is not None]))
# ~ plt.show()

# Plot frequency of co-citation pairs
# ~ fig, ax = plt.subplots()
# ~ ax.plot(sorted((val for (key, val) in cc_pairs_count.items()), reverse = True))
# ~ plt.show()

# ~ # Draw the citation network and save it as an image file
# ~ fig, ax = plt.subplots(figsize=(50, 50), dpi=300)
# ~ ax.axis('off')
# ~ nx.draw_networkx(cn, pos = nx.random_layout(cn))
# ~ plt.savefig("citation_network.png")

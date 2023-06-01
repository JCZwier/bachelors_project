import numpy as np
import networkx as nx

reps = 100                      # times new networks created
A = 100                         # simulations on each network
C = 200                         # citation chances per simulation
P = 100                         # nodes in network
p1 = np.linspace(0.5, 0.9, 5)   # proportion majority group members
H = np.linspace(0.5, 0.9, 5)    # determines in- vs. out-group linking probability
cit = 0.3                       # probability of citing

# track: M cites M, Mm, mM, mm (M=majority, m=minority)
gc = np.zeros(4, len(p1), len(H), A, reps)


for pr1 in p1:
    for h in H:
        for r in range(reps):  
            # make a multitype random graph
            pin=h/10; pout=(1-h)/10; run('multitype.m')
            
            for a in range(A):
                # pick authors (one from maj. and one from min.)
                onez = find(types(1, 1:N) == 1); zeroz = find(types(1, 1:N) == 0)
                disc(1, 1) = np.random.rand(onez, 1); disc(1, 2) = np.random.rand(zeroz, 1)

                # draw people from the network at random to cite the papers
                citers = np.random.rand(1:N, C, true); G = nx.graph.Graph(net)
                
                # and record who cites whom
                gcita = np.zeros(1, 4) % M cites M, Mm, mM, mm (M=majority, m=minority)
                for c = citers:
                    d = distances(G, c, disc) # path length to authors
                    if min(d) == 0: # self-citation always happens
                        if c == disc(1, 1):
                            gcita(1, 1) = gcita(1, 1) + 1 # MM
                        else
                            gcita(1, 4) = gcita(1, 4) + 1 # mm
                    else # otherwise, depends on path length & citation prob.
                        pc1 = cit^d(1)
                        pc2 = cit^d(2) 
                        if np.random.rand() < pc1
                            if types(1, c)==1
                                gcita(1, 1) = gcita(1, 1) + 1 # MM
                            else
                                gcita(1, 3) = gcita(1, 3) + 1 # mM
                        if np.random.rand() < pc2:
                            if types(1, c) == 1:
                                gcita(1, 2) = gcita(1, 2) + 1 # Mm
                            else:
                                gcita(1, 4) = gcita(1, 4) + 1 # mm
                # record final counts for that simulation
                gc(:, find(p1==pr1),find(H==h), a, r) = gcita' % MM, Mm, mM, mm
    datestr(clock) # (track progress to see how long it's taking)

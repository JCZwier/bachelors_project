import graph_tool.all as gt

N = 10				# number of papers
m = 2				# number of papers that a paper cites on average
t = 0				# time of publication

g = gt.price_network(20000)

gt.graph_draw(g, pos=gt.sfdp_layout(g, cooling_step=0.99),

              vertex_fill_color=g.vertex_index, vertex_size=2,

              vcmap=matplotlib.cm.plasma,

              edge_pen_width=1, output="price-network.pdf")

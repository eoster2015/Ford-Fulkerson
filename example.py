import cairocffi
import ford_fulkerson as ff
import igraph as ig
from igraph import *


def main():
    g = Graph(directed=True)
    g.add_vertices(6)
    vertices = ["s", "a", "b", "c", "d", "t"]
    g.add_edges([(0, 1), (0, 3), (1, 2), (1, 3), (1, 4), (2, 3), (2, 5), (3, 1), (3, 4), (4, 2), (4, 3), (4, 5)])
    flows = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    capacities = [18, 15, 12, 10, 2, 9, 22, 4, 18, 7, 3, 8]
    labels = []
    for i in range(len(capacities)):
        current_string = str(flows[i]) + "/" + str(capacities[i])
        labels.append(current_string)
    g.vs["label"] = vertices
    g.es["label"] = labels
    g.es["flow"] = flows
    g.es["capacity"] = capacities

    graph_style = {}
    graph_style["vertex_color"] = "gold"
    graph_style["vertex_size"] = 20
    graph_style["bbox"] = (600, 600)
    ig.plot(g, **graph_style)

    max_flow = ff.max_flow(g)
    min_cut_edgelist, vertex_partitions = ff.min_cut(g)

    print("The maximum flow of this graph is ", max_flow, sep="")
    print("The minimum cut edges of this graph are ", min_cut_edgelist, sep="")
    print("The resultant vertex partitions are ", vertex_partitions, sep="")
    ff.plot_min_cut_highlight(g)
    ff.plot_min_cut_partition(g)


if __name__ == '__main__':
    main()

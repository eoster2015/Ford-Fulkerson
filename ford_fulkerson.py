import cairocffi
import copy
from igraph import *
import itertools
import warnings

# an interface between cairo and python, such as cairocffi, is necessary for graphs to plot properly

def ford_fulkerson(g):
    nodes = g.vs.indices
    labels = g.vs["label"]
    residual_networks = []
    augmenting_path = []
    augmenting_flow = []
    g_sequence = [copy.deepcopy(g)]

    while True:
        # construct residual network
        g_residual = Graph(directed=True)
        g_residual.add_vertices(len(nodes))
        g_residual.vs["label"] = labels
        weights = []
        for edge in g.get_edgelist():
            x, y = edge
            g_residual.add_edges([(x, y), (y, x)])
            weights += [g.es[g.get_eid(x, y)]["capacity"] - g.es[g.get_eid(x, y)]["flow"],
                        g.es[g.get_eid(x, y)]["flow"]]
        g_residual.es["weight"] = weights
        g_residual.es.select(weight=0).delete()
        g_residual.es["weight"] = [int(weight) for weight in g_residual.es["weight"]]
        g_residual.es["label"] = g_residual.es["weight"]

        # find augmenting path
        with warnings.catch_warnings():
            # suppress igraph warning for shortest path of length 0,
            # since that is the condition we are checking for
            warnings.filterwarnings("ignore", message="Couldn't reach some vertices")
            current_path = g_residual.get_shortest_paths(v=g_residual.vs[0], to=g_residual.vs[-1], output="epath")
        current_path = list(itertools.chain.from_iterable(current_path))
        # if shortest path length between source and target vertices on the residual network is 0,
        # then the maximum flow through network has been found and the loop can be exited
        if len(current_path) == 0:
            residual_networks.append(copy.deepcopy(g_residual))
            break
        current_weight = []
        for i in range(len(current_path)):
            current_weight.append(g_residual.es[current_path[i]]["weight"])
            current_path[i] = g_residual.get_edgelist()[current_path[i]]
        current_min_flow = min(current_weight)
        augmenting_path.append(current_path)
        augmenting_flow.append(current_min_flow)

        # update flow of original graph
        for edge in current_path:
            x, y = edge
            g.es[g.get_eid(x, y)]["flow"] += current_min_flow
        new_labels = []
        for i in range(g.ecount()):
            current_string = str(g.es[i]["flow"]) + "/" + str(g.es[i]["capacity"])
            new_labels.append(current_string)
        g.es["label"] = new_labels
        g_sequence.append(copy.deepcopy(g))
        residual_networks.append(copy.deepcopy(g_residual))

    return augmenting_flow, residual_networks[-1]


def max_flow(g):
    augmenting_flow, final_residual_network = ford_fulkerson(g)
    return sum(augmenting_flow)


def min_cut(g):
    augmenting_flow, final_residual_network = ford_fulkerson(g)
    for edge in final_residual_network.get_edgelist():
        x, y = edge
        if x > y:
            final_residual_network.delete_edges(final_residual_network.es[final_residual_network.get_eid(x, y)])
    # the minimum cut is the edges on the shortest paths connecting reachable vertexes to the source node
    final_residual_network_shortest_paths = []
    for i in range(1, final_residual_network.vcount()):
        with warnings.catch_warnings():
            # suppress igraph warning for shortest path of length 0
            warnings.filterwarnings("ignore", message="Couldn't reach some vertices")
            current_path = final_residual_network.get_shortest_paths(
                v=final_residual_network.vs[0], to=final_residual_network.vs[i], output="vpath")[0]
        final_residual_network_shortest_paths.append(current_path)

    vertex_partitions = [[0], []]
    for i in range(len(final_residual_network_shortest_paths)):
        if len(final_residual_network_shortest_paths[i]) > 0:
            vertex_partitions[0].append(i + 1)
        else:
            vertex_partitions[1].append(i + 1)

    min_cut_edgelist = []
    for i in range(len(vertex_partitions[0])):
        for j in range(len(vertex_partitions[1])):
            x = vertex_partitions[0][i]
            y = vertex_partitions[1][j]
            if g.get_eid(x, y, directed=True, error=False) != -1:
                min_cut_edgelist.append([x, y])

    return min_cut_edgelist, vertex_partitions


def plot_min_cut_highlight(g):
    min_cut_edgelist, vertex_partitions = min_cut(g)
    final_cut_g = copy.deepcopy(g)
    final_cut_g.es["color"] = "black"
    final_cut_g.es["label"] = final_cut_g.es["capacity"]
    for edge in min_cut_edgelist:
        x, y = edge
        final_cut_g.es[final_cut_g.get_eid(x, y)]["color"] = "red"
    graph_style = {}
    g_cut_class = []
    for i in range(g.vcount()):
        if i in vertex_partitions[0]:
            g_cut_class.append(1)
        if i in vertex_partitions[1]:
            g_cut_class.append(2)
    node_color_dict = ["white", "cyan", "magenta"]
    final_cut_g.vs["class"] = g_cut_class
    final_cut_g.vs["label"] = g.vs["label"]
    graph_style["vertex_color"] = [node_color_dict[vert] for vert in final_cut_g.vs["class"]]
    graph_style["vertex_size"] = 20
    graph_style["bbox"] = (600, 600)
    plot(final_cut_g, **graph_style)


def plot_min_cut_partition(g):
    min_cut_edgelist, vertex_partitions = min_cut(g)
    split_g = copy.deepcopy(g.as_undirected())
    split_g.es["color"] = "black"
    for i in range(len(vertex_partitions[0])):
        for j in range(len(vertex_partitions[1])):
            x = vertex_partitions[0][i]
            y = vertex_partitions[1][j]
            if split_g.get_eid(x, y, directed=False, error=False) != -1:
                split_g.delete_edges(split_g.es[split_g.get_eid(x, y)])
    graph_style = {}
    g_cut_class = []
    for i in range(g.vcount()):
        if i in vertex_partitions[0]:
            g_cut_class.append(1)
        if i in vertex_partitions[1]:
            g_cut_class.append(2)
    node_color_dict = ["white", "cyan", "magenta"]
    split_g.vs["class"] = g_cut_class
    split_g.vs["label"] = g.vs["label"]
    graph_style["vertex_color"] = [node_color_dict[vert] for vert in split_g.vs["class"]]
    graph_style["vertex_size"] = 20
    graph_style["bbox"] = (600, 600)
    plot(split_g, **graph_style)

import sys
import networkx as nx
import matplotlib.pyplot as plt

def is_central_point_of_graph(node, graph, comp_rel_color="green", delim_rel_color="red"):
    if not graph.has_node(node):
        return False
    if len(graph.in_edges(node)) > 0:
        return False
    for e in graph.out_edges(node):
        if graph.get_edge_data(e[0], e[1])["color"] == delim_rel_color:
            return False
    return True

def subgraph_only_color(graph, color):
    edges = []
    for e in graph.edges:
        #print(e)
        if graph.get_edge_data(e[0],e[1])["color"] == color:
            edges.append(e)

    return graph.edge_subgraph(edges).copy()

def alg(graph, data, i):
    if len(graph.nodes) == 0:
        return data
    co_alpha = list(nx.weakly_connected_components(subgraph_only_color(graph, "green")))
    co_alpha.extend([{x} for x in nx.isolates(graph)])

    central_nodes = []
    for c in co_alpha:
        component_as_graph = graph.subgraph(c)
        for x in component_as_graph.nodes:
            if is_central_point_of_graph(x, component_as_graph):
                central_nodes.append(x)
    graph.remove_nodes_from(central_nodes)

    data[i] = {"co": co_alpha, "cn": central_nodes}

    #print(graph.nodes)

    green_edges = []
    red_edges = []
    for e in graph.edges.data("color", default="green"):
        if e[2] == "green":
            green_edges.append((e[0], e[1]))
        else:
            red_edges.append((e[0], e[1]))

    fig, ax = plt.subplots()
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph, pos)
    nx.draw_networkx_labels(graph, pos)
    nx.draw_networkx_edges(graph, pos, edgelist=green_edges, edge_color="tab:green")
    nx.draw_networkx_edges(graph, pos, edgelist=red_edges, edge_color="tab:red")
    fig.savefig("e_"+str(i)+".png")
    plt.close(fig)

    print("STEP: " + str(i) + " | CO_ALPHA: " + str(co_alpha) + " | CENTRAL NODES: " + ",".join(str(x) for x in central_nodes))
    i+=1
    return alg(graph,data,i)

def generate_sequential_edge_list(n, prefix="x", suffix="", comp_rel_color="green"):
    edge_list = []
    for i in range(0, n):
        edge_list.append((prefix + str(i) + suffix, prefix + str(i+1) + suffix, {"color": comp_rel_color}))
    return edge_list

def generate_triple_u(n,m, i, comp_rel_color="green", delim_rel_color="red"):
    edge_list = [(x[0]+"_"+str(i), x[1]+"_"+str(i), {"color":comp_rel_color}) for x in [("r", "b3"), ("a2", "b3"), ("a2", "b2"), ("a1", "b2"), ("a1", "b1"), ("l", "b1"), ("x"+str(n), "a2"), ("y"+str(m), "a1")]]
    edge_list.append(("r_"+str(i), "l_"+str(i), {"color":delim_rel_color}))
    edge_list.append(("l_"+str(i), "r_"+str(i), {"color":delim_rel_color}))
    edge_list.extend(generate_sequential_edge_list(n, "x", "_" + str(i), comp_rel_color))
    edge_list.extend(generate_sequential_edge_list(m, "y", "_" + str(i), comp_rel_color))

    return edge_list

def get_road_of_node(node, data):
    road = []
    for _,val in data.items():
        for c in val["co"]:
            if node in c:
                road.append(c)
    return road

def list_to_hashset(l):
    hl = ()
    for x in l:
        newt = (hash(frozenset(x)),)
        hl = hl + newt
    return hl

def get_ordindex_for_node(node, data):
    for i,val in data.items():
        if node in val["cn"]:
            return i

def init_graph():
    graph = nx.DiGraph()
    graph.add_edges_from(generate_sequential_edge_list(8))
    graph.add_edges_from(generate_sequential_edge_list(10, prefix="y"))
    graph.add_edges_from([("x8", "d", {"color": "green"}), ("y10", "d", {"color": "green"})])
    return graph

def init_e_graph(j, cn=2):
    graph = nx.DiGraph()
    edge_list = []
    for i in range(1,j+1):
        graph.add_edges_from(generate_triple_u(cn, cn*i, i))
        graph.add_edge("l_"+str(i), "d", color="green")

        graph.add_edges_from(generate_triple_u(cn*i, cn, j+i))
        graph.add_edge("l_"+str(j+i), "d", color="green")
    return graph

def road_until_equal(road1, road2, u):
    for i in range(0, u):
        if road1[i] != road2[i]:
            return False
    return True


def construct_tree(hash_map, data):
    joined_tnodes = {x:list_to_hashset(get_road_of_node(hash_map[x][0], data)) for x in hash_map.keys()}
    tedges = []
    
    for eq_elx in hash_map.keys():
        for eq_ely in hash_map.keys():
            oi_x = len(joined_tnodes[eq_elx])
            if oi_x < len(joined_tnodes[eq_ely]):
                if road_until_equal(joined_tnodes[eq_elx], joined_tnodes[eq_ely], oi_x):
                    tedges.append((eq_elx, eq_ely))

    atree = nx.DiGraph(tedges)
    for node in list(atree.nodes):
        atree.add_edge("road0", node)

    tree = nx.transitive_reduction(atree)

    print(tree.edges)

    fig, ax = plt.subplots()
    fig.set_figwidth(15)
    pos = nx.nx_agraph.graphviz_layout(tree, prog="dot")
    nx.draw(tree, pos)
    nx.draw_networkx_labels(tree, pos=pos)
    
    print("TREE: ", nx.is_tree(tree))
    fig.savefig("tree.png")
    return tree

def get_hashmap(graph, data):
    hashmap = {}
    for x in graph.nodes:
        hsh = hash(list_to_hashset(get_road_of_node(x, data)))
        if hsh not in hashmap.keys():
            hashmap[hsh] = []
        hashmap[hsh].append(x)
    return hashmap

def init_word_graph():
    graph = nx.DiGraph()
    words = ["aaabbaaa", "aab"]
    edges = []

    for i,w in enumerate(words):
        prefix = str(i)+"_"
        prior = prefix+"{}"
        restructed = prefix+w[0]
        edges.append((prior, restructed))
        for c in w[1:]:
            prior = restructed
            restructed += str(c)
            edges.append((prior, restructed))
        #edges.append((restructed, "FINAL"))

    graph.add_edges_from((e[0], e[1], {"color": "green"}) for e in edges)
    return graph

def construct_prefix_tree(tree, hash_map, data):
    h = {}

    for x in hash_map.keys():
        road = list_to_hashset(get_road_of_node(hash_map[x][0], data))
        for component in road:
            if component not in h.keys():
                h[component] = "a"+str(len(h))

    tedges = []
    for i,e in enumerate(tree.edges):
        tedge = ()
        for j in range(0,2):
            v = e[j]
            if v == "road0":
                #empty word
                tedge = tedge + ("{}",)
                continue
            new_v = ""
            for component in list_to_hashset(get_road_of_node(hash_map[v][0], data)):
                new_v += h[component]
            tedge = tedge + (new_v,)
        tedges.append(tedge)

    trie = nx.DiGraph()
    trie.add_edges_from(tedges)
    trie = nx.transitive_reduction(trie)

    fig, ax = plt.subplots()
    fig.set_figwidth(15)
    pos = nx.nx_agraph.graphviz_layout(trie, prog="dot")
    nx.draw(trie, pos)
    nx.draw_networkx_labels(trie, pos=pos)
    
    fig.savefig("trie.png")


def main():
    graph = init_e_graph(2)

    #graph = init_word_graph()

    pos = nx.nx_agraph.graphviz_layout(graph, prog="dot")
    fig, ax = plt.subplots()
    nx.draw(graph, pos=pos)
    nx.draw_networkx_labels(graph, pos=pos)
    fig.savefig("graph.png")

    data = alg(graph.copy(), {}, 0)
    
    
    hashmap = get_hashmap(graph, data)
    print(hashmap)

    #print("road(0_aaa): " + str(get_road_of_node("0_aaa", data)))
    #print("road(1_aab): " + str(get_road_of_node("1_aab", data)))
    
    tree = construct_tree(hashmap, data)
    
    prefix_tree = construct_prefix_tree(tree, hashmap, data)


if __name__ == "__main__":
    sys.exit(main())

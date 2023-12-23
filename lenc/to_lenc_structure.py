import sys
import os
import networkx as nx
import matplotlib.pyplot as plt

def generateGraph(n):
    return nx.DiGraph()

def unravel(s_n, map_to_elements):
    unraveled = []
    for s in s_n:
        unraveled.extend(map_to_elements[s])
    return unraveled

def check_for_paths(s1, s2, g):
    for source in s1:
        for target in s2:
            if g.hasEdge(source, target):
                return True

def get_path(s1,s2,g):
    for source in s1:
        for target in s2:
            if g.hasEdge(source, target):
                return g.edge()


def main ():
    alph_size = 5

    nGr = 10
    a = ["a" + str(i) for i in range(0,nGr)]
    (gg, map_to_elements) = generateGraph(nGr, a)
    g = nx.transitive_closure(gg, reflexive=true)

    hom = {}

    

    s_n = []
    unraveled_s_n = []
    for node,i in enumerate(g.nodes()):
        unraveled_s_n = unravel(s_n, map_to_elements)
        

        # N = 0; INDUKTIONSBEGINN
        if i = 0:
            s_n = [node]
            unraveled_s_n = unravel(s_n, map_to_elements)
            for unraveled in unraveled_s_n:
                hom[unraveled] = ""
            continue
        
        a_i = map_to_elements[node][0]
        a_j = map_to_elements[node][1]

        #FALL 1
        if node in s_n:
            continue

        #FALL 2
        if node not in s_n and not check_for_paths([node], s_n):
            s_n.append(node)
            #FALL 2.a
            if a_i in unraveled_s_n and a_j in unraveled_s_n:
                continue
            else if a_i in unraveled_s_n and a_j not in unraveled_s_n:
                hom[a_j]=hom[a_i]
                continue
            else if a_i not in unraveled_s_n and a_j in unraveled_s_n:
                hom[a_i]=hom[a_j]
                continue
            else if a_i not in unraveled_s_n and a_j not in unraveled_s_n:
                hom[a_i] = ""
                hom[a_j] = ""
                continue

        #FALL 3
        if node not in s_n and check_for_paths([node], s_n):
            s_n.append 

if __name__ == "__main__":
    sys.exit(main())

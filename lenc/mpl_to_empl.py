import networkx as nx
import matplotlib.pyplot as plt

def has_iedge(g,ge,x1,x2,y1,y2):
    #print(x1,x2,y1,y2)
    if not (g.has_node((x1,x2)) or g.has_node((x2,x1)) or g.has_node((y1,y2)) or g.has_node((y2,y1))):
        return False

    #print("l")

    return g.has_edge((x1,x2),(y1,y2)) or g.has_edge((x1,x2),(y2,y1)) or g.has_edge((x2,x1),(y1,y2)) or g.has_edge((x2,x1),(y2,y1))

def has_eq_iedge(gs,g,x1,x2,y1,y2):
    return has_iedge(g,gs,x1,x2,y1,y2) or has_iedge(g,gs,y1,y2,x1,x2)

def has_sm_eq_iedge(g,ge,x1,x2,y1,y2):
    for node in ge.nodes():
        if has_eq_ipath(g,ge,(x1,x2),(node[0],node[1]),20) or node == (x1,x2) or node == (x2,x1):
            if has_iedge(g,ge,node[0],node[1],y1,y2):
                #print("hallo",node)
                return True

    return False

def nextINodes(g,ge,x,n,edge_func):
    inodes = []
    for i in range(0,n):
        inodes.append("a"+str(i))

    next_nodes = []

    for n1 in inodes:
        for n2 in inodes:
            #if n1 == "a7" and n2 == "a8":
                #print("????", x, edge_func(g,ge,x[0],x[1],n1,n2))
            if edge_func(g,ge,x[0],x[1],n1,n2):
                #print("g")
                next_nodes.append((n1,n2))

    return next_nodes 

"""def find_all_ipaths(g,ge,x,y,n, connection_paths,current,edge_func):
    for nn in nextINodes(g,ge,x,n,edge_func):
        if nn == x:
            print("problem?")
        #print(nn)
        if nn == y:
            #print("yes",nn)
            current.append(nn)
            connection_paths.append(current)
        elif nn not in current:
            current.append(nn)
            ncp,nc = find_all_ipaths(g,ge,nn,y,n,connection_paths,current,edge_func)
            #connenction_paths.extend(ncp)
            current.extend()
            current.pop()

    return connection_paths
"""

def find_all_ipaths2(g,ge,x,y,n,path=None,seen=None,edge_func=has_iedge):
    if path is None:
        path = [x]
    if seen is None:
        seen = {x}

    nns = nextINodes(g,ge,x,n,edge_func)
    for nn in nns:
        #print(nn, seen)
        if nn==y or (nn[1],nn[0])==y:
            #print("target reached")
            yield path+[nn]
        else:
            if nn in seen:
                #print("already seen; other nns: ", nns)
                yield path
            else:
                #print("recursion magic")
                seen = seen.union([nn,(nn[1],nn[0])])
                path.append(nn)
                #path.append((nn[1],nn[0]))
                yield from find_all_ipaths2(g,ge,nn,y,n,path,seen,edge_func)

def find_all_ipaths(g,ge,x,y,n,edge_func=has_iedge):
    start_1 = x[0]
    start_2 = x[1]
    end_1=y[0]
    end_2=y[1]
    return filter(lambda path: ((path[0] == (start_1,start_2) or path[0] == (start_2,start_1)) and (path[len(path)-1] == (end_1,end_2) or path[len(path)-1] == (end_2,end_1))),
                    find_all_ipaths2(g,ge,x,y,n,edge_func=edge_func))
 

def mpl(g,ge,x,y,n):
    if not g.has_node((x,y)):
        if g.has_node((y,x)):
            return mpl(g,ge,y,x,n)
        return 0

    all_path_lens = [1]
    for node in g.nodes():
            if has_sm_ipath(g,ge,node,(x,y),n):
                #all_path_lens.extend(map(len, list(nx.all_simple_paths(g,source=node,target=(x,y)))))
                all_path_lens.extend(map(len,find_all_ipaths(g,ge,node,(x,y),n, has_iedge)))

    #print("look",find_all_ipaths(g,("a0","a1"),("a2","a3"),n,[],[]))

    return max(all_path_lens)

def has_eq_ipath(g,ge,x,y,n):
    #return len(list(find_all_ipaths(g,ge,x,y,n,has_eq_iedge))) > 0
    if x not in ge.nodes or y not in ge.nodes:
        return False
    return nx.has_path(ge,x,y)

def has_sm_ipath(gs,ge,x,y,n):
    return len(list(find_all_ipaths(gs,ge,x,y,n,has_iedge))) > 0


def has_smeq_ipath(gs,ge,x,y,n):
    return len(list(find_all_ipaths(gs,ge,x,y,n,has_sm_eq_iedge))) > 0

def empl_helper(gs,ge,x,y,n,rec_list):
    if not gs.has_node((x,y)):
        if gs.has_node((y,x)):
            return empl_helper(gs,ge,y,x,n,rec_list)
        return 0

    #print(rec_list)

    buddies = [mpl(gs,ge,x,y,n)]
    for node in ge.nodes:
        if has_eq_ipath(gs,ge,(x,y),node,n):
            #print(set_map)
            if (node[0],node[1]) in rec_list or (node[1],node[0]) in rec_list:
                #print("hier",(node[0],node[1]))
                buddies.append(mpl(gs,ge,node[0],node[1],n))
                #rec_list.clear()
            else:
                #print("dort",(node[0],node[1]))
                buddies.append(empl(gs,ge,node[0],node[1],n,rec_list))

    pd_delta = [0]
    all_pds = list(gs.predecessors((x,y)))
    if gs.has_node((y,x)):
        all_pds.extend(list(gs.predecessors((y,x))))
    for pd in all_pds:
        pd_delta.append(empl(gs,ge,pd[0],pd[1],n,rec_list) - mpl(gs,ge,pd[0],pd[1],n))

    """for pd in gs.nodes:
        if has_smeq_ipath(gs,ge,pd,(x,y),n):
            pd_delta.append(empl_helper(gs,ge,pd[0],pd[1],n,alr_set) - mpl(gs,ge,pd[0],pd[1],n))"""
    return max(buddies) + max(pd_delta)


def empl(gs,ge,x,y,n,rec_list):
    if not gs.has_node((x,y)):
        if gs.has_node((y,x)):
            return empl(gs,ge,y,x,n,rec_list)
        return 0
    rec_list.append((x,y))
    all_dd = [empl_helper(gs,ge,x,y,n,rec_list)]
    for i in range(0,n):
        if gs.has_node((y,"a"+str(i))):
            if has_smeq_ipath(gs,ge,(x,y),(y,"a"+str(i)),n):
                all_dd.append(empl_helper(gs,ge,x,"a"+str(i),n,rec_list))

    return max(all_dd)

def gen_empl_map(gs,ge,n):
    #init_map = {}
    #for i in range(0,n):
    #    for j in range(0,n):
    #for node in gs.nodes:
    #    init_map[node]=mpl(gs,ge,node[0],node[1],n)

    #print(init_map)

    constr_map = {}
    #for _ in range(0,len(gs.nodes)):
    #for _ in range(0,1):
#        for i in range(0,n):
#            for j in range(0,n):
    for node in gs.nodes:
        constr_map[node] = empl(gs,ge,node[0],node[1],n,[])
        #init_map = constr_map
    return constr_map

def main():
    n = 20
    inodes = []

    for i in range(0,n):
        inodes.append("a"+str(i))

    edges = []
    edges.append((("a0", "a2"),("a2","a3")))
    edges.append((("a5","a6"),("a7","a8")))
    edges.append((("a8","a7"),("a2","a3")))
    edges.append((("a10","a9"),("a6","a5")))

    edges.append((("a15","a16"),("a13","a14")))
    edges.append((("a14","a13"),("a11","a12")))
    edges.append((("a11","a12"),("a0","a3")))

    g = nx.DiGraph()
    g.add_nodes_from([("a0","a2")])
    g.add_edges_from(edges)

    eq_edges_min = [(("a6","a5"),("a2","a0"))]
    sym_eq_edges= [(e[1],e[0]) for e in eq_edges_min]
    sym_eq_edges.extend(eq_edges_min)
    all_eq_edges = []

    for e in sym_eq_edges:
        x=e[0]
        y=e[1]
        all_eq_edges.append(((x[0],x[0]),(y[0],y[1])))
        all_eq_edges.append(((x[1],x[0]),(y[0],y[1])))
        all_eq_edges.append(((x[1],x[0]),(y[1],y[0])))
        all_eq_edges.append(((x[0],x[1]),(y[1],y[0])))

    ge = nx.DiGraph()
    ge.add_nodes_from(g.nodes)
    ge.add_edges_from(all_eq_edges)


    #print("look",list(find_all_ipaths(g,ge,("a0","a1"),("a2","a3"),n)))

    #print(empl(g,ge,"a3","a2",n))
    #print(mpl(g,ge,"a2","a6",n))

    empl_map = gen_empl_map(g,ge,n)

    all_empls = {}
    for node in g.nodes:
        all_empls[node] = [empl_map[node], mpl(g,ge,node[0],node[1],n)]

    fall_empls = {}
    for k,v in all_empls.items():
        if k in fall_empls or (k[1],k[0]) in fall_empls:
            continue
        fall_empls[k] = v

    print(g.edges)
    print(ge.edges)

    print("{:<15} {:<8} {:<8}".format('node','EMPL', "MPL"))
    for k, v in fall_empls.items():
        print("{:<15} {:<8} {:<8}".format("("+",".join(k)+")", v[0], v[1]))

    print(list(find_all_ipaths(g,ge,("a5","a6"),("a2","a3"),n,has_iedge)))
    #print(has_smeq_ipath(g,ge,("a0","a1"),("a2","a3"),n))
    #print(has_sm_eq_iedge(g,ge,"a5","a6","a7","a8"))


if __name__ == "__main__":
    main()

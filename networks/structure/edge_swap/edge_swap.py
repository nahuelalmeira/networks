def doubleEdgeSwap(G, nswap=1, max_tries=100):
    """Swap two edges in the graph while keeping the node degrees fixed.
    A double-edge swap removes two randomly chosen edges u-v and x-y
    and creates the new edges u-x and v-y::
     u--v            u  v
            becomes  |  |
     x--y            x  y
    If either the edge u-x or v-y already exist no swap is performed
    and another attempt is made to find a suitable edge pair.
    Swapping is made IN PLACE
    
    Parameters
    ----------
    (ig.Graph) G : An undirected graph
    (int) nswap : Number of double-edge swaps to perform (default=1)
       
    (int) max_tries : Maximum number of attempts to swap edges
                     (default=None)
       
       
    Returns
    -------
    G : (ig.Graph) The graph after double edge swaps.
       
    Notes
    -----
    Does not enforce any connectivity constraints.
    The graph G is modified in place.
    """
    
    assert not G.is_directed(), ('double_edge_swap() not defined for '
                                 'directed graphs.')
    assert nswap <= max_tries, 'Number of swaps > number of tries allowed.'
    
    N = G.vcount()
    assert N >= 4, 'Graph has less than four nodes.'
    
    if not max_tries:
        max_tries = 100*nswap
    
    # Instead of choosing uniformly at random from a generated edge list,
    # this algorithm chooses nonuniformly from the set of nodes with
    # probability weighted by degree.
    n = 0
    swapcount = 0
    degrees_list = [(i,  G.vs[i].degree()) for i in range(N)]
    degrees_list = sorted(degrees_list, key=lambda x: x[1])
    keys, degrees = zip(*degrees_list) # keys, degree
    cdf = nx.utils.cumulative_distribution(degrees)  # cdf of degree

    while swapcount < nswap:
        # pick two random edges without creating edge list
        # choose source node indices from discrete distribution
        ui, xi = nx.utils.discrete_sequence(2, cdistribution = cdf)

        if ui == xi:
            continue # same source, skip
        
        u = keys[ui] # convert index to label
        x = keys[xi]

        # choose target uniformly from neighbors
        u_nn = {node.index for node in G.vs[u].neighbors()}
        x_nn = {node.index for node in G.vs[x].neighbors()}
        v = random.sample(u_nn, 1)[0]
        y = random.sample(x_nn, 1)[0]
        v_nn = {node.index for node in G.vs[v].neighbors()}
        
        if v == y:
            continue # same target, skip
        
        if (x not in u_nn) and (y not in v_nn): # don't create parallel edges
            G.add_edges([(u, x), (v, y)])
            e1 = G.get_eid(u, v)
            e2 = G.get_eid(x, y)
            G.delete_edges([e1, e2])
            swapcount += 1
            
        assert n < max_tries, ('Maximum number of swap attempts '
                               '(%s) exceeded ' % n + 'before desired '
                               'swaps achieved (%s).' % nswap)
        n += 1
    return G

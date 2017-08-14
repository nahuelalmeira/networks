def mba_attack(graph, output_file, algorithm='louvain'):
    '''Ataque similar al propuesto por da Cunha et. al., pero no chequea
    que los nodos a remover pertenezcan a la componente gigante'''
        
    ## Si el archivo existe, no hago nada
    if os.path.isfile(output_file):
        print("El archivo " + output_file + " ya existe.")
        return     
    
    g = graph.copy()
    n = g.vcount()
    g.vs["betweenness"] = g.betweenness(directed=False)
    g.vs["original_index"]  = range(0, n)
    
    if algorithm == 'louvain':
        communities = g.community_multilevel()
    elif algorithm == 'infomap':
        communities = g.community_infomap()
    else:
        print('Algorithm must be "louvain" or "infomap"')
        return

    bridges_indices = [i for i, e in enumerate(communities.crossing()) if e]
    bridges = g.es().select(bridges_indices)
    
    bridging_vertices_set = set([])
    for e in bridges:
        bridging_vertices_set.add(e.source)
        bridging_vertices_set.add(e.target)  
        
    bridging_vertices = g.vs().select(bridging_vertices_set)
    bridging_vertices = sorted(bridging_vertices, 
                               key=lambda v: v['betweenness'], reverse=True)

    original_indices = [v['original_index'] for v in bridging_vertices]
    
    nn_sets = []
    for original_index in original_indices:
        nn = g.vs()[original_index].neighbors()
        nn_set = set([v.index for v in nn])
        nn_sets.append(nn_set.intersection(bridging_vertices_set))      
        
    with open(output_file, 'w') as f:
        j = 0
        while original_indices:
            
            giant = g.clusters(mode='WEAK').giant()
            for i, original_index in enumerate(original_indices):
                
                if original_index in giant.vs()['original_index']:
                    
                    
                    index = g.vs()['original_index'].index(original_index)
                    if nn_sets[i]:    

                        num_comp, num_edges, first, second, mean_small_orders = getComponentsOrders(g)
                        f.write("%d\t%d\t%d\t%d\t%d\t%d\t%d\t" % (j, index, g.vs[index]['betweenness'], 
                                                              original_index,
                                                              g.vs[index]['betweenness'],
                                                              num_comp, num_edges))
                        f.write("%d\t%d\t%f\n" % (first, second, mean_small_orders))
                        g.vs[index].delete()
                        j += 1
                        original_indices.remove(original_index)
                        for nn_set in nn_sets:
                            if index in nn_set:
                                nn_set.remove(index)
                        break
                       
                elif i == len(original_indices) - 1:
                    return
    return

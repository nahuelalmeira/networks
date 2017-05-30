import os
import pickle
import numpy as np

try:
    from itertools import accumulate
except ImportError:
    import operator

    # The code for this function is from the Python 3.5 documentation,
    # distributed under the PSF license:
    # <https://docs.python.org/3.5/library/itertools.html#itertools.accumulate>
    def accumulate(iterable, func=operator.add):
        it = iter(iterable)
        try:
            total = next(it)
        except StopIteration:
            return
        yield total
        for element in it:
            total = func(total, element)
            yield total

def richClubCoefficient(G, normalized='vl', Q=100):
    r"""Returns the rich-club coefficient of the graph `G`.
    For each degree *k*, the *rich-club coefficient* is the ratio of the
    number of actual to the number of potential edges for nodes with
    degree greater than *k*:
    .. math::
        \phi(k) = \frac{2 E_k}{N_k (N_k - 1)}
    where `N_k` is the number of nodes with degree larger than *k*, and
    `E_k` is the number of edges among those nodes.
    
    Parameters:
    -----------
    (igraph.Graph) G: undirected simple graph
    (str) normalized: whether the coefficient will be normalized by
                      using a random graph.
                      'vl': Fabien-Viger (default)
                      'rewire': edge swapping (iGraph implementation)
                      'swap': edge swapping (my implementation)

    Returns:
    --------
    (dict) rc: dictionary, keyed by degree, with rich-club coefficient 
           values.
           
    Examples
    --------
    >>> G = ig.Graph([(0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (4, 5)])
    >>> rc = rich_club_coefficient_ig(G, normalized=False)
    >>> rc[0]
    0.4
    
    Notes
    -----
    The rich club definition and algorithm are found in [1]_.  This
    algorithm ignores any edge weights and is not defined for directed
    graphs or graphs with parallel edges or self loops.
    Estimates for appropriate values of `Q` are found in [2]_.
    
    References
    ----------
    .. [1] V. Colizza, A. Flammini, M. A. Serrano and A. Vespignani,
       "Detecting rich-club ordering in complex networks", 2006. 
       https://arxiv.org/abs/physics/0602134
    .. [2] R. Milo, N. Kashtan, S. Itzkovitz, M. E. J. Newman, U. Alon,
       "Uniform generation of random graphs with arbitrary degree
       sequences", 2006. http://arxiv.org/abs/cond-mat/0312028
    """
    
    if not G.is_simple():
        raise Exception('rich_club_coefficient is not implemented for '
                        'graphs with self loops.')
        
    rc = _computeRC(G)
    if normalized:
        # make R a copy of G
        
        if normalized == 'rewire':
            # randomize with Q*|E| double edge swaps
            # and use rich_club coefficient of R to normalize
            R = G.copy()
            E = R.ecount()
            R.rewire(n=Q*E)
        elif normalized == 'swap':
            assert False, 'TODO: implement swapping in rich club'
        elif normalized == 'vl':
            # generate a random graph with the same degree 
            # sequence using the Fabien-Viger algorithm
            R = ig.Graph().Degree_Sequence(G.degree(), method='vl')
        else:
            assert False, 'Unknown normalization.'
            
        rcran = _computeRC(R)
        #rc = {k: v / rcran[k] for k, v in rc.items()}
        rc = {k: v / rcran[k] for k, v in rc.items() if rcran[k] != 0}
    return rc

def getDegreeHistogram(g):
    deg_seq = g.degree()
    deg_hist = {i: 0 for i in xrange(max(deg_seq) + 1)}
    for k in deg_seq:
        deg_hist[k] += 1
    deg_tuples = sorted(deg_hist.items(), key=lambda x: x[0])
    return zip(*deg_tuples)[1]

def _computeRC(G):
    """Returns the rich-club coefficient for each degree in the graph
    `G`. `G` is an undirected graph without multiedges.
    Returns a dictionary mapping degree to rich-club coefficient for
    that degree.
    """
    
    deghist = getDegreeHistogram(G)
    total = sum(deghist)
    # Compute the number of nodes with degree greater than `k`, for each
    # degree `k` (omitting the last entry, which is zero).
    nks = (total - cs for cs in accumulate(deghist) if total - cs > 1)
    # Create a sorted list of pairs of edge endpoint degrees.
    #
    # The list is sorted in reverse order so that we can pop from the
    # right side of the list later, instead of popping from the left
    # side of the list, which would have a linear time cost.
    edge_degrees = sorted((sorted(map(lambda v: G.vs[v].degree(), e.tuple)) 
                           for e in G.es()), reverse=True)

    ek = G.ecount()
    k1, k2 = edge_degrees.pop()
    rc = {}
    for d, nk in enumerate(nks):
        while k1 <= d:
            if len(edge_degrees) == 0:
                ek = 0
                break
            k1, k2 = edge_degrees.pop()
            ek -= 1
        rc[d] = 2 * ek / (nk * (nk - 1))
    return rc

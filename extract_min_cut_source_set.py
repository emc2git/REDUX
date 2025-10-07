# -*- coding: utf-8 -*-
"""
Created on Sat Mar  8 08:23:28 2025

This file is called by kclosures AND sub_problem_solver
This file contains the following functions:
    extract_min_cut_source_set: this function take a networkX residual graph and returns the source set (that is, the set of vertices that are reachable by the source node)
    

@author: andre
"""

#INPUT: graphA: a networkX residual graph
#OUTPUT: source_set: a set object containing the vertices reachable by the source node (e.g. the source set of the minimum-cut solution)

def extract_min_cut_source_set(graphA):
    
    nodes = list(graphA.nodes())
    nodes.sort()
    nodes_visited = dict(map(lambda key: (key, False),nodes))
    source = min(graphA.nodes())
    source_set = {source}
    queue = [source]
    while queue:
        j = queue.pop(0)
        children = list(graphA.successors(j))
        for child in children:
            if graphA.get_edge_data(j,child)['capacity'] > graphA.get_edge_data(j,child)['flow']:
                if nodes_visited[child] == False:
                    queue.append(child)
                    source_set.add(child)
                nodes_visited[child] = True
    return source_set



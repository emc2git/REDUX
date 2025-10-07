# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 16:22:00 2025
This file is called be kclosures
This file contains the following functions:
    picard: this function takes a networkx directed graph and transforms it into its corresponding Picard transformed graph

@author: andre
"""
import networkx as nx

#INPUT: DirGraph (a directed graph networkX object that contains node weight ('capacity' values in the networkX graph object))
#OUTPUT: DirGraph (the Picard transformation of the original directed graph)
def picard(DirGraph):
    # Add weight of infinity to each edge
    nx.set_edge_attributes(DirGraph, float('inf'), 'capacity')
    # Add node s (source) as node 0 and t (terminal) as node n+1
    DirGraph.add_node(len(list(DirGraph.nodes()))+1)
    DirGraph.add_node(0)
    # Connect the source node (node 0) to each positive weight node and make the arc the weight of the node; 
    # Connect each negative weight node to the terminal node (node n+1) and make the arc weight the absolute value of the node weight
    for i in range(len(list(DirGraph.nodes()))-2):
        wt = DirGraph.nodes[list(DirGraph.nodes)[i]]['capacity']*1e8
        if wt > 0:
            DirGraph.add_edge(0,list(DirGraph.nodes)[i], capacity = wt)
        if wt < 0:
            DirGraph.add_edge(list(DirGraph.nodes)[i],len(list(DirGraph.nodes()))-1, capacity = -1*wt)
    return DirGraph
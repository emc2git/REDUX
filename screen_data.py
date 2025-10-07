# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 16:18:09 2025
This file is called by kclosures
This file contains the following function:
    prescreen: this function takes and adjacency dictionary and list of node weights and checks to make sure there are no critical errors in the file.
    Then, it produces a networkx graph object. It then puts the graph on topological order and produces a mapping dictionary that can be used to put
    the graph back in the original vertex order.
@author: andre
"""
import networkx as nx
#INPUT: Adjacency dictionary and node weight list
#OUTPUT: networkx directed graph with node weights and a vertex mapping dictionary (used to reconstruct original graph after it is topologically sorted)

def prescreen(adjacency_dict, node_weights):
    try: #First, create DG, the directed graph object (if invalid adjacency dictionary input, throw an error)
        DG = nx.DiGraph(adjacency_dict)
    except TypeError:
        print("Input entry error: invalid adjacency dictionary")
        return True
    cycles = list(nx.simple_cycles(DG))
    if cycles: #Test for a cycle - if one or more exist, then it is an invalid graph
        print("Input entry error: cycle(s) detected ->", cycles)
        print("Cannot determine closure when cycles exist")
        return True 
    for i in range(len(node_weights)): #Add node weights to the graph
        if DG.has_node(node_weights[i][0]):
            DG.nodes[node_weights[i][0]]['capacity'] = node_weights[i][1]
        else: 
            DG.add_node(node_weights[i][0])
            DG.nodes[node_weights[i][0]]['capacity'] = node_weights[i][1]
    for i in range(min(list(adjacency_dict.keys())),max(list(adjacency_dict.keys()))+1):
        try:  #Check to make sure each node has a respective weight assigned to it
            DG.nodes()[i]['capacity']
        except KeyError:
            print("Input entry error: missing node weight")
            return True
    topo_nodes = list(nx.topological_sort(DG)) #Generate the topological order of the graph
    mapping = {node: i for i, node in enumerate(topo_nodes)} #Create the mapping dictionary
    for i in mapping: #Increase each node number by 1 to reflect correct graph mapping
        mapping[i] += 1
    DG = nx.relabel_nodes(DG, mapping) #Use the mapping dictionary to relabel the graph nodes 
    return DG, mapping


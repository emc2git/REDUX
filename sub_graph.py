# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 16:31:36 2025
     This file is called by sub_problem_solver and used to manipulate REDUX graphs before solving
     It includes the following functions:
         subgraph_res: this function updates the residual graph for REDUX in accordance with which nodes must be fixed. It outputs a new residual graph (networkx object) and a list of dictionary items containing information about the nodes/arcs that were changed.
         subgraph_res_revert: this function changes the residual graph back to what it was given what was changed in subgraph_res

@author: andre
"""

#INPUT: In_Out: a dictionary containing which vertices are fixed to 1 and which vertices are fixed to 0; G_res: a networkx residual graph
#OUTPUT: G_res: a networkx residual graph, nodes_removed_info: a list object containing dictionary items with information about which nodes and edges were changed from the inputted residual graph
def subgraph_res(In_Out, G_res):
    nodes_removed_info = [] #List to store information about the nodes "removed" from the residual graph
    for i in In_Out['IN']:
        edges = list(G_res.in_edges(i))
        edge_cap = []
        edge_flow = []
        for edge in edges:
            edge_cap.append(G_res.edges[edge]['capacity'])
            edge_flow.append(G_res.edges[edge]['flow'])
            G_res.add_edge(edge[0], edge[1], capacity = 0, flow = 0)
        nodes_removed_info.append({'Node': i, 'Edges': edges, 'Edge Cap': edge_cap, 'Edge Flow': edge_flow})
    for i in In_Out['OUT']:
        edges = list(G_res.in_edges(i))
        edge_cap = []
        edge_flow = []
        for edge in edges:
            edge_cap.append(G_res.edges[edge]['capacity'])
            edge_flow.append(G_res.edges[edge]['flow'])
            G_res.add_edge(edge[0], edge[1], capacity = 0, flow = 0)
        nodes_removed_info.append({'Node': i, 'Edges': edges, 'Edge Cap': edge_cap, 'Edge Flow': edge_flow})
    return G_res, nodes_removed_info

#INPUT: G_res: a networkx residual graph; nodes_removed_info: a list object containing dictionary items with information about which nodes/edges need to be changed back to get the original residual graph
#OUTPUT: G_res: a networkx residual graph
def subgraph_res_revert(G_res, nodes_removed_info):
    for i in range(len(nodes_removed_info)):
        for j in range(len(nodes_removed_info[i]['Edges'])):
            edge = nodes_removed_info[i]['Edges'][j]
            edge_cap = nodes_removed_info[i]['Edge Cap'][j]
            edge_flow = nodes_removed_info[i]['Edge Flow'][j]
            G_res.add_edge(edge[0],edge[1], capacity = edge_cap, flow = edge_flow)   
    return G_res

'''
Old functions that were used ---- these are less efficient with networkx

def subgraph_new(In_Out, G_ST):
    nodes_removed_info = []
    for i in In_Out['IN']:
        node_cap = G_ST.nodes[i]['capacity']
        edges = list(G_ST.out_edges(i)) 
        edges.extend(list(G_ST.in_edges(i)))  
        edge_cap = []
        for edge in edges:
            edge_cap.append(G_ST.edges[edge]['capacity'])
        nodes_removed_info.append({'Node': i, 'Node Cap': node_cap, 'Edges': edges, 'Edge Cap': edge_cap})
        G_ST.remove_node(i)
    for i in In_Out['OUT']:
        node_cap = G_ST.nodes[i]['capacity']
        edges = list(G_ST.out_edges(i)) 
        edges.extend(list(G_ST.in_edges(i)))  
        edge_cap = []
        for edge in edges:
            edge_cap.append(G_ST.edges[edge]['capacity'])
        nodes_removed_info.append({'Node': i, 'Node Cap': node_cap, 'Edges': edges, 'Edge Cap': edge_cap}) 
        G_ST.remove_node(i)
    return G_ST, nodes_removed_info

def subgraph_revert(G_ST, nodes_removed_info):
    for i in range(len(nodes_removed_info)):
        G_ST.add_node(nodes_removed_info[i]['Node'], capacity = nodes_removed_info[i]['Node Cap'])
        for j in range(len(nodes_removed_info[i]['Edges'])):
            edge = nodes_removed_info[i]['Edges'][j]
            edge_cap = nodes_removed_info[i]['Edge Cap'][j]
            G_ST.add_edge(edge[0],edge[1], capacity = edge_cap )   
    return G_ST

'''
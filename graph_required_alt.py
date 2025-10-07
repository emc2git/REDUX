# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 16:48:22 2025
This file is called by sub_problem_solver and used to manipulate ML (BASIC) graphs before solving
It includes the following functions:
    G_req: this function updates the residual graph for BASIC (ML) in accordance with which nodes must be fixed. It outputs a new residual graph (networkx object) and a list of dictionary items containing information about the nodes/arcs that were changed.
    G_revert_back: this function changes the residual graph back to what it was given what was changed in G_req
@author: andre
"""

#INPUT: in_out_list: a dictionary object that contains a list of nodes that must be included in the closure and a list of nodes that must not be included, G_ST: Picard transformation of the directed graph
#OUTPUT: Graph: a networkx graph that has been adjusted based on the nodes that must be in the closure and the nodes that must not be in the closure
#Note - this routine must be different than the SG (subgraph) routine of the reduction method since we do not eliminate or require the nodes that must be in or out based on the fixed variables.


#INPUT: in_out: a dictionary containing which vertices are fixed to 1 and which vertices are fixed to 0; G_res: a networkx residual graph
#OUTPUT: G_res: a networkx residual graph, nodes_removed_info: a list object containing dictionary items with information about which nodes and edges were changed from the inputted residual graph
def G_req(in_out_list, G_res):
    nodes_in = in_out_list['IN']
    nodes_out = in_out_list['OUT']
    min_node = min(G_res.nodes())
    max_node = max(G_res.nodes())
    adjusted_edges = []
    for i in range(len(nodes_in)): #If a node must be included, then we update the capacity from soure to node to "inf"; if it does not already exist, we add both the arc with infinite capcity and its corresponding residual with capacity and flow = 0.   
        edge = (min_node, nodes_in[i])
        try:
            edge_cap = G_res.edges[edge]['capacity']
            edge_flow = G_res.edges[edge]['flow']
            G_res.add_edge(edge[0], edge[1], capacity = G_res.graph['inf'])
            adjusted_edges.append({"edge": edge, "cap": edge_cap, "flow": edge_flow, "res cap": 0, "res flow": -1*edge_flow})
        except KeyError:
            edge_cap = 0
            edge_flow = 0
            G_res.add_edge(edge[0], edge[1], capacity = G_res.graph['inf'], flow = 0)
            G_res.add_edge(edge[1], edge[0], capacity = 0, flow = 0)
            adjusted_edges.append({"edge": edge, "cap": edge_cap, "flow": edge_flow, "res cap": 0, "res flow": -1*edge_flow})
    for j in range(len(nodes_out)): #If a node must be excluded, then we update the capacity from node to terminal to "inf"; if it does not already exist, we add both the arc with infinite capcity and its corresponding residual with capacity and flow = 0.   
        edge = (nodes_out[j], max_node)
        try:
            edge_cap = G_res.edges[edge]['capacity']
            edge_flow = G_res.edges[edge]['flow']
            G_res.add_edge(edge[0], edge[1], capacity = G_res.graph['inf'])
            adjusted_edges.append({"edge": edge, "cap": edge_cap, "flow": edge_flow, "res cap": 0, "res flow": -1*edge_flow})
        except KeyError:
            edge_cap = 0
            edge_flow = 0
            G_res.add_edge(edge[0], edge[1], capacity = G_res.graph['inf'], flow = 0)
            G_res.add_edge(edge[1], edge[0], capacity = 0, flow = 0)
            adjusted_edges.append({"edge": edge, "cap": edge_cap, "flow": edge_flow, "res cap": 0, "res flow": -1*edge_flow})
    return G_res, adjusted_edges

#INPUT: G_res: a networkx residual graph; adjusted_edges: a list object containing dictionary items with information about which nodes/edges need to be changed back to get the original residual graph
#OUTPUT: G_res: a networkx residual graph
def G_revert_back(adjusted_edges, G_res):
    for i in range(len(adjusted_edges)):
        edge = adjusted_edges[i]["edge"]
        G_res.add_edge(edge[0],edge[1], capacity = adjusted_edges[i]["cap"], flow = adjusted_edges[i]["flow"])
        G_res.add_edge(edge[1],edge[0], capacity = adjusted_edges[i]["res cap"], flow = adjusted_edges[i]["res flow"])
    return G_res



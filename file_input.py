# -*- coding: utf-8 -*-
"""
This file is called by kclosures
This file contains the following function:
    file_input: it takes a prec and upit file (files formatted IAW prec and upit files from MineLib:https://mansci-web.uai.cl/minelib/Datasets.xhtml) and produces a dictionary object with the adjacency list and a list obect with the node weights.
    
"""
#INPUT: prec (precedence file entered as a 'string' - uses MineLib data format: https://mansci-web.uai.cl/minelib/Datasets.xhtml), upit (upit file contains node weights - MineLib file)
#OUTPUT: adjacency dictionary, and node weight list 
   
def file_input(prec, upit): 
    file_prec = prec
    file_upit = upit
    with open(file_prec,'r') as file: #Read in the precedence list
        lines = file.readlines() 
        lines = [line.strip() for line in lines]
    for i in range(len(lines)):
        lines[i] = lines[i].split()
        for j in range(len(lines[i])):
            lines[i][j] = int(lines[i][j])+1 #We increase each value by one so that we start with a node "1" instead of node "0"
    adjacency_dict = {}
    #Fill the adjacency dictionary such that the key represents is the first value in the list
    for i in range(len(lines)):
        node = lines[i][0] #The first value in the list is the key for the adjacency list
        if lines[i][1] > 1:
            temp_list = lines[i][2:]
            adjacency_dict[node] = tuple(temp_list)
        
    #Read in the node weights data and convert to a list of tuples
    with open(file_upit, 'r') as file:
        node_weights = file.readlines()
        del node_weights[:4]
        for i in range(len(node_weights)):
            node_weights[i] = node_weights[i].split()
            node_weights[i][0] = int(node_weights[i][0])+1
            node_weights[i][1] = float(node_weights[i][1])
            node_weights[i] = tuple(node_weights[i])
    return adjacency_dict, node_weights

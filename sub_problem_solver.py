# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 09:46:21 2025


This file is called by kclosures

It includes the following functions: 
    subproblems: produces a python dictionary that contains all reduced problems per the M-L framework
    in_out_func: produces a python dictionary that has lists of variables that must be fixed in the closure and variable that must be fixed out of the closure
    sub_problem_solver: this function solves all reduced problems and outputs a python dictionary with all solutions to the set of reduced problems (note: it also generates numbers that give times to solve and numbers of infeasible reduced problems) 

@author: andre
"""
import sub_graph as sg
import graph_required_alt as gr
import binary_solution as bs
import time
from networkx.algorithms.flow import shortest_augmenting_path
import extract_min_cut_source_set as emc
import closure_value as cv
import networkx as nx

#INPUT: sol_vec (the binary solution vector that results from the optimal solution as a list object
#OUTPUT: sp_dictionary (the dictionary object containing all initial sub-problems)
def subproblems(sol_vec): 
    #Create the sub-problems
    sp_dictionary = {} #Empty dictionary to store the sub-problems
    for i in range(1,len(sol_vec)+1):
        new_prob = sol_vec[0:i] #extract the optimal solution variables from 0 to i
        new_prob[i-1] = 1-new_prob[i-1] #the last element of the sub-problem is changed from the optimal solution
        sp_dictionary[i] =  new_prob #add the new sub-problem to the dictionary 
        sp_dictionary[i].extend([None]*(len(sol_vec)-i))
    return sp_dictionary

#INPUT: sub_prob_list: the sub problem is a list of 1's and 0's indicating which nodes must be included in the closure and which nodes must not be included
#OUTPUT: a dictionary that contains the a list of the nodes that must be in the closure and a list of the nodes that must not be in the closure
def in_out_func(sub_prob_list):
    IN = [] #Empty list to store nodes that must be "IN" the closure
    OUT = [] #Empty list to store nodes that must be "OUT" of the closure
    for i in range(len(sub_prob_list)):
        if sub_prob_list[i] == 1: #If the input list is a 1, then the corresponding index+1 is the node that is in the closure
            IN.append(i+1)
        if sub_prob_list[i] == 0: #If the input is is a 0, then the corresponding index+1 is the node that is not in the closure
            OUT.append(i+1)
    in_out_list = {"IN":IN, "OUT":OUT}
    return in_out_list

#INPUT: branch_num: a string designating the branch number of the previous best solution, sp_dictionary: a dictionary containing all reduced problems, G_R: networkx residual graph, G_ST: networkx Picard transformed graph, method: string that is either "REDUX" or "ML" designating which algorithm to use
#OUTPUT: a dictionary containing all solved reduced problems AND various time stamp data and number of infeasible problem data
def sub_problem_solver(branch_num, sp_dictionary, G_R, G_ST_node_data, method):
    solutions_dict = [] #create a list that we will populate with dictionaries
    sub_problems = list(sp_dictionary.keys()) # pull out the list of all sub-problems
    string_part = str(branch_num) + "_" #this string will help keep track of the sub-problem keys and branches for the dictionary
    tot_solve_time = 0 #set total time to 0 - this is where we will update the total time used to extract min-cut solution from the residual graph
    gr_adj_time_tot = 0
    gr_revert_time_tot = 0
    infeasible_time_tot = 0
    tot_time_extract_min_cut = 0
    num_infeasible_sols = 0
    for i in range(len(sp_dictionary)): #cycle through each sub-problem to find the optimal solution
        sub_prob_list = sp_dictionary[sub_problems[i]] #Pull out the sub problem from the sub problem dictionary
        in_out_list = in_out_func(sub_prob_list) #Identify which solution variables need to be included and which ones do not need to be included
        gr_adj_time_start = time.time()
        if method == "REDUX":
            G_res, adjusted_edges = sg.subgraph_res(in_out_list, G_R)
        if method == "ML":
            G_res, adjusted_edges = gr.G_req(in_out_list, G_R)
        gr_adj_time_end = time.time()
        gr_adj_time_tot = gr_adj_time_tot + gr_adj_time_end - gr_adj_time_start
        feasible = True #Set feasibility to "True" - this variable will turn "False" if the flow is infinite
        #This try-except structure is to deal with unbounded paths (in which case, there is not a feasible solution)
        time_to_extract_min_cut = 0
        extract_time_start = 0
        extract_time_end = 0
        solve_time_start = time.time()
        try:
            ### Solve for the subproblem using the updated Graph object and the updated residual graph (G_res)
            ### We use shortest_augmenting_path due to networkx algorithm error associated with preflow_push: https://github.com/networkx/networkx/discussions/7868 
            #sol3_PFP = preflow_push(Graph,0,len(G_ST.nodes())-1)
            #sol3_SAP = shortest_augmenting_path(Graph,0,len(G_ST.nodes())-1, residual = G_res) #Solve for the residual graph using maximum flow
            sol3_SAP = shortest_augmenting_path(G_res, 0, len(G_ST_node_data)-1, residual = G_res)
            #sol3_EK = edmonds_karp(Graph,0,len(G_ST.nodes())-1)  
            extract_time_start = time.time() #Initial time for starting min-cut extraction
            included = emc.extract_min_cut_source_set(sol3_SAP)
            if method == "REDUX":
                included.update(in_out_list['IN']) 
            excluded = [0]*(len(sol3_SAP.nodes())-len(included))
            sol = (None,(included,excluded)) #Create the solution object (note: this format matches of the format produced by networkx "minimum_cut" function)
            extract_time_end = time.time() #time stamp for finishing the min-cut extraction process
            solve_time_end = time.time()
            time_to_extract_min_cut = extract_time_end - extract_time_start #comput time to extract the minimum cut solution from the residual graph
            tot_time_extract_min_cut = tot_time_extract_min_cut + time_to_extract_min_cut
            tot_solve_time = tot_solve_time + solve_time_end - solve_time_start - time_to_extract_min_cut
        except nx.NetworkXUnbounded:
            infeasible_end_time = time.time()
            feasible = False #Change feasible to "False" if network has unbounded flow
            infeasible_time = infeasible_end_time - solve_time_start
            infeasible_time_tot = infeasible_time_tot + infeasible_time 
            num_infeasible_sols = num_infeasible_sols + 1
        if feasible == True: #If we get a solution, we do the following:
            sol_vector = bs.binary_sol_vector(sol) #create a binary solution vector
            val = cv.closure_value(sol_vector, G_ST_node_data)
            num_part = sub_problems[i] #create the numbered part for the dictionary
            branch = string_part + str(num_part) #put the string and number part together to create "p_r" for the dictionary key
            key = sub_problems[i] #we will use the sub-problem number as the dictionary key        
            if method == "REDUX":    
                num_nodes = G_res.number_of_nodes() - (len(in_out_list['IN'])+len(in_out_list['OUT']))
            if method == "ML":
                num_nodes = G_res.number_of_nodes()
            solutions_dict.append({"Branch": branch, "Sub Problem": key, "Value": val, "Solution": sol_vector, "Residual Graph": sol3_SAP, "Num Nodes in SG": num_nodes}) #add the solution dictionary to the solution list
        gr_revert_time_start = time.time()
        if method == "REDUX":
            G_res = sg.subgraph_res_revert(G_res, adjusted_edges) #Reset G_res
        if method == "ML":
            G_res = gr.G_revert_back(adjusted_edges, G_res)
        gr_revert_time_end = time.time()
        gr_revert_time_tot = gr_revert_time_tot + gr_revert_time_end - gr_revert_time_start
    return solutions_dict, tot_solve_time, tot_time_extract_min_cut, gr_adj_time_tot, gr_revert_time_tot, infeasible_time_tot, num_infeasible_sols

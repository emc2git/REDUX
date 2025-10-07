# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 09:25:37 2025

This file is the primary executable file for both REDUX and BASIC algorithms to compute the k-best closures

INPUT: See arguments below
OUTPUT: a dictionary having the k best closure solutions and json files will be written that provide the kbest list and, if desired, a json file containing all candidate solutions 

To find k-best closures using this file, do the following:
    import kclosures as kc
    kc.solve(K, prec, upit, filename, method, write_sol_file)
    
Arguments for solve function:
    K: any positive integer
    prec: a string that is the name of the precedence file (this file will contain the precedence relationships between vertices)
    upit: a string that is the name of upit file (this file will contain the weights for each vertex)
    filename: a string that is the title you want all of the output files to have
    method: a string that must be either "REDUX" or "ML" (note - "ML" corresponds to the BASIC algorithm)
    write_sol_file: boolean (True or False) - if True, the master file (file containing all candidate solutions) will be written


@author: andre
"""

import time
import json
from networkx.algorithms.flow import shortest_augmenting_path

#Custom modules
import file_input as ip
import screen_data as sd
import picard_transform as pt
import binary_solution as bs
import next_best as nb
import reduce3 as redux3
import extract_min_cut_source_set as emc
import closure_value as cv
import sub_problem_solver as sps


##################### SOLVE FUNCTION #####################################
##INPUT:
#K: any positive integer
#prec: a string that is the name of the precedence file (this file will contain the precedence relationships between vertices)
#upit: a string that is the name of upit file (this file will contain the weights for each vertex)
#filename: a string that is the title you want all of the output files to have
#method: a string that must be either "REDUX" or "ML" (note - "ML" corresponds to the BASIC algorithm)
#write_sol_file: boolean (True or False) - if True, the master file (file containing all candidate solutions) will be written

def solve(K, prec, upit, filename, method, write_sol_file): #method takes either "REDUX" or "ML"; write_sol_file take either "True" or "False"
    overall_time_start = time.time()
    filename = filename + method + '.json'
    input_data_time_start = time.time()
    if method != "REDUX" and method != "ML":
        print("Incorrect method entry; method must be 'REDUX' or 'ML'")
        return
    input_info = ip.file_input(prec, upit)
    adjacency_dict = input_info[0]
    node_weights = input_info[1]
    Graph_with_map = sd.prescreen(adjacency_dict, node_weights) #generate the topologically sorted DAG 
    DG = Graph_with_map[0] #assign DG as the DAG
    mapping = Graph_with_map[1] #retrieve the mapping dictionary
    if DG == True:
        return
    master_list = [] #We create a master list that will store all of the solutions created for each sub-problem solved
    k_best_list = [] #This list will be where we store the k best solutions
    G_ST = pt.picard(DG.copy()) #Transform the inputted directed graph from a directed graph to a directed graph with source and terminal node using Picard transformation
    G_ST_node_data = dict(list(G_ST.nodes.data('capacity')))
    input_data_time_end = time.time()
    input_data_time = input_data_time_end - input_data_time_start
    solve_time_start = time.time()
    opt_sol_R = shortest_augmenting_path(G_ST,min(G_ST.nodes()),max(G_ST.nodes())) #Residual graph of optimal solution
    solve_time_end = time.time()
    solve_time = solve_time_end - solve_time_start
    emc_start = time.time()
    included = emc.extract_min_cut_source_set(opt_sol_R)
    excluded = [0]*(len(opt_sol_R.nodes())-len(included))
    opt_sol = (None,(included,excluded)) #Create the solution object (note: this format matches of the format produced by networkx "minimum_cut" function)
    emc_end = time.time()
    tot_emc = emc_end - emc_start
    binary_sol_time_start = time.time()
    sol_vector = bs.binary_sol_vector(opt_sol) #transform the optimal solution given by the networkx package to a binary soluion vector for the closure problem
    binary_sol_time_end = time.time()
    binary_sol_time = binary_sol_time_end - binary_sol_time_start
    val_comp_time_start = time.time()
    val = cv.closure_value(sol_vector, G_ST_node_data)
    val_comp_time_end = time.time()
    val_comp_time = val_comp_time_end - val_comp_time_start
    admin_rearrange_time_start = time.time()
    branch_num = str(0) #We give the number 0 to the optimal solution for the purposes of branching
    num_nodes = G_ST.number_of_nodes()
    solution_entry_reordered = [0]*len(sol_vector) #Before adding the solution to the k_best list, use the mapping so that the solution reflects the original inputted graph
    for i in range(len(sol_vector)): #Before adding the solution to the k_best list, use the mapping so that the solution reflects the original inputted graph
        solution_entry_reordered[i] = sol_vector[mapping[i+1]-1]   
    admin_rearrange_time_end = time.time()
    admin_rearrange_time = admin_rearrange_time_end - admin_rearrange_time_start
    sp_dict_time_start = time.time()
    sp_dictionary = sps.subproblems(sol_vector) #next, we generate the  reduced problems to solve for the next best solution  
    sp_dict_time_end = time.time()
    sp_dict_time = sp_dict_time_end - sp_dict_time_start
    k_best_list.append({"Branch": branch_num, "Sub Problem": 0, "Value": val,"Solution": solution_entry_reordered,"Find Solution Total Time": sp_dict_time_start - overall_time_start, "SP Dict Create Time": sp_dict_time,"Reorder Sol Time": admin_rearrange_time ,"Input Data Time": input_data_time, "Binary Sol Time": binary_sol_time, "Val Comp Time": val_comp_time, "Solve Time": solve_time, "Graph Adjust Time": 0, "Graph Revert Time": 0, "REDUX Infeas Time": 0, "REDUX Extend Time": 0, "Num Subproblems": 1, "Num Subproblems Deleted in REDUX": 0, "Num Nodes in SG": num_nodes, "Time Extracting Min Cut": tot_emc, "Infeasible Sols Found While SP Solve": 0, "Infeasible Solve Time While SP Solve": 0 }) #Since we have the optimal solution, we append this solution to the k-best solutions li 
    if write_sol_file == True:
        with open(filename, "w") as f:
            json.dump(k_best_list, f)       
    G_res = opt_sol_R
    ## Apply REDUX if method is REDUX
    if method == 'REDUX':
        while len(k_best_list) < K: #In this while loop, we will have the k best solutions
            find_next_sol_time_start = time.time()
            number_of_sp = len(sp_dictionary) #Capture the number of sub-problems
            reduxInfeas_time_start = time.time()
            sp_dictionary = redux3.redux_infeas(sp_dictionary, DG)
            reduxInfeas_time_end = time.time()
            reduxInfeas_time_tot = reduxInfeas_time_end - reduxInfeas_time_start
            reduxExtend_time_start = time.time()
            sp_dictionary = redux3.redux_extend(sp_dictionary, DG)
            reduxExtend_time_end = time.time()
            reduxExtend_time_tot = reduxExtend_time_end - reduxExtend_time_start
            number_of_sp_NEW = len(sp_dictionary) #Capture the number of sub-problems after reduction
            num_of_sp_deleted = number_of_sp - number_of_sp_NEW
            all_solutions = sps.sub_problem_solver(branch_num, sp_dictionary, G_res, G_ST_node_data, method) #Solve all of the sub-problems after doing the reduction
            master_list.extend(all_solutions[0]) #Add all the solutions to the master list
            if len(master_list) == 0:
                print("K is larger than set of all solutions; all solutions found")
                return k_best_list
            next_sol = nb.nextbestSol(master_list) #Retrieve the next best solution from the master list
            solve_time = all_solutions[1]
            gr_tot_time = all_solutions[3]
            gr_tot_revert_time = all_solutions[4]
            time_extract_min_cut = all_solutions[2]
            infeasible_sols_while_solving = all_solutions[6]
            infeasible_sol_time_while_solving = all_solutions[5]
            next_sol["Solve Time"] = solve_time
            next_sol["Graph Adjust Time"] = gr_tot_time
            next_sol["Graph Revert Time"] = gr_tot_revert_time
            next_sol["REDUX Infeas Time"] = reduxInfeas_time_tot
            next_sol["REDUX Extend Time"] = reduxExtend_time_tot
            next_sol["Num Subproblems"] = number_of_sp
            next_sol["Num Subproblems Deleted in REDUX"] = num_of_sp_deleted
            next_sol["Time Extracting Min Cut"] =  time_extract_min_cut
            next_sol["Infeasible Sols Found While SP Solve"] = infeasible_sols_while_solving
            next_sol["Infeasible Solve Time While SP Solve"] = infeasible_sol_time_while_solving
            sp_dict_time_start = time.time()
            sp_dictionary = nb.nextbestSP(next_sol) #Generate the sub-problems to solve for the follow-on next best solutions
            sp_dict_time_end = time.time()
            sp_dict_time = sp_dict_time_end - sp_dict_time_start
            next_sol["SP Dict Create Time"] = sp_dict_time
            admin_rearrange_time_start = time.time()
            G_res = next_sol["Residual Graph"] #Extract the residual graph from the solution entry to use as the initial starting point for solving for the next best solution
            del next_sol["Residual Graph"] #Remove the residual graph from the solution entry, since it is a networkx object
            solution_entry_reordered = [0]*len(next_sol["Solution"]) #Before adding the solution to the k_best list, use the mapping so that the solution reflects the original inputted graph
            for i in range(len(next_sol["Solution"])): #Before adding the solution to the k_best list, use the mapping so that the solution reflects the original inputted graph
                solution_entry_reordered[i] = next_sol["Solution"][mapping[i+1]-1]   
            next_sol["Solution"] = solution_entry_reordered
            admin_rearrange_time_end = time.time()
            admin_rearrange_time = admin_rearrange_time_end - admin_rearrange_time_start
            next_sol["Reorder Sol Time"] = admin_rearrange_time
            find_next_sol_time_end = time.time()
            find_next_sol_time = find_next_sol_time_end - find_next_sol_time_start
            next_sol["Find Solution Total Time"] = find_next_sol_time - sp_dict_time
            k_best_list.append(next_sol) #Add the next best solution to the k best solution list
            if write_sol_file == True:
                with open(filename, "w") as f:
                    json.dump(k_best_list, f)
            branch_num = next_sol["Branch"] #Record the branching number from the next best solution       
            master_list.remove(next_sol) #Remove the next best solution from the master list, since it is no longer needed  
        master_file = str('master_') + filename
        for i in range(len(master_list)):    
            del master_list[i]['Residual Graph']
        if write_sol_file == True:
            with open(master_file, "w") as M:
                json.dump(master_list, M)   
        overall_time_end = time.time()
        overall_time = overall_time_end - overall_time_start
        time_file = str('time_') + filename
        file = open(time_file, 'w')
        file.write(str(overall_time))
        file.close()
    #Apply ML if method is ML    
    if method == 'ML':
        while len(k_best_list) < K: #In this while loop, we will have the k best solutions
            find_next_sol_time_start = time.time()
            number_of_sp = len(sp_dictionary) #Capture the number of sub-problems
            all_solutions = sps.sub_problem_solver(branch_num, sp_dictionary, G_res, G_ST_node_data, method) #Solve all of the sub-problems after doing the reduction
            master_list.extend(all_solutions[0]) #Add all the solutions to the master list
            if len(master_list) == 0:
                print("K is larger than set of all solutions; all solutions found")
                return k_best_list
            next_sol = nb.nextbestSol(master_list) #Retrieve the next best solution from the master list
            solve_time = all_solutions[1]
            gr_tot_time = all_solutions[3]
            gr_tot_revert_time = all_solutions[4]
            time_extract_min_cut = all_solutions[2]
            infeasible_sols_while_solving = all_solutions[6]
            infeasible_sol_time_while_solving = all_solutions[5]
            next_sol["Solve Time"] = solve_time
            next_sol["Graph Adjust Time"] = gr_tot_time
            next_sol["Graph Revert Time"] = gr_tot_revert_time
            next_sol["Num Subproblems"] = number_of_sp
            next_sol["Time Extracting Min Cut"] =  time_extract_min_cut
            next_sol["Infeasible Sols Found While SP Solve"] = infeasible_sols_while_solving
            next_sol["Infeasible Solve Time While SP Solve"] = infeasible_sol_time_while_solving
            sp_dict_time_start = time.time()
            sp_dictionary = nb.nextbestSP(next_sol) #Generate the sub-problems to solve for the follow-on next best solutions
            sp_dict_time_end = time.time()
            sp_dict_time = sp_dict_time_end - sp_dict_time_start
            next_sol["SP Dict Create Time"] = sp_dict_time
            admin_rearrange_time_start = time.time()
            G_res = next_sol["Residual Graph"] #Extract the residual graph from the solution entry to use as the initial starting point for solving for the next best solution
            del next_sol["Residual Graph"] #Remove the residual graph from the solution entry, since it is a networkx object
            solution_entry_reordered = [0]*len(next_sol["Solution"]) #Before adding the solution to the k_best list, use the mapping so that the solution reflects the original inputted graph
            for i in range(len(next_sol["Solution"])): #Before adding the solution to the k_best list, use the mapping so that the solution reflects the original inputted graph
                solution_entry_reordered[i] = next_sol["Solution"][mapping[i+1]-1]   
            next_sol["Solution"] = solution_entry_reordered
            admin_rearrange_time_end = time.time()
            admin_rearrange_time = admin_rearrange_time_end - admin_rearrange_time_start
            next_sol["Reorder Sol Time"] = admin_rearrange_time
            find_next_sol_time_end = time.time()
            find_next_sol_time = find_next_sol_time_end - find_next_sol_time_start
            next_sol["Find Solution Total Time"] = find_next_sol_time - sp_dict_time
            k_best_list.append(next_sol) #Add the next best solution to the k best solution list
            if write_sol_file == True:
                with open(filename, "w") as f:
                    json.dump(k_best_list, f)
            branch_num = next_sol["Branch"] #Record the branching number from the next best solution       
            master_list.remove(next_sol) #Remove the next best solution from the master list, since it is no longer needed  
        master_file = str('master_') + filename
        for i in range(len(master_list)):    
            del master_list[i]['Residual Graph']
        if write_sol_file == True:
            with open(master_file, "w") as M:
                json.dump(master_list, M)
        overall_time_end = time.time()
        overall_time = overall_time_end - overall_time_start
        time_file = str('time_') + filename
        if write_sol_file == True:
            file = open(time_file, 'w')
            file.write(str(overall_time))
            file.close()
    
    return k_best_list

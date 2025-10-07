# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 16:25:37 2025

This file is called by kclosures AND sub_problem_solver
This file has the following functions:
    binary_sol_vector: this function takes an optimal solution in the form of a minimum-cut networkX solution and transforms it into a binary solution list

@author: andre
"""
#import numpy as np

#INPUT: opt_sol (the optimal solution from the minimum cut networkX function)
#OUTPUT: sol_vec: a binary solution vector (python list) that represents the optimal solution as a list object
def binary_sol_vector(opt_sol):
    #Create the binary solution vector
    length = len(opt_sol[1][0])-1+len(opt_sol[1][1])-1
    sol_vec = [0]*length
    closure = opt_sol[1][0] #The closure of the optimum solution is comprised of the nodes of the set containing node 0
    for i in range(len(list(closure))):
        val = list(closure)[i]
        if val > 0: #if the node is not the source node, then we update the sub-problem 
            sol_vec[val-1]=1
    return sol_vec
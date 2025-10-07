# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 09:28:30 2025

This file is called by kclosures AND sub_problem_solver
This file contains the following functions:
    closure_value: this function takes a binary solution vector and a list object that contains vertex weights to compute the closure value

@author: andre
"""
#INPUT: sol_vector: a binary list; G_ST_node_data: a list containing the node weights
#OUTPUT: val: a number that is the value of the closure
def closure_value(sol_vector, G_ST_node_data):
    val = 0 #set the value to 0; val will be updated to get the value of the closure 
    for j in range(len(sol_vector)): #compute value of the closure using node capacity
        val = val + sol_vector[j]*G_ST_node_data[j+1]
    return val
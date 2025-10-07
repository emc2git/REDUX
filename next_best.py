# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 16:40:53 2025

This file is called by kclosures
This file has the following functions:
    nextbestSol: this function takes a list object that contains dictionaries of solutions and retrieves the best solution from the list
    nextbestSP: this function takes a dictionary object that is the next best solution and generates the set of reduced problems
@author: andre
"""

### ----- Function to extract the next best solution from the master list  --- 
#INPUT: solution_list (a list object with dictionary entries of Closure Problem solutions); 
#OUTPUT: next_sol (a dictionary object with a single solution)
def nextbestSol(solution_list):
    next_sol = max(solution_list, key=lambda x: x["Value"]) #we pull out the next best solution
    return next_sol    

#### ------------- Function to generate the sub-problems for the next best solution ---- 
#INPUT: next_sol (a dictionary object containing a solution); 
#OUTPUT: sp_dictionary (a dictionary object of all sub-problems based on the input solution)
def nextbestSP(next_sol):
    num_fixed = next_sol["Sub Problem"] #we keep variables fixed if they were part of the initial fixing of variables from the previous sub-problem (this is the branching technique)
    sp_dictionary = {} #Empty dictionary to store the sub-problems
    for i in range(num_fixed+1,len(next_sol["Solution"])+1):
        new_prob = next_sol["Solution"][0:i] #extract the optimal solution variables from 0 to i
        new_prob[i-1] = 1-new_prob[i-1] #the last element of the sub-problem is changed from the optimal solution
        sp_dictionary[i] =  new_prob #add the new sub-problem to the dictionary 
        sp_dictionary[i].extend([None]*(len(next_sol["Solution"])-i))
    return sp_dictionary
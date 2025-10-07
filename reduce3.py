# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 16:38:36 2025

This file is called by kclosures
This file contains the following functions:
    
    redux_infeas: this function takes a set of reduced problems and the original closure
    graph (before the Picard transformed graph) and eliminates all reduced problems that are infeasible.
    
    redux_extend: this function takes a set of reduced problems (after redux_infeas) and the original closure 
    graph (before the Picard transformed graph) and extends the sets of fixed variables

@author: andre
"""

#INPUT: sp_dict: a dictionary object containing the reduced problems; DG: the original problem's directed graph (e.g. not the Picard Graph)
#OUTPUT: sp_dict: an updated dictionary object with all feasible reduced problems

def redux_infeas(sp_dict, DG):
    if len(sp_dict) == 0:
        return sp_dict
    keys = list(sp_dict.keys())
    for key in keys:
        if sp_dict[key][key-1] == 0:
            parents = list(DG.predecessors(key))
            for parent in parents:
                if sp_dict[key][parent-1] == 1:
                    del sp_dict[key]
                    break
    return sp_dict

#INPUT: sp_dict: a dictionary object containing all feasible reduced problems; DG: the original problem's directed graph (e.g. not the Picard Graph) 
#OUTPUT: sp_dict: an updated dictionary object with all sets of fixed variables extended
def redux_extend(sp_dict, DG):
    if len(sp_dict) == 0:
        return sp_dict
    keys = list(sp_dict.keys())
    for key in keys:
        visit_dict = {node: False for node in DG.nodes()}
        D = list()
        for j in range(1,key+1): 
            if visit_dict[j] == False:
                D.append(j)
            while len(D) > 0:
                d = D.pop(0)
                if sp_dict[key][d-1] == 1:
                    children = list(DG.successors(d))
                    for child in children:
                        if visit_dict[child] == False:
                            visit_dict[child] = True
                            sp_dict[key][child-1] = 1
                            D.append(child)
    return sp_dict





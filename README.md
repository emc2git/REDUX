# REDUX
An Efficient Method to Compute the k-Best Closures in a DAG

IMPORTANT: kclosures requires the networkX (version 2.6.3 or higher) package to be installed in the environment.

**To test that kclosures loaded and runs properly, execute the following commands (and verify the below output) in python to obtain the 10-best closures to the Picard graph (the .prec and .upit files for this graph is included in the file and is from Picard's paper on how to solve the maximum weight closure problem - reference: https://pubsonline.informs.org/doi/10.1287/mnsc.22.11.1268):

import kclosures as kc
kbestREDUX = kc.solve(10, 'picard.prec','picard.upit','picard_out1','REDUX',True)
kbestBASIC = kc.solve(10, 'picard.prec','picard.upit','picard_out2','ML',True)
#To view solutions
kbestREDUX[0]['Value']
	Out[1]: 9.0
kbestREDUX[0]['Solution']
	Out[2]: [1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1]
kbestREDUX[9]['Value']
	Out[3]: 6.0
kbestREDUX[9]['Solution']
	Out[4]: [0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1]
kbestBASIC[9]['Value']
	Out[5]: 6.0
kbestBASIC[9]['Solution']
	Out[6]: [0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1]

###########################################################################################################
FILES INCLUDED IN KCLOSURES SOLVER PACKAGE
**Note: the headings in each python file provide descriptions for the included functions

kclosures.py
file_input.py
screen_data.py
picard_transform.py
binary_solution.py
next_best.py
reduce3.py
extract_min_cut_source_set.py
closure_value.py
sub_problem_solve.py
sub_graph.py
graph_required_alt.py

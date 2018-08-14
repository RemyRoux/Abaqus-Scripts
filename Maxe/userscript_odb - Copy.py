"""
userscript_odb.py

Script to read the maximum U1 at midpoint in U1 in mm and convert to inches.

Author : Jegan Chinnaraju, DS Simulia 
Version : 1.0
Date : 6/1/2013

usage:
abaqus python userscript_odb.py
"""

#
import odbAccess
from odbAccess import *
import __main__
import operator

#
# S T A R T
# 
if __name__ == '__main__':
    

	odbName = "PlateStretch.odb"
	myOdb = openOdb(odbName,readOnly=True)
		
	U1_Measure = myOdb.rootAssembly.instances['PLATE-1'].nodeSets['U1_MEASURE']
	U1_Max_AT_MIDPOINT_mm = myOdb.steps['Loading'].frames[-1].fieldOutputs['U'].getScalarField(componentLabel = 'U1').getSubset(region = U1_Measure).values[0].data
	U1_Max_AT_MIDPOINT_inches =  0.0393701 * U1_Max_AT_MIDPOINT_mm 
	
	paramsFile=open('user_params.txt','w')
	
	paramsFile.write("U1_Max_AT_MIDPOINT_mm"+"\t"+ str(U1_Max_AT_MIDPOINT_mm)+"\n")
	paramsFile.write("U1_Max_AT_MIDPOINT_inches"+"\t"+ str(U1_Max_AT_MIDPOINT_inches)+"\n")

	paramsFile.close()
	
	myOdb.close()

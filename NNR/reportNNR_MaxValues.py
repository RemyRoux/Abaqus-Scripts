# script to find the largest absolute Y-value within a group of history regions
# User to specify the ODB, step name and output variable name

from abaqus import *
from abaqusConstants import *
from caeModules import *
from textRepr import prettyPrint as pp
from odbAccess import *
# USER INPUT

stepName    = 'SSE_0p3g-4_1_4'
OutSetNames     = ['ROOF','STRAKE-6','STRAKE-5','STRAKE-4','STRAKE-3','STRAKE-2','STRAKE-1']
fileName   = 'PTR_Tank-'+stepName+'.odb'

odb = openOdb(fileName)
ra  = odb.rootAssembly

variableU = 'U'


#####################################################################################################
coordSys = odb.rootAssembly.DatumCsysByThreePoints(name='cylC',
    coordSysType=CYLINDRICAL, origin=(0,0,0),
    point1=(1.0, 0.0, 0), point2=(1.0, 1.0, 0.0) )

reportName = fileName+'_Displacements.txt'
reportFile = open(reportName,'w')
reportFile.write('Output Data for NNR Displacements: \n')
reportFile.write('  NodeSet   Max Value   Min Value \n')  

Ref_nSet= odb.rootAssembly.instances['TANK-1'].nodeSets['FLOOR']

for nSetName in OutSetNames:
 maxRU1 = 0.
 minRU1 = 0.

 maxZU1 = 0.
 minZU1 = 0.

 nSet= odb.rootAssembly.instances['TANK-1'].nodeSets[nSetName]


 for i in range(0,10):
   curFrame = odb.steps[stepName].frames[i]

   Ref_displace = curFrame.fieldOutputs['U'].getSubset(region=Ref_nSet)
   Ref_cylindricalDisp = Ref_displace.getTransformedField(datumCsys=coordSys)
   Ref_radialDisp = Ref_cylindricalDisp.getScalarField(componentLabel='U1')
   for val in Ref_radialDisp.values:
     if val.nodeLabel == 23:
        R_Ref = val.data
        break
#   reportFile.write(' %s %12.4E  \n' %('Reference Radial Disp Centre', R_Ref))  

   displace = curFrame.fieldOutputs['U'].getSubset(region=nSet)
   cylindricalDisp = displace.getTransformedField(datumCsys=coordSys)
   radialDisp = cylindricalDisp.getScalarField(componentLabel='U1')
   for val in radialDisp.values:
     delR = val.data - R_Ref
     if minRU1 > delR:
       minRU1 = delR
     if maxRU1 < delR:
       maxRU1 = delR

   Ref_ZDisp = Ref_cylindricalDisp.getScalarField(componentLabel='U3')
   for val in Ref_ZDisp.values:
     if val.nodeLabel == 23:
        Z_Ref = val.data
        break
#   reportFile.write(' %s %12.4E  \n' %('Reference Vertical Disp Centre',Z_Ref)) 

   ZDisp = cylindricalDisp.getScalarField(componentLabel='U3')
   for val in ZDisp.values:
     if minZU1 > Z_Ref:
       minZU1 = Z_Ref
     if maxZU1 < Z_Ref:
       maxZU1 = Z_Ref

#output to file

 reportFile.write(' %s %12.4E  %12.4E  %s %12.4E \n' %(nSetName,maxRU1,minRU1,'R',max(abs(maxRU1),abs(minRU1)) ))  
 reportFile.write(' %s %12.4E  %12.4E  %s %12.4E \n' %(nSetName,maxZU1,minZU1,'Z',max(abs(maxZU1),abs(minZU1)) )) 
reportFile.close()
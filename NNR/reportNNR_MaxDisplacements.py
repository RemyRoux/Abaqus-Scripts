# script to find the largest absolute Y-value within a group of history regions
# User to specify the ODB, step name and output variable name

from abaqus import *
from abaqusConstants import *
from caeModules import *
from textRepr import prettyPrint as pp
from odbAccess import *
# USER INPUT

stepName    = 'OBE_0p15g-1_4_4'
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
 maxXU = 0.
 minXU = 0.
 maxYV = 0.
 minYV = 0.
 maxZW = 0.
 minZW = 0.

 nSet= odb.rootAssembly.instances['TANK-1'].nodeSets[nSetName]


 for i in range(0,600):
   curFrame = odb.steps[stepName].frames[i]

   Ref_displace = curFrame.fieldOutputs['U'].getSubset(region=Ref_nSet)
   Ref_XDisp = Ref_displace.getScalarField(componentLabel='U1')
   for val in Ref_XDisp.values:
     if val.nodeLabel == 23:
        X_Ref = val.data
        break
   Ref_YDisp = Ref_displace.getScalarField(componentLabel='U2')
   for val in Ref_YDisp.values:
     if val.nodeLabel == 23:
        Y_Ref = val.data
        break
   Ref_ZDisp = Ref_displace.getScalarField(componentLabel='U3')
   for val in Ref_ZDisp.values:
     if val.nodeLabel == 23:
        Z_Ref = val.data
        break


   displace = curFrame.fieldOutputs['U'].getSubset(region=nSet)
   XDisp = displace.getScalarField(componentLabel='U1')
   for val in XDisp.values:
     delX = val.data - X_Ref
     if minXU > delX:
       minXU = delX
     if maxXU < delX:
       maxXU = delX
   YDisp = displace.getScalarField(componentLabel='U2')
   for val in YDisp.values:
     delY = val.data - Y_Ref
     if minYV > delY:
       minYV = delY
     if maxYV < delY:
       maxYV = delY
   ZDisp = displace.getScalarField(componentLabel='U3')
   for val in ZDisp.values:
     delZ = val.data - Z_Ref
     if minZW > delZ:
       minZW = delZ
     if maxZW < delZ:
       maxZW = delZ

#output to file

 reportFile.write(' %s %12.4E  %12.4E  %s %12.4E \n' %(nSetName,maxXU,minXU,'X',max(abs(maxXU),abs(minXU)) ))  
 reportFile.write(' %s %12.4E  %12.4E  %s %12.4E \n' %(nSetName,maxYV,minYV,'Y',max(abs(maxYV),abs(minYV)) ))  
 reportFile.write(' %s %12.4E  %12.4E  %s %12.4E \n' %(nSetName,maxZW,minZW,'Z',max(abs(maxZW),abs(minZW)) )) 
reportFile.close()
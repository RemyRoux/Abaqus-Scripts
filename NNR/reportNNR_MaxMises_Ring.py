# Script to determine the membrane and bending stress for a 3D shell model using
# the stresses at the top and bottom section points
#
#################################################################################

# import modules
from abaqus import *
from abaqusConstants import *
from caeModules import *
from odbAccess import *
from itertools import izip
from textRepr import prettyPrint as pp

stepName    = 'OBE_0p15g-1_4_4'
OutSetNames     = ['ALL']
fileName   = 'PTR_Tank-'+stepName+'.odb'
reportName = fileName+'_MaxMises_Ring.txt'
reportFile = open(reportName,'w')
reportFile.write('Output Data for NNR Maximum Mises Stress Values: \n')
reportFile.write('  ElementSet   Max Value  \n')  


# define odb based on what is currently in the active viewport
# define odb based on what is currently in the active viewport
odb = openOdb(fileName)
ra  = odb.rootAssembly

for step in odb.steps.values():
 eSetMaxValueM = 0.
 eSetMaxM = []

 for i,frame in enumerate(step.frames):
   print 'frame %s '%i
   for inst in ra.instances.items():
#    print ' Name',inst[0]
    iName = inst[0]
    if 'RING' in iName:

       for eSetName in OutSetNames:
         instance = ra.instances[iName]
         eSet = instance.elementSets[eSetName]

         stressValuesM   = frame.fieldOutputs['S'].getSubset(region=eSet).values

       for j in range(len(stressValuesM)):
         eSetMaxM.append(stressValuesM[j].mises)
       if max(eSetMaxM) > eSetMaxValueM:
         eSetMaxValueM = max(eSetMaxM)
         iFmax = i
#output to file

 reportFile.write(' Frame %s RING Maximum Stress %12.4e  \n' %(iFmax,eSetMaxValueM ))  
reportFile.close()



# script to find the largest absolute Y-value within a group of history regions
# User to specify the ODB, step name and output variable name

from abaqus import *
from abaqusConstants import *
from caeModules import *
from textRepr import prettyPrint as pp
from odbAccess import *
import time

# USER INPUT

stepName    = 'OBE_0p15g-1_4_4'
OutSetNames = ['OUTER']
fileName    = 'PTR_Tank-'+stepName+'P1.odb'

odb = openOdb(fileName)
ra  = odb.rootAssembly
step = odb.steps[stepName]

#####################################################################################################

reportName = fileName+'_Pressure.txt'
reportFile = open(reportName,'w')
reportFile.write('Output Data for NNR Pressure: \n')
reportFile.write('  NodeSet   Max Value   Min Value \n')  

instance = odb.rootAssembly.instances['WATER-1']

outPut = {}
for nSetName in OutSetNames:
	outPut[nSetName] = {}
	outPut[nSetName]['maxPressure'] = []
	outPut[nSetName]['minPressure'] = []

frameRepository = step.frames
for i, frame in enumerate(frameRepository):
  print 'Frame %s'%i
  for nSetName in OutSetNames:
    print 'Node set %s'%nSetName
    nSet= instance.nodeSets[nSetName]
    pressure = frame.fieldOutputs['POR'].getSubset(region=nSet).values
    maxP = max(pressure)
    minP = min(pressure)
    outPut[nSetName]['maxPressure'].append(maxP.data)
    outPut[nSetName]['minPressure'].append(minP.data)

#output to file
for nSetName in OutSetNames:
  maxPres = max(outPut[nSetName]['maxPressure'])
  minPres = min(outPut[nSetName]['minPressure'])
  reportFile.write(' %s %12.4E  %12.4E \n' %(nSetName,maxPres,minPres) )  


reportFile.close()

del outPut

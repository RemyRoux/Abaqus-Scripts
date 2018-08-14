
#-------------------------------------------------------------------------------------
# script to determine relative displacements
#-------------------------------------------------------------------------------------

#
from abaqus import *
from abaqusConstants import *
from caeModules import *
from part import *
from assembly import *
from visualization import *
from string import split
from textRepr import prettyPrint as pp
from VectorModule import Vector as Vector
from interaction import CouplingType
from interaction import TieType
import string
import time
import numpy


##############################################################3

## Starting to run script
VP = session.viewports[session.currentViewportName]
displayedObject = VP.displayedObject

part  = None
model = None
# check what is the displayedObject
if type(displayedObject) == PartType:
  part = displayedObject
  modelName = part.modelName
  model = mdb.models[modelName]
  ra = model.rootAssembly
  print 'Found Part Type'
elif type(displayedObject) == AssemblyType:
  ra = displayedObject
  modelName = ra.modelName
  model = mdb.models[modelName]
  print 'Found Assembly Type'
elif type(displayedObject) == OdbType:
  odb = displayedObject
  print 'Found ODB Type'


scratchOdb = session.ScratchOdb(odb=odb)
sessionStep = scratchOdb.Step(name='Session Step', domain=TIME, timePeriod=1.0,
                              description='Step for Viewer non-persistent fields')
sessionFrame = sessionStep.Frame(frameId=0, frameValue=0.0, description='Session Frame')


preloadStepName = 'Preload'
for stepName in odb.steps.keys():
  print stepName
  if 'Unload Test-' in stepName:
    print 'found stepName'
    unloadStepName = stepName
    break

preloadU = odb.steps[preloadStepName].frames[-1].fieldOutputs['U']
unloadU  = odb.steps[unloadStepName].frames[-1].fieldOutputs['U']

deltaU = unloadU - preloadU
sessionField = sessionFrame.FieldOutput(name='DeltaU', field=deltaU, description='Relative Displacement')
VP.odbDisplay.setFrame(frame=sessionFrame)


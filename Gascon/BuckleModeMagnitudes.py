# script to output the maximum displacement magnitude for a set in 
# a linear buckleing ODV
#
from abaqus import *
from caeModules import *
import assembly
from abaqusConstants import *
from part import PartType
from assembly import AssemblyType
from visualization import OdbType
import displayGroupMdbToolset as dgm
from textRepr import prettyPrint as pp


VP = session.viewports[session.currentViewportName]
displayedObject = VP.displayedObject

part  = None
model = None
ra = None
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
  ra = model.rootAssembly
  print 'Found Assembly Type'
elif type(displayedObject) == OdbType:
  odb = displayedObject
  ra = odb.rootAssembly
  print 'Found ODB Type'

frameIndexList = []
tol = 5e-1
if odb:
  fileName = odb.name.split('/')[-1]
  name = fileName.split('.odb')[0]
  #
  for stepName, step in odb.steps.items():
    if 'Buckling' in stepName:
      stepIndex = odb.steps.keys().index(stepName)
      for frameIndex in range(1,len(step.frames)):
        print 'Checking frame %s'%frameIndex
        frame = step.frames[frameIndex]
        uMag = frame.fieldOutputs['U'].getScalarField(invariant=MAGNITUDE)
        for elementSetName in ['TOROSPHERICALENDS',]:
           nodeset = ra.instances['OUTERTANK_SIDE2-1'].nodeSets[elementSetName]
           uMagSet = uMag.getSubset(region = nodeset)
           uMagValues = [value.data for value in uMagSet.values]
           uMagMax = max(uMagValues)
           if uMagMax > tol:
             eigenValue = float(frame.description.split('EigenValue = ')[-1].strip()) + 1
             frameIndexList.append((frameIndex, eigenValue))
             print '%s has maximum magnitude %s at mode %s'%(frameIndex, uMagMax, frame.description.split('EigenValue = ')[-1].strip())
  
  if len(frameIndexList) > 0:
    print 'The following frames include significant torospherical displacements'
    print frameIndexList





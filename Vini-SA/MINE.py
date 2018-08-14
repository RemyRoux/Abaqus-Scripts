# script to define material properties according to ASME 2
from abaqus import *
import assembly
from abaqusConstants import *
from part import PartType
from assembly import AssemblyType
from visualization import OdbType
import numpy
from textRepr import prettyPrint as pp

VP = session.viewports[session.currentViewportName]
displayedObject = VP.displayedObject

part  = None
model = None
# check what is the displayedObject
if type(displayedObject) == PartType:
  part = displayedObject
  modelName = part.modelName
  model = mdb.models[modelName]
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


refPnts = ra.referencePoints
for instanceName, instance in ra.instances.items():
  if 'HoldDownBolt' in instanceName:
    coordinates = instance.sets['Top'].nodes[0].coordinates
    refPoint = ra.ReferencePoint(point=coordinates)
    feature = ra.features[refPoint.name]
    referencePoint = refPnts[feature.id]
    ra.Set(referencePoints=(referencePoint,), name='Refpnt-%s'%instanceName.split('-')[-1])

pointList = []
for instanceName, instance in ra.instances.items():
  if 'HoldDownBolt' in instanceName:
    v1 = instance.sets['Top'].nodes[0]
    x, y, z = v1.coordinates
    for featureName, feature in ra.features.items():
      if featureName[:3] == 'RP-':
        if feature.xValue == x and feature.yValue == y:
	   v2 = refPnts[feature.id]
           pointList.append((v1, v2))
           break


ra.WirePolyLine(points=pointList, mergeType=IMPRINT, meshable=OFF)





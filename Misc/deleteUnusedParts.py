# script to delete parts that are not used in the model assembly
#
from abaqus import *
import assembly
from abaqusConstants import *
from part import PartType
from assembly import AssemblyType
from visualization import OdbType
from textRepr import prettyPrint as pp

VP = session.viewports[session.currentViewportName]
displayedObject = VP.displayedObject

part  = None
model = None
ra    = None
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


# delete parts that are not used in assembly
usedParts = [instance.part.name for instance in ra.instances.values()]
for partName in model.parts.keys():
  if partName not in usedParts:
    print partName
    del model.parts[partName]


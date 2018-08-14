# script to rename instances according to their part names
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

# change instanceNames to be consistent with part names
for instanceName, instance in ra.instances.items():
  partName = instance.partName
  if partName not in instance.name:
  	newInstanceName = partName
  	ra.features.changeKey(fromName=instanceName, toName=instance.partName)


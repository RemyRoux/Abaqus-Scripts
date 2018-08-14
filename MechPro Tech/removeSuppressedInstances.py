# Script to rename parts to be have same name as corresponding instance
#  and delete parts for instances that have been suppressed

from abaqus import *
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


if ra:
  leafInstanceList = VP.assemblyDisplay.displayGroup.root.leaf.instances
  instanceNameList = [ra.instances.keys()[key/2-2] for key in leafInstanceList]
  instancesNotUsed = [key for key inra.instances.keys() if key not in instanceNameList]

for instanceName in instancesNotUsed:
	ra.features[instanceName].suppressed()



# change partnames to be consistent with named instances
for instanceName, instance in ra.instances.items():
  partName = instance.partName
  #print partName, instance.name
  if partName not in instance.name:
    if len(instanceName.split('-'))>1:
      newPartName = instanceName.split('-')[0]
    else:
      newPartName = instanceName
    print 'Name change required for %s and %s'%(instanceName, partName)
    model.parts.changeKey( fromName=partName, toName=newPartName)


# delete parts that are not used in assembly
usedParts = [instance.part.name for instanceName, instance in ra.instances.items() \
             if ra.features[instanceName].isSuppressed() == False]

for instanceName in ra.instances.keys():
	if ra.features[instanceName].isSuppressed():
		del ra.features[instanceName]

for partName in model.parts.keys():
  if partName not in usedParts:
    print partName
    del model.parts[partName]


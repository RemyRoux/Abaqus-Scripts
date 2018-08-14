# script to rename parts according to their instance names
#
from abaqus import *
import assembly
from abaqusConstants import *
from part import PartType
from assembly import AssemblyType
from visualization import OdbType
from textRepr import prettyPrint as pp

print '\n\n\nStart\n'

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

# change partnames to be consistent with named instances
for instanceName, instance in ra.instances.items():
  partName    = instance.partName
  newPartName = ''
  if partName not in instance.name:
    if len(instanceName.split('-'))>1:
      try:
        instanceName.split('-')[-1] += 1
        for i in range(0, len(instanceName.split('-'))-2):
          newPartName = newPartName + instanceName.split('-')[i]
      except TypeError:
        for i in range(0, len(instanceName.split('-'))):
          if i == 0:
            newPartName = instanceName.split('-')[i]
          else:
            newPartName = newPartName + '-' + instanceName.split('-')[i]
    else:
      newPartName = instanceName
    print 'Name change required for %s and %s for New name: %s'%(instanceName, partName, newPartName)
    try:
      model.parts.changeKey( fromName=partName, toName=newPartName)
      print 'Name change successful for %s and %s'%(instanceName, partName)
    except e:
      print 'NOT SUCCESSFUl!'
      pass

from abaqus import mdb, session
from abaqusConstants import *
from textRepr import prettyPrint as pp
from abaqus import *
import assembly
from part import PartType
import re

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
  
  print 'Model: '+model.name
  print 'Part to be wrapped: '+part.name 
  
  originalPartName = re.subn('-Wrapped','',part.name)
  part = mdb.models[modelName].parts[originalPartName[0]]
else:
  print 'Please make the part to be wrapped as current'


#model = 'Q-SeventeenthIteration-Full'

try:
	del mdb.models[model.name].parts[part.name+'-Wrapped']
except KeyError:
	pass
except TypeError:
	pass

p = part
p.PartFromMesh(name=part.name+'-Wrapped', copySets=True)

model 	= mdb.models[model.name]
part 	= model.parts[part.name+'-Wrapped']

#Radius 	= 11.5
Radius = float(getInputs(fields=(('Radius','11.5')), dialogTitle='Input the desired Outer Diameter')[0])


def editNodesOuterDiam(wrappedPart,wrappedPartRadius):
    nodes = wrappedPart.nodes
    coords = []
    
    for n in nodes:
        x,y,z = n.coordinates
        theta = x/wrappedPartRadius
        newX = (wrappedPartRadius - z) * sin(theta)
        newY = y
        newZ = -(wrappedPartRadius - z) * cos(theta)
        coords.append((newX, newY, newZ))
    wrappedPart.editNode(nodes=nodes,coordinates=coords)   
    return

editNodesOuterDiam(part,Radius)

part 	= model.parts[part.name]
session.viewports['Viewport: 1'].setValues(displayedObject=part)

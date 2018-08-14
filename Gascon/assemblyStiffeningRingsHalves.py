#**********************************************************************************************
# 
#**********************************************************************************************
#  
# set up Abaqus defaults
from abaqus import *
from abaqusConstants import *
from caeModules import *
import xyPlot
from part import PartType
from assembly import AssemblyType
from visualization import OdbType
from textRepr import prettyPrint as pp
from VectorModule import Vector

VP = session.viewports[session.currentViewportName]
displayedObject = VP.displayedObject

part  = None
model = None
odb   = None
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
  ra = odb.rootAssembly
  print 'Found ODB Type'        


origin = -5.681435

###################################################################
######### Half stiffeners #########################################
###################################################################

pointList = [	-5.497435,
				-4.875,
				-4.253,
				-3.631,
				-3.009,
				]

part = model.parts['HalfRingStiffener']
vesselDatum = ra.instances['OuterVessel-1'].datums[3]
for i, point in enumerate(pointList):
  offset = point - origin
  print i, offset
  inst = ra.Instance(name='HalfRingStiffener-%s'%i, part=part, dependent=ON)
  instanceDatum = inst.datums[5]
  ra.FaceToFace(movablePlane=instanceDatum, fixedPlane=vesselDatum, flip=ON, clearance=-offset)
  
  
####################################################################
########### Full Stiffeners ########################################
####################################################################



pointList = [	-2.387,
				-1.765,
				-1.143,
				-5.89E-01,
				2.83E-04,
				5.89E-01,
				1.143565,
				1.765565,
				2.387565,
				3.009565,
				3.631565,
				4.253565,
				4.875565,
				5.497565
				]

part = model.parts['CompleteRingStiffener']
vesselDatum = ra.instances['OuterVessel-1'].datums[3]
for i, point in enumerate(pointList):
  offset = point - origin
  print i, offset
  inst = ra.Instance(name='CompleteRingStiffener-%s'%i, part=part, dependent=ON)
  instanceDatum = inst.datums[5]
  ra.FaceToFace(movablePlane=instanceDatum, fixedPlane=vesselDatum, flip=ON, clearance=-offset)


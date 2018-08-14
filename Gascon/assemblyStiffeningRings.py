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


origin = -5.675129
pointList = [-5.497694,
             -4.880662,
             -4.26363,
             -3.638087,
             -3.012543,
             -2.387,
             -1.765,
             -1.143,
             -521.E-03,
             -5.097E-03,
             510.806E-03,
             1.132806,
             1.754806,
             1.754806,
             2.376806,
             3.002349,
             3.627892,
             4.253436,
             4.875436,
             5.497436]

part = model.parts['CompleteRingStiffener']
vesselDatum = ra.instances['OuterVessel-1'].datums[3]
for i, point in enumerate(pointList):
  offset = point - origin
  print i, offset
  inst = ra.Instance(name='CompleteRingStiffener-%s'%i, part=part, dependent=ON)
  instanceDatum = inst.datums[5]
  ra.FaceToFace(movablePlane=instanceDatum, fixedPlane=vesselDatum, flip=ON, clearance=-offset)


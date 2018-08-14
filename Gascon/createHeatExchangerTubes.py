# Script to generate wires between points represent tubes between tubesheets
#
from abaqus import *
from abaqusConstants import *
from caeModules import *
from part import *
from assembly import *
from visualization import *
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
   print 'Found Assembly Type'
elif type(displayedObject) == OdbType:
   odb = displayedObject
   print 'Found ODB Type'
 


HoleDistribution = [ (1, 5),
                     (2, 10),
                     (3, 13),
                     (4, 14),
                     (5, 15),
                     (6, 16),
                     (7, 15),
                     (8, 16),
                     (9, 15),
		     (10, 16),
                     (11, 15),
                     (12, 16),
                     (13, 15),
                     (14, 14),
                     (15, 13),
                     (16, 10),
                     (17, 7),
                     (18, 4) 	]

dX = 34E-3
dY = dX*sin(pi/3.0)
zValue1 = 0.5637 
zValue2 = 4.1487
y_origin = 8*dY
pointList = []
for row, holeNo in HoleDistribution:
 	x_origin = -(holeNo - 1)/2.0 * dX
 	for i in range(holeNo):
 		xValue = x_origin + i*dX
 		yValue = y_origin - (row-1)*dY
 		pointList.append(((xValue, yValue, zValue1), (xValue, yValue, zValue2)))
 
if part:
   partName = part.name
   try:
      tubeWires = part.WirePolyLine(points=tuple(pointList), meshable=ON)
   except:
      print 'Error trying to create wires'
 
                                                                                                                                                                                                                                                                    
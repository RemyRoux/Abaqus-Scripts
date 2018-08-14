# script to import various parts from STEP file

from abaqus import *
import assembly
from abaqusConstants import *
from textRepr import prettyPrint as pp

VP = session.viewports[session.currentViewportName]
model  = mdb.models['NewGeometry']
step = mdb.openStep(fileName='e:/Consult/MechProTech/GeometryFiles/0BM3060.00-06-000.000-00 Drum Assy.stp', 
                    scaleFromFile=OFF)

for counter in range(1,401):
  print 'Importing part number %s'%counter
  model.PartFromGeometryFile(name='Part-%s'%counter, geometryFile=step, scale=0.001, bodyNum=counter,
                             combine=False, dimensionality=THREE_D, type=DEFORMABLE_BODY)



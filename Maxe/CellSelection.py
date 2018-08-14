from abaqus import *
from abaqusConstants import *
import __main__
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import optimization
import step
import interaction
import load
import mesh
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior

from abaqus import *
import assembly
from abaqusConstants import *
from part import PartType
from assembly import AssemblyType
from visualization import OdbType
from textRepr import prettyPrint as p

VP 				= session.viewports[session.currentViewportName]
displayedObject = VP.displayedObject

part 	= None
model 	= None
ra 		= None 

if type(displayedObject) == PartType:
	part = displayedObject
	modelName = part.modelName
	model = mdb.models[modelName]
	ra = model.rootAssembly
	print 'Found Part Type'
	print len(model.parts)

for i in model.parts.items():
	try:
		p = i[1]
		c = p.cells
		cells = c.getByBoundingSphere((0.0,0.0,0.0),(300),)
		p.Set(cells=cells, name='AllCell')
		p.AssignMidsurfaceRegion(cellList = c[0:1])
	except:
		pass
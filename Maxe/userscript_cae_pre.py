#"""
#userscript_oae_pre.py
#
#Script to include MeshSize
#
#Author : Jegan Chinnaraju, DS Simulia 
#Version : 1.0
#Date : 6/1/2013
#
#"""
#
from abaqus import *
from abaqusConstants import *
from caeModules import *
execfile('userscript_cae_pre.py')
#
#
#
def runUserScript(mdb, values):   
	#
	model = mdb.models['AerodynamicNoise_Round']
	part = model.parts['Volume']
	sketchtoedit = part.features['Cut extrude-1'].sketch
	model.ConstrainedSketch(name = '__edit__', objectToCopy = sketchtoedit)
	s1 = model.sketches['__edit__']
	g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
	s1.setPrimaryObject(option = SUPERIMPOSE)
	part.projectReferencesOntoSketch(sketch = s1, upToFeature = part.features['Cut extrude-1'], filter = COPLANAR_EDGES)
	d[0].setValues(value = 0.015, )
	s1.unsetPrimaryObject()
	#
	part = model.parts['Volume']
	part.features['Cut extrude-1'].setValues(sketch = s1)
	del model.sketches['__edit__']
	part = model.parts['Volume']
	#
	#part.deleteMesh()
	#part.seedPart(size=float(values['MeshSize']), deviationFactor=0.1, minSizeFactor=0.1)
	#
	part.regenerate()
	model.rootAssembly.regenerate()
	part.generateMesh()
	#
	mdb.save()
											

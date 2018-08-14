# -*- coding: utf-8 -*-
"""
Created on Wed Dec 07 09:23:43 2016

@author: feas

Refinement module
Refines the definition of each part of each model

"""

from abaqus import mdb, session
from abaqusConstants import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def SetDisplayProps():
	# define model name based on what is currently in the active viewport
	VP = session.viewports[session.currentViewportName]
	try:
		modelNameStr = VP.displayedObject.modelName
		for part in mdb.models[modelNameStr].parts.values():
			part.setValues(geometryRefinement=COARSE)
			part.setValues(geometryRefinement=EXTRA_FINE)
		# turn perspective off in viewport
		session.viewports['Viewport: 1'].view.setProjection(projection=PARALLEL)
		print 'All parts have been refined in the model {}'.format(modelNameStr)
	except AttributeError:
		print 'Please select an object in the model that you want to refine'
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
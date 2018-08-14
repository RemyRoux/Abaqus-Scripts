# -*- coding: utf-8 -*-
"""
Created on Wed Dec 07 09:33:52 2016

@author: feas
"""

from abaqusGui import *
from abaqusConstants import ALL
import osutils, os
from kernelAccess import mdb, session

class RefinePart_Plugin(AFXForm):

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def __init__(self, owner):
		
		# Construct the base class.
		#
		AFXForm.__init__(self, owner)
		

thisPath 	= os.path.abspath(__file__)
thisDir 	= os.path.dirname(thisPath)

toolset 	= getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerKernelMenuButton(
	moduleName 			= 'refinePartModule', functionName='SetDisplayProps()',
	buttonText 			= 'Refine Parts view',
	version 			= '1.0',
	author 			= 'FEAS (Pty) Ltd',
	description 		= 'Plug-In to refine the view of all the parts of each model',
	helpUrl 			= 'feas@feas.co.za'
)
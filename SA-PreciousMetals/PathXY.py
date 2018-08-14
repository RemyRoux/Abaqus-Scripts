# -*- coding: utf-8 -*-
"""
Created on Tue May 03 09:17:22 2016

@author: Jack
"""

from abaqus import *
from abaqusConstants import *
import __main__
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior

for i in range(1,10):
    pathName = 'Path-'+str(i)
    pth = session.paths[pathName]
    session.XYDataFromPath(name='V2-'+str(i)+'0% - Original Design', path=pth, includeIntersections=True, 
        projectOntoMesh=False, pathStyle=PATH_POINTS, numIntervals=10, 
        projectionTolerance=0, shape=DEFORMED, labelType=TRUE_DISTANCE)

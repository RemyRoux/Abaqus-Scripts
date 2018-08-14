# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 11:00:37 2016

@author: feas
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
from part import *
from assembly import *
from visualization import *
from string import split
from textRepr import prettyPrint as pp
from VectorModule import Vector as Vector
from interaction import CouplingType
from interaction import TieType
import time
import numpy as np
import csv


## Starting to run script
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



datums = ra.datums

hullMass = 10165.
hullR = 0.881
hullL = 6.


cats = ['Lateral','Long','GRP']
caty = [0.2,0,-0.2]
catmass = [hullMass/4*0.3,hullMass/4*0.3,hullMass/4*0.7]
ends = ['Aft','Fore']
endx = [-0.2,0.2]
sides = ['Port', 'Stb']
sidez = [-0.2, 0.2]



for cat, yOffset, mass in zip(cats, caty, catmass):
  for end, xOffset in zip(ends, endx):
    for side, zOffset in zip(sides, sidez):
      prefix = '{}-{}-{}'.format(cat, end, side)
      ra.features[prefix+'-Pt'].setValues(xOffset=xOffset, yOffset = yOffset, zOffset = zOffset)

for cat, yOffset, mass in zip(cats, caty, catmass):
  for end, xOffset in zip(ends, endx):
    for side, zOffset in zip(sides, sidez):
      prefix = '{}-{}-{}'.format(cat, end, side)
      ra.features[prefix+'-Pt'].setValues(xOffset=0, yOffset = 0, zOffset = 0)      
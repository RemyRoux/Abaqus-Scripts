# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 09:37:58 2016

@author: feas

Writes all set and surface names of instances and the RA to a file. Used to compare naming between two models

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
import csv, os



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

setList = []
surfList = []

for instKey in [k for k in ra.instances.keys() if 'FEAS-Bolt' not in k]:
  setList  += [instKey]
  surfList += [instKey]
  for setKey in [k for k in ra.instances[instKey].sets.keys()]:
    setList += [setKey]
  for surfKey in [k for k in ra.instances[instKey].surfaces.keys()]:
    surfList += [surfKey]    
  setList += ['']
  surfList += ['']


setList += [model.name ]
for setKey in [k for k in ra.sets.keys()]:
  setList += [setKey]

for surfKey in [k for k in ra.surfaces.keys() if 'FEAS-Bolt' not in k]:
  surfList += [surfKey]      


with open('SetNames.csv', "wb") as csvfile:
  wr = csv.writer(csvfile)
  wr.writerow(['Sets'])
  for entry in setList:
    wr.writerow([entry])
  wr.writerow([''])
  wr.writerow(['Surfaces'])
  for entry in surfList:
    wr.writerow([entry])
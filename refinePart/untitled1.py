# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 15:57:29 2017

@author: feas
"""
import exceptions 

from abaqus import *
from abaqusConstants import *
import __main__
import section
import regionToolset
import displayGroupMdbToolset as dgm
import mesh
import part
import material
import assembly
import optimization
import step
import interaction
import load
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior

#mod = mdb.models['TDC1150_TUP-007']
mod = mdb.models['ImportedParts']
for part in mod.parts.keys():
    num = part.split('-')[-1]
    p = mod.Part(name='Scaled-'+num, 
            objectToCopy=mod.parts[part], 
            compressFeatureList=ON, scale=1e-3)

#for part in mod.parts.keys():
#    if part.split('-')[0]!='Scaled':
#        mod.parts.changeKey(fromName=part, 
#            toName='TDC-'+part)
i=11
for part in mod.parts.keys():
    num = part.split('-')[-1]
    try:
        numInt=int(num)
        print numInt
        print part.split('-')[0]+'           '+part.split('-')[1]
        if (part.split('-')[0]=='TUP' and part.split('-')[1]=='Penetrator'):
            if int(numInt)>=9:
                i+=1
#                mod.parts.changeKey(fromName=part, 
#                                    toName='TDC-Bolt-%s'%i)
                print 'Renammed '+part+' to TUP-Pernetrator-%s'%i
    except e:
        print e
        
        

import section
import regionToolset
import displayGroupMdbToolset as dgm
import mesh
import part
import material
import assembly
import optimization
import step
import interaction
import load
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
from textRepr import prettyPrint as pp

a=mdb.models['F-LoadCase-F'].rootAssembly
for i in range(1,25):
    region1=a.instances['Bolt-%s'%i].sets['Start']
    region2=a.instances['TDC-BoltedCrown-1-Scaled'].surfaces['WasherFace-Bolt-%s'%i]
#    pp(region1)
#    pp(region2)
#    print '\n'
    mdb.models['F-LoadCase-F'].Coupling(name='WasherCoupling-Bolt-%s'%i, 
        controlPoint=region1, surface=region2, influenceRadius=WHOLE_SURFACE, 
        couplingType=KINEMATIC, localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, 
        ur2=ON, ur3=ON)


a = mdb.models['F-LoadCase-F'].rootAssembly
for i in range(1,25):
    region = a.instances['Bolt-%s'%i].surfaces['MidBolt']
    mdb.models['F-LoadCase-F'].BoltLoad(name='Bolt-%s'%i, createStepName='Contact', 
        region=region, magnitude=20767.0, boltMethod=APPLY_FORCE)

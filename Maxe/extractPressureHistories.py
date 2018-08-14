# script to extract pressure histories for all elements in outputSet
#
from abaqus import *
from abaqusConstants import *
from caeModules import *
from part import *
from assembly import *
from visualization import *

odb=session.odbs['E:/Support/FEAS/Isight/Round.odb']

ra       = odb.rootAssembly
instance = ra.instances['VOLUME-1']
step     = odb.steps['Flow']

timeType     = visualization.QuantityType(type=TIME)
pressureType = visualization.QuantityType(type=PRESSURE)

outputSet = instance.elementSets['HISTORYOUTPUT']
for element in outputSet.elements:
  elementLabel = element.label
  historyPoint = visualization.HistoryPoint(element=element)
  if step.getHistoryRegion(point=historyPoint).historyOutputs.has_key('PRESSURE'):
    history = step.getHistoryRegion(point=historyPoint).historyOutputs['PRESSURE']
    historyData = history.data
    historyName = history.name
    historyDescription = history.description
    session.XYData(data=historyData, name='%s-%s'%(historyName, elementLabel),
                   positionDescription='%s at element %s'%(historyDescription, elementLabel),
                   axis1QuantityType = timeType, axis2QuantityType=pressureType)


  
# script to output the vertical deflection along a path defined
# by set definitions. The algorithm defines the path using the shortest 
# distance to the next node. 
#

from abaqus import *
from abaqusConstants import *
import visualization
import displayGroupOdbToolset as dgo
import string
import numpy
from operator import itemgetter
from textRepr import prettyPrint as pp

def findNearestNode(currentNode, nodeList):
  """return the next nearest node in nodeList based on distance apart"""
  mag = [[numpy.linalg.norm(node.coordinates-currentNode.coordinates), node] for node in nodeList]
  nextNode = min(mag)[1]
  return nextNode

def createNodePathList(startNode, nodeList):
  """generate path based on node set"""
  pathNodeList = [[startNode.label, startNode.instanceName]]
  while len(nodeList) > 1:
    nodeList.remove(startNode)
    nextNode = findNearestNode(startNode, nodeList)
    pathNodeList.append([nextNode.label, nextNode.instanceName])
    startNode = nextNode
  return pathNodeList

def createPath(nodeSet):
  """generate XYData for contact pressure along path defined by nodeSet""" 
  nodeList = []
  for instanceCase in range(len(nodeSet.nodes )):
    nodeList += [node for node in nodeSet.nodes[instanceCase]]
  mag = [[abs(node.coordinates[1]),node.coordinates[1],node.coordinates[0], node] for node in nodeList]
  a=sorted(mag,key=itemgetter(0,1,2))
#  mag = [[numpy.linalg.norm(node.coordinates), node] for node in nodeList]
  startNode = a[1][3]
  pathNodeList = createNodePathList(startNode, nodeList)
  
  pathList = []
  instanceNameCurrent = pathNodeList[0][1]
  pathList += [[pathNodeList[0][1], [pathNodeList[0][0]]]]
  
  
  #  print instanceName, nodeNum
  for nodeNum, instanceName in pathNodeList[1:]:
    if instanceName == instanceNameCurrent:
      pathList[-1][-1] += [nodeNum]
    else:
      pathList += [[instanceName, [nodeNum]]]
      instanceNameCurrent = instanceName
  
  pathTuple = tuple([(name, tuple(nodeNums),) for name, nodeNums in pathList])    
  
  path = session.Path(name=nodeSet.name, type=NODE_LIST, expression=pathTuple)
  return path


def averageRepeatedXYData(xyDataObject):
  '''return the average values for xyDataObjects containing 
  multiple entries for the same x-values'''
  data = xyDataObject.data
  xInitial = data[0][0]
  sum = 0.0
  newData=[]
  count = 0
  for x, y in data:
    if x == xInitial:
      sum += y
      count += 1
    else:
      newData.append((xInitial,sum/count))
      xInitial = x
      sum = y
      count = 1
  newXYData = session.XYData(data=newData, name=xyDataObject.name+'_Averaged',
                             axis1QuantityType=xyDataObject.axis1QuantityType,
                             axis2QuantityType=xyDataObject.axis2QuantityType)
  return newXYData  

def minimumRepeatedXYData(xyDataObject):
  '''return the minimum values for xyDataObjects containing 
  multiple entries for the same x-values'''
  data = xyDataObject.data
  xInitial = data[0][0]
  minimum = data[0][1]
  newData=[]
  count = 0
  for x, y in data:
    if x == xInitial:
      if y < minimum:
         minimum = y
    else:
      newData.append((xInitial,minimum))
      xInitial = x
      minimum = y
  newXYData = session.XYData(data=newData, name=xyDataObject.name+'_Minimum',
                             axis1QuantityType=xyDataObject.axis1QuantityType,
                             axis2QuantityType=xyDataObject.axis2QuantityType)
  return newXYData  


def createRelativeData(xyDataObject):
	"""function to redine the xyDataObject as relative values"""
	(xData, yData) = zip(*xyDataObject.data)
	minYValue = min(yData)
	newYData = [dataValue-minYValue for dataValue in yData]
	newData = zip(xData,newYData)
	xyDataObject.setValues(data=newData)




VP  = session.viewports[session.currentViewportName]
odb = VP.displayedObject
ra = odb.rootAssembly
setNames = ['PERIMETER_A',
            'PERIMETER_B',
            'PERIMETER_C',
            'PERIMETER_D']

for nodeSetName in setNames:
  print nodeSetName
  nodeSet  = ra.nodeSets[nodeSetName]
  path = createPath(nodeSet)

VP.odbDisplay.display.setValues(plotState=CONTOURS_ON_DEF)
VP.odbDisplay.setPrimaryVariable(variableLabel='U', outputPosition=NODAL, refinement=(COMPONENT, 'U3'), )

for stepName, step in odb.steps.items():
  if 'ElasticFoundation' not in stepName:
    print stepName
    VP.odbDisplay.setFrame(step=stepName, frame=-1)
    for pathName, path in session.paths.items():
      print pathName
      session.XYDataFromPath(name='%s_%s'%(stepName, pathName), path=path, shape=UNDEFORMED, 
                             includeIntersections=False, projectOntoMesh=False, pathStyle=PATH_POINTS, labelType=TRUE_DISTANCE)


for xyDataObjectName, xyDataObject in session.xyDataObjects.items():
  if 'PERIMETER' in xyDataObjectName:
	 	print xyDataObjectName
	 	createRelativeData(xyDataObject)
	 	averageRepeatedXYData(xyDataObject)

for xyDataObjectName in session.xyDataObjects.keys():
	if 'Averaged' not in xyDataObjectName:
		del session.xyDataObjects[xyDataObjectName]

#for xyDataObjectName, xyDataObject in session.xyDataObjects.items():
#  if 'PERIMETER' in xyDataObjectName and 'Averaged' in xyDataObjectName:
#    xy = differentiate(differentiate(xyDataObject))
#    xy.setValues(sourceDescription='differentiate ( differentiate (%s) )'%xyDataObjectName)
#    session.xyDataObjects.changeKey(xy.name, 'doubleDerivative_%s'%xyDataObjectName)

for xyDataObjectName in session.xyDataObjects.keys():
	if '_temp_' in xyDataObjectName:
		del session.xyDataObjects[xyDataObjectName]

#for xyDataObjectName in session.xyDataObjects.keys():
#	if 'double' in xyDataObjectName:
#		del session.xyDataObjects[xyDataObjectName]

if len(session.xyPlots.keys())> 0:
  xyPlot1Name = session.xyPlots.keys()[0]
  xyp1 = session.xyPlots[xyPlot1Name]
  if len(session.xyPlots.keys())> 1:
    xyPlot2Name = session.xyPlots.keys()[1]
    xyp2 = session.xyPlots[xyPlot2Name]
else:
  xyp1 = session.XYPlot(name='myPlot1')
  xyp2 = session.XYPlot(name='myPlot2')

chartName = xyp.charts.keys()[0]
chart1 = xyp1.charts[chartName]
chart2 = xyp2.charts[chartName]

xyDataListUnloaded = []
for xyDataObjectName, xyDataObject in session.xyDataObjects.items():
  #print xyDataObjectName
  loadedTanks, dummy1, perimeterName, dummy2 = xyDataObjectName.split('_')
  if perimeterName not in loadedTanks:
    xyDataListUnloaded.append(session.Curve(xyData=xyDataObject))

xyDataListLoaded = []
for xyDataObjectName, xyDataObject in session.xyDataObjects.items():
  #print xyDataObjectName
  loadedTanks, dummy1, perimeterName, dummy2 = xyDataObjectName.split('_')
  if perimeterName in loadedTanks:
    xyDataListLoaded.append(session.Curve(xyData=xyDataObject))

chart1.setValues(curvesToPlot=xyDataListUnloaded, )
chart2.setValues(curvesToPlot=xyDataListLoaded, )
VP1.setValues(displayedObject=xyp1)

VP2  = session.viewports['Viewport: 2']
VP2.setValues(displayedObject=xyp2)


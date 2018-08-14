from abaqusConstants import *
from abaqus import *
from textRepr import prettyPrint as pp
from VectorModule import Vector as Vector
import copy
import numpy as np
import re
import regionToolset
from textwrap import fill

scriptOwner = 'FEAS-'

def centreOfCircularArc(edge):
  """function to return the coordinates of the centrepoint of a circular arc"""
  curvature_1 = edge.getCurvature(parameter = 0.0)
  curvature_2 = edge.getCurvature(parameter = 0.25)
  tangent_1 = Vector(curvature_1['tangent'])
  tangent_2 = Vector(curvature_2['tangent'])
  evaluationPoint_1 = Vector(curvature_1['evaluationPoint'])
  evaluationPoint_2 = Vector(curvature_2['evaluationPoint'])
  temp = tangent_1.cross(tangent_2)
  Axial = temp/temp.length()
  Radial_1 = tangent_1.cross(Axial)
  Radial_2 = tangent_2.cross(Axial)
  radius = curvature_1['radius']
  check_1 = evaluationPoint_1 + radius*Radial_1
  check_2 = evaluationPoint_2 + radius*Radial_2
  tol = 0.01 * radius
  if (check_1 - check_2).length() < tol:
    centre = check_1
    #print 'Found centre using positive radius'
  else:
    check_1 = evaluationPoint_1 - radius*Radial_1
    check_2 = evaluationPoint_2 - radius*Radial_2
    if (check_1 - check_2).length() < tol:
      centre = check_1
      #print 'Found centre using negative radius'
    else:
      print 'Unable to find curve centre'
  return centre

def isFaceConvex(face, edge):
  """function to determine whether the edge defines a convex arc within the face"""
  verySmall = 1E-2
  evaluationPoint = Vector(edge.getCurvature(parameter = 0.5)['evaluationPoint'])
  centre = centreOfCircularArc(edge)
  testPoint = verySmall*centre +(1.0-verySmall)*evaluationPoint
  try:
    foundFace = ra.instances[face.instanceName].faces.findAt(coordinates=(testPoint.x(),
                                                                          testPoint.y(),
                                                                          testPoint.z()))
  except:
    foundFace= None
  return foundFace==face

def findFaceAndCentroid(instance, elSet, diameter):
  """Returns face index and centre of circular arc"""
  Radius = diameter/2.
  tol = 0.06  # 8% variation allowed between specified washer OD and face OD
  faceAndCentreList = []
  for face in elSet.faces:
#    if len(face.getCells()) == 0:     # Ensures that cell faces are not included
      for edgeID in face.getEdges():
        edge = instance.edges[edgeID]
        try:
          edgeRadius = edge.getRadius()
        except:
          edgeRadius = None
        if type(edgeRadius) == float:
#          print 'Found', edgeRadius
          if abs(edgeRadius-Radius)/Radius < tol:
            if isFaceConvex(face, edge):
              centre = centreOfCircularArc(edge)
              try:
                middleFace = instance.faces.findAt(coordinates=tuple(centre.array))
              except:
                middleFace = None
              if middleFace == None:
                faceAndCentreList.append((face.index, centre))
  return faceAndCentreList

def readPartSections(instance):
  """Returns a dictionary with section assignments of an instance, grouped according to
     part level sets
  """
  part = model.parts[instance.partName]
  sections = {}
  for section in part.sectionAssignments:
    name = section.region[0]
    sections[name] = {}
    sections[name]['name'] = section.sectionName
    if 'Shell' in str(type(model.sections[section.sectionName])):
      if section.offsetType == MIDDLE_SURFACE:
        sections[name]['offset'] = 0.
      elif section.offsetType == TOP_SURFACE:
        sections[name]['offset'] = 0.5
      elif section.offsetType == BOTTOM_SURFACE:
        sections[name]['offset'] = -0.5
      elif section.offsetType == SINGLE_VALUE:
        sections[name]['offset'] = section.offset
      else:                                 # Could be expanded to measure offset
        sections[name]['offset'] = 0.
      sections[name]['thickness'] = model.sections[section.sectionName].thickness
    else:
      sections[name]['offset'] = 0.
      sections[name]['thickness'] = 0.
  return sections


def findWasherFaceClusters(instance, elsetName, diameter,count):
  """ Returns dict with: list of face IDs, bolt hole centre, plate thickness, shell offset
      grouped per bolt hole
  """
  tol = 1./Units
  tempFaceList = copy.deepcopy(findFaceAndCentroid(instance, instance.sets[elsetName],diameter))
  sections = readPartSections(instance)
  washerFaces = {}
  for i, (faceId, centre) in enumerate(tempFaceList):
    count += 1
    faceGroup = {}   
    washerFaces[count]=faceGroup
    faceIdGroup = [faceId]
    face = instance.faces[faceId]
    edges = [instance.edges[ID] for ID in face.getEdges()]
    radii = []
    for edge in edges:
      try:
        radii += [edge.getRadius()]
      except:
        pass
    radius = min(radii)  
    faceGroup['IDs'] = faceIdGroup
    faceGroup['instanceName'] = instance.name
    faceGroup['type'] = '3D' if len(face.getCells()) > 0 else '2D'
    faceGroup['centre'] = centre
    faceGroup['diameter'] = radius*2
    for setName in sections.keys():
      if face in instance.sets[setName].faces:
        faceGroup['thickness'] = sections[setName]['thickness']
        faceGroup['offset'] = sections[setName]['offset']
    if faceGroup['type'] == '3D':
        faceGroup['thickness'] = 0.
        faceGroup['offset'] = 0.
    for nextFaceId, nextCentre in tempFaceList[i+1:]:
      offset = (nextCentre - centre).length()
      if offset < tol:
        face = instance.faces[nextFaceId]
        edges = [instance.edges[ID] for ID in face.getEdges()]
        radii = []
        for edge in edges:
          try:
            radii += [edge.getRadius()]
          except:
            pass
        radius = min(radii)
        if faceGroup['diameter']/2 > radius:
          faceGroup['diameter']=radius*2
        faceIdGroup += [nextFaceId]
        tempFaceList.remove((nextFaceId, nextCentre))
  return washerFaces,count

def findBoltDiam(washerFaceDiam,boltDiamList):
  """ Returns the nearest sized bolt smaller than the washer face ID 
  """
  matchingDiams = [washerFaceDiam-i/Units for i in boltDiamList]
  sizeDiff = np.array([i if i >0 else 100. for i in matchingDiams ])
  return boltDiamList[np.argmin(sizeDiff)]



def matchHole(holeNum, myWasherFaces, allBoltHoles, matchedBoltHoles, boltDiamList):
  """ Finds the best match for provided hole, considering distance apart
      and distance being perpendicular to washer face
  """
  tol_allign = 0.001   # tolerance used when matching washerface normal to target washer face centre  
  tol_thick = 0.005    # tolerance used for plate thickness.
  tol_size = 0.05      # > abs(diameter1-diameter2)/smallDiameter. Based on Whaser OD
  instanceName = allBoltHoles[holeNum][1]
  matched = {}
  mWF = myWasherFaces
  washerNum = allBoltHoles[holeNum][2]
  centre = mWF[instanceName][washerNum]['centre']
  
  otherCentres=np.array([mWF[iN][wN]['centre']  for n,iN, wN in allBoltHoles] )
  centreDistances = [[n, centreDistV.length()] for n,centreDistV in enumerate(otherCentres-centre)
                      if
                      n not in matchedBoltHoles and
                      n != holeNum]
  
  centreDistances = np.array(centreDistances)
  
  washerFaceNum =  mWF[instanceName][washerNum]['IDs'][0]
  washerFaceNorm = Vector(ra.instances[instanceName].faces[washerFaceNum].getNormal())
  washerFaceThick = mWF[instanceName][washerNum]['thickness']
  washerFaceDiam = mWF[instanceName][washerNum]['diameter']
  tol_allign = washerFaceDiam/4.
  potentialMates = []
  for n, dist in centreDistances:
    n = int(n)
    targetInstanceName = allBoltHoles[n][1]
    targetWasherCentre = mWF[targetInstanceName][allBoltHoles[n][2]]['centre']
    targetWasherFaceThick = mWF[targetInstanceName][allBoltHoles[n][2]]['thickness']
    targetWasherFaceDiam = mWF[targetInstanceName][allBoltHoles[n][2]]['diameter']
    centreDiff = min([(centre-targetWasherCentre+washerFaceNorm*dist).length(),
                      (centre-targetWasherCentre-washerFaceNorm*dist).length()])
    correctThickness = 1                  
    correctAllignment = centreDiff < tol_allign                                # Checks allignmen           
    correctSizing = abs(washerFaceDiam-targetWasherFaceDiam)/ \
                    min([washerFaceDiam,targetWasherFaceDiam]) < tol_size
  #    print washerFaceDiam, targetWasherFaceDiam
  #    print correctThickness, correctAllignment , correctSizing
    if correctThickness and correctAllignment and correctSizing:
      potentialMates += [n]
    
    cDistances = []
    for item in potentialMates:
      indexNo = np.nonzero(centreDistances[:,0]==item)[0][0]
      cDistances += [centreDistances[indexNo]]
    cDistances = np.array(cDistances) if len(potentialMates) > 0 else []
  
  if len(potentialMates) > 1:     # Should more than one bolthole match the criteria, use the closest one
    selected = np.argmin(cDistances[:,1])
    mate = int(cDistances[selected,0])
    matched['holes'] = [holeNum, mate]
    washer1 = mWF[allBoltHoles[holeNum][1]][allBoltHoles[holeNum][2]]
    washer2 = mWF[allBoltHoles[mate][1]][allBoltHoles[mate][2]]
    matched['offset'] = offsetDirection(washer1, washer2)
    matched['length'] = sum(matched['offset']) + \
                         centreDistances[mate-1][1]
    matched['diameter'] = findBoltDiam(washerFaceDiam,boltDiamList)
  elif len(potentialMates) > 0:
    mate = potentialMates[0]
    selected = cDistances[0,0]
  #  print mate, selected
    
    matched['holes'] = [holeNum, mate]
    
    washer1 = mWF[allBoltHoles[holeNum][1]][allBoltHoles[holeNum][2]]
    washer2 = mWF[allBoltHoles[mate][1]][allBoltHoles[mate][2]]
    
    matched['offset'] = offsetDirection(washer1, washer2)
    matched['length'] = sum(matched['offset']) + \
                              cDistances[0][1]
    matched['diameter'] = findBoltDiam(washerFaceDiam,boltDiamList)
  else:
    matched['holes'] = [holeNum]
  
  matchedBoltHoles += [matched]
  return matchedBoltHoles

def offsetDirection(washer1, washer2):
  washerFaceNum1 =  washer1['IDs'][0]
  washerFaceNum2 =  washer2['IDs'][0]
  
  washerNorm1 = Vector(ra.instances[washer1['instanceName']].faces[washerFaceNum1].getNormal())
  washerNorm2 = Vector(ra.instances[washer2['instanceName']].faces[washerFaceNum2].getNormal())
  
  f1tof2 = washer2['centre']-washer1['centre']
  th1 = washer1['thickness']
  if np.dot(washerNorm1, f1tof2) < 0: #if W1 norm is alligned with c2-c1
    offset1 = th1 - (0.5+washer1['offset'])*th1
  else:
    offset1 = (0.5+washer1['offset'])*th1
  th2 = washer2['thickness']
  if np.dot(washerNorm2, f1tof2) > 0: #if W2 norm opposes c2-c1
    offset2 = th2 - (0.5+washer2['offset'])*th2
  else:
    offset2 = (0.5+washer2['offset'])*th2  
  return [offset1, offset2]


def createWasherSurfaces(faceList1, faceList2, namePrefix):
  """function to create washerface surfaces with the correct orientation"""
  centroidList1 = [face[1] for face in faceList1]
  sum = Vector(0.,0.,0.)
  for i in range(len(centroidList1)):
    sum = sum + centroidList1[i]
  centroid1 = sum/len(centroidList1)
  
  centroidList2 = [face[1] for face in faceList2]
  sum = Vector(0.,0.,0.)
  for i in range(len(centroidList2)):
    sum = sum + centroidList2[i]
  centroid2 = sum/len(centroidList2)
  
  VectorFace1ToFace2 = centroid2 - centroid1
  #
  side1Faces = []
  side2Faces = []
  for face, centroid in faceList1:
    if np.dot(Vector(face.getNormal()), VectorFace1ToFace2) > 0:
      side2Faces.append(ra.instances[face.instanceName].faces[face.index:face.index+1])
    else:
      side1Faces.append(ra.instances[face.instanceName].faces[face.index:face.index+1])
  name1 = '{}Face1'.format(namePrefix)
  ra.Surface(name = name1, side1Faces=side1Faces, side2Faces=side2Faces)
  #
  side1Faces = []
  side2Faces = []
  for face, centroid in faceList2:
    if np.dot(Vector(face.getNormal()), VectorFace1ToFace2) < 0:
      side2Faces.append(ra.instances[face.instanceName].faces[face.index:face.index+1])
    else:
      side1Faces.append(ra.instances[face.instanceName].faces[face.index:face.index+1])
  name2 = '{}Face2'.format(namePrefix)
  ra.Surface(name = name2, side1Faces=side1Faces, side2Faces=side2Faces)
  return

def placeBolt(instanceName, p1,p2, offset =0.):
  """ Places instance in assembly, alligning vector between nodes if instance sets
     'end1' and 'end2' with vector p1 and p2. Places 'end1' on p1 and shifts by washer thickness
  """   
  vZ = Vector([0.,0.,1.])
  instance = ra.instances[instanceName]
  end1 = instance.sets['End1'].vertices[0].pointOn[0]
  end2 = instance.sets['End2'].vertices[0].pointOn[0]
  
  #Translate instance such that 'end1' lies on glogabl (0,0,0)
  if end1 != (0.0, 0.0, 0.0):
    translate = tuple([-i for i in end1])
    ra.translate(instanceList=(instanceName, ), vector=translate)
  end1 = instance.sets['End1'].vertices[0].pointOn[0]
  end2 = instance.sets['End2'].vertices[0].pointOn[0]
  
  #Rotate instance to lie on global Z axis
  vB = Vector(end2)-Vector(end1)               #Bolt vector
  vBxy = Vector([vB[0],vB[1], 0.])             #Bolt vector on XY plane
  vBxy_perp = Vector(-vBxy[1], vBxy[0], 0.)    #Vector perpendiculst to vBxy
  vBxy_rotate = -vB.angle(vZ)*180/pi           #Angle to rotate from vBxy around vBxy_perp 
  ra.rotate(instanceList=(instanceName, ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=tuple(vBxy_perp.array), angle=vBxy_rotate)
  
  #Rotate to allign with p2-p1
  vB = p2-p1                   #Target bolt vector
  vBxy = Vector([vB[0],vB[1], 0.])             #Target bolt vector on XY plane
  vBxy_perp = (-vBxy[1], vBxy[0], 0.,) if vBxy.length() > 1E-14 else (1,0,0,)        #Vector perpendiculst to vBxy
  
  vBxy_rotate = vB.angle(vZ)*180/pi            #Angle to rotate from vBxy around vBxy_perp 
  ra.rotate(instanceList=(instanceName, ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=vBxy_perp, angle=vBxy_rotate)
  
  #Translate instance to p1, offset by washer face
  vBtrans = p1-vB.normal()*offset
  ra.translate(instanceList=(instanceName, ), vector=tuple(vBtrans.array))

def createBoltSection(diameter, boltMaterialName):
  sizeName = 'M{}'.format(int(diameter*Units))
  stressRadius = ((diameter*Units)**2.061724*0.505537/1E6/pi)**0.5*(1000./Units)
  model.CircularProfile(name=scriptOwner+'BoltProfile-'+sizeName, r=stressRadius)
  model.BeamSection(name=scriptOwner+'BoltSection-'+sizeName, 
      integration=DURING_ANALYSIS, poissonRatio=0.0, profile=scriptOwner+'BoltProfile-'+sizeName, 
      material=boltMaterialName, temperatureVar=LINEAR, consistentMassMatrix=False)


def createBolt(length,diameter):
  """ Creates bolt part using provided diameter and length
  """
  boltName = scriptOwner+'Bolt-M{}-{:0.1f}mm'.format(int(diameter*Units), length*Units)
  boltName = ''.join([b if b !='.' else 'p' for b in boltName])
  boltEnd1SetName = 'End1'
  boltEnd2SetName = 'End2'
  
  # Create the part
  sketch = model.ConstrainedSketch(name='__profile__', sheetSize=0.5)
  sketch.Line(point1=(0.0, 0.0), point2=(length, 0.0))
  part = model.Part(name=boltName, dimensionality=THREE_D,type=DEFORMABLE_BODY)
  part = model.parts[boltName]
  part.BaseWire(sketch=sketch)
  del model.sketches['__profile__']
  
  #Create sets
  edges = part.edges
  vertices = part.vertices
  part.Set(edges=edges[:], name='All')
  v1 = vertices.findAt(coordinates=((0,0,0),))
  v2 = vertices.findAt(coordinates=((length,0,0),))
  part.Set(vertices=v1, name=boltEnd1SetName)
  part.Set(vertices=v2, name=boltEnd2SetName)
  
  ### Section part
  part.PartitionEdgeByPoint(edge=edges[0], point=part.InterestingPoint(edge=edges[0], 
      rule=MIDDLE))
  v3 = vertices.findAt(coordinates=((length/2.,0,0),))
  part.Set(vertices=v3, name='BoltTension')
  
  ### Assign Section
  region = part.sets['All']
  sectionName = scriptOwner+'BoltSection-M{}'.format(int(diameter*Units))
  part.SectionAssignment(region=region, sectionName=sectionName, offset=0.0, 
      offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
  part.assignBeamSectionOrientation(region=region, method=N1_COSINES, n1=(0., 0., 1.))
  
  # Create bolt tension surface
  edges = part.edges
  end2Edges = edges[0:1]
  part.Surface(end2Edges=end2Edges, name='BoltTension')
  
  #Mesh bolt
  e = part.edges
  pickedEdges = e.getSequenceFromMask(mask=e.getMask(), )
  part.seedEdgeByNumber(edges=pickedEdges, number=1, constraint=FINER)
  part.generateMesh()

def boltLength(lengthIn,boltLengthIncrement):
  return ceil(lengthIn/boltLengthIncrement)*boltLengthIncrement

def affixBolt(fastener,allBoltHoles, myWasherFaces, boltMaterialStress, pretensionStepName):
  #create faces
  stepsNames = model.steps.keys()
  temp1 = allBoltHoles[fastener['holes'][0]]
  temp2 = allBoltHoles[fastener['holes'][1]]
  hole1 = myWasherFaces[temp1[1]][temp1[2]]
  hole2 = myWasherFaces[temp2[1]][temp2[2]]
  facesList1 = [tuple([ra.instances[temp1[1]].faces[faceNum],hole1['centre']])  for faceNum in hole1['IDs']]
  facesList2 = [tuple([ra.instances[temp2[1]].faces[faceNum],hole2['centre']])  for faceNum in hole2['IDs']]
  namePrefix = scriptOwner+'Bolt-{}-M{}_'.format(fastener['boltNum'],fastener['diameter'] ) # Mod this naming if other fasteners are to be used
  createWasherSurfaces(facesList1, facesList2, namePrefix)  
  
  #Insert instance and place in correct position
  boltName = scriptOwner+'Bolt-M{}-{:0.1f}mm'.format(int(fastener['diameter']), fastener['length']*Units)
  boltName = ''.join([b if b !='.' else 'p' for b in boltName])
  instanceName = scriptOwner+'Bolt-{}-M{}-{:0.1f}mm'.format(fastener['boltNum'],int(fastener['diameter']), fastener['length']*Units)
  instanceName = ''.join([b if b !='.' else 'p' for b in instanceName])
  part = model.parts[boltName]
  ra.Instance(name=instanceName, part=part, dependent=ON)
#  offset = (fastener['length']-sum(fastener['offset'])-(hole1['centre']-hole2['centre']).length())/2+fastener['offset'][0]
  offset = fastener['washerOffset']+fastener['offset'][0]
  placeBolt(instanceName, hole1['centre'],hole2['centre'], offset = offset)
  #Create Coupling A on end 1
  couplingName= 'z-'+scriptOwner+'Bolt-{}-A'.format(fastener['boltNum'], temp1[1],temp2[1])
  region1=ra.surfaces['{}Face1'.format(namePrefix)]
  region2=ra.surfaces['{}Face2'.format(namePrefix)]
  boltend = ra.instances[instanceName].sets['End1'].vertices
  regionEnd = regionToolset.Region(vertices=boltend)    
  model.Coupling(name=couplingName, controlPoint=regionEnd, surface=region1,
                   influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, localCsys=None,
                   u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)
  #Create Coupling B on end 2
  couplingName= 'z-'+scriptOwner+'Bolt-{}-B'.format(fastener['boltNum'], temp1[1],temp2[1])
  boltend = ra.instances[instanceName].sets['End2'].vertices
  regionEnd = regionToolset.Region(vertices=boltend)    
  model.Coupling(name=couplingName, controlPoint=regionEnd, surface=region2,
                   influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, localCsys=None,
                   u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)
  stressArea = (fastener['diameter']**2.061724*0.505537)/Units**2
  pretension = (boltMaterialStress)*stressArea
  loadName = 'z-'+instanceName
  region = ra.instances[instanceName].surfaces['BoltTension']
  model.BoltLoad(name=loadName, createStepName=pretensionStepName,
                 region=region, magnitude=pretension, boltMethod=APPLY_FORCE)
  model.loads[loadName].setValuesInStep(stepName=stepsNames[2], boltMethod=FIX_LENGTH)

#============================= MAIN ======================================

def Main(modelName='', washerElsetName='', pretensionStepName='', boltMaterialProof='',
         boltMaterialPretension='',  boltInput='', boltLengthIncrement='', boltMaterialName='', UnitsSel='m'):

  global model, ra, Units, scriptOwner
  
  if UnitsSel == 'm':
    Units = 1000.
  else:
    Units = 1.
  
  
  model = mdb.models[modelName]
  ra = model.rootAssembly
  
  boltLengthIncrement = boltLengthIncrement/Units
  ### Basic constants
  tol = 0.001
  
  ### Deletes all bolt related components from the model
  
  for constraintKey in [key for key in model.constraints.keys() if 'z-'+scriptOwner+'Bolt-' in  key]:
    del model.constraints[constraintKey]
  for surfaceKey in [key for key in ra.surfaces.keys() if scriptOwner+'Bolt-' in  key]:
    del ra.surfaces[surfaceKey]
  for instanceKey in [key for key in ra.instances.keys() if scriptOwner+'Bolt-' in key]:
    del ra.instances[instanceKey]
  rePart = re.compile(scriptOwner+'Bolt-M(.*)-(.*)mm')
  for partName in [string for string in model.parts.keys() if re.match(rePart, string)]:
    del model.parts[partName]
  for sectionKey in [key for key in model.sections.keys() if scriptOwner+'BoltSection-M' in key]:
    del model.sections[sectionKey]
  for profileKey in [key for key in model.profiles.keys() if scriptOwner+'BoltProfile-M' in key]:
    del model.profiles[profileKey]  
  for loadKey in [key for key in model.loads.keys() if 'z-{}Bolt-'.format(scriptOwner) in  key]:
    del model.loads[loadKey]
  
  ### Ordered procedure 
  
  boltMaterialStress = boltMaterialProof*boltMaterialPretension
  
  boltDiamList =    [b[0] for b in boltInput]
  washerODList =    [b[1] for b in boltInput]
  washerThickList = [b[2] for b in boltInput]
  washers = {}  
  for b, w in zip(boltDiamList, washerThickList):
    washers['M{}'.format(int(b))] = w/Units
  
  ##Probe for all possible bolt holes using potential washer faces
  myWasherFaces = {}
  for instanceName, instance in ra.instances.items():
    try:
      tempSet = instance.sets[washerElsetName]
    except:
      tempSet = []
    if 'Set' in str(type(tempSet)):
      count = 0
      myWasherFaces[instanceName] = {}
      for washerDiameter, boltDiameter in zip(washerODList, boltDiamList):
#        print 'M{}, washer diam:{}'.format(str(boltDiameter),str(washerDiameter))
        temp,count = findWasherFaceClusters(instance,washerElsetName,washerDiameter/Units,count)
        for num, holeDict in temp.iteritems():
          myWasherFaces[instanceName][num] = holeDict
  
  allBoltHoles = []
  n = 0
  for instanceName, boltholes in myWasherFaces.iteritems():
    for bolthole in boltholes.keys():
      allBoltHoles += [[n, instanceName, bolthole]]
      n += 1
  
  ## Match bolt holes
  matchedBoltHoles = []
  unmatchedHoles = []
  notMidplaneFaces = []
  
  n = 1
  for holeNum, instanceName, boltholeKey in allBoltHoles:
    if holeNum not in [item for sublist in [i['holes'] for i in matchedBoltHoles] for item in sublist]:
      matchedBoltHoles = matchHole(holeNum, myWasherFaces, allBoltHoles, matchedBoltHoles,boltDiamList)
      
      if len(matchedBoltHoles[-1]['holes']) == 2:
  #      print '-'*5
        matchedBoltHoles[-1]['boltNum'] = n
        washerThick = washerThickList[boltDiamList.index(matchedBoltHoles[-1]['diameter'])]/Units #$#
        matchedBoltHoles[-1]['washerOffset'] = washerThick
        matchedBoltHoles[-1]['length'] = boltLength(matchedBoltHoles[-1]['length']+2.*washerThick,boltLengthIncrement)
        
        for holeNum in matchedBoltHoles[-1]['holes']:
          if myWasherFaces[allBoltHoles[holeNum][1]][allBoltHoles[holeNum][2]]['offset'] != 0.0:
            notMidplaneFaces  +=  [matchedBoltHoles[-1]['boltNum']]
        n += 1
      else:
        unmatchedHoles += matchedBoltHoles[-1]['holes']
        del matchedBoltHoles[-1]
  # Creates set with all unpaired potetial washer faces
  faces = []
  for holeNum in unmatchedHoles:
    instanceName = allBoltHoles[holeNum][1]
    washerFaceNum = allBoltHoles[holeNum][2]
    faceIDs = myWasherFaces[instanceName][washerFaceNum]['IDs']
    faces += [ra.instances[instanceName].faces[n] for n in faceIDs]
  
  faceSetList = []
  for face in faces:
    faceSetList.append(ra.instances[face.instanceName].faces[face.index:face.index+1])
  
  if len(faceSetList)>0:
    ra.Set(name='A - Unpaired Faces', faces=faceSetList)  
  
  #Create list of unique bolts in model
  boltPartsInModel= []
  for bolt in matchedBoltHoles:
  #  print bolt['diameter'], bolt['length']
    newBolt = [bolt['diameter'], bolt['length']]
    if newBolt not in boltPartsInModel:
      boltPartsInModel += [newBolt]
  
  
  ## Creates the required bolt sections and bolt part    
  for diameter in set([b[0] for b in boltPartsInModel]):
    createBoltSection(diameter/Units,boltMaterialName)
  
  for diameter, length in boltPartsInModel:  
    createBolt(length,diameter/Units)
  
  #Ensure preload and load steps are present
  stepsNames = model.steps.keys()
  if len(stepsNames) == 1:
    model.StaticStep(name=pretensionStepName, previous='Initial', initialInc=0.1)
    model.StaticStep(name='Step-1', previous=pretensionStepName,  initialInc=0.1)
  elif len(stepsNames) == 2 and stepsNames[1] == pretensionStepName:
    model.StaticStep(name='Step-1', previous=pretensionStepName, initialInc=0.1)
  elif len(stepsNames) > 1 and stepsNames[1] != pretensionStepName:
    model.StaticStep(name=pretensionStepName, previous='Initial', initialInc=0.1)
  
  stepsNames = model.steps.keys()
  
  # Create coupling beteeen bolt-ends and washer faces
  for fastener in matchedBoltHoles:
    affixBolt(fastener,allBoltHoles, myWasherFaces,boltMaterialStress,pretensionStepName)
  
#  notMidPlaneInstances = []
#  for boltNum in notMidplaneFaces:
#    notMidPlaneInstances += [key for key in ra.instances.keys() if 'Fastener-{}'.format(boltNum) in key]  
  # Feedback  
  boltInstanceNames = [key for key in ra.instances.keys() if scriptOwner+'Bolt' in key]
  report = []
  reportWidth = 45
  spacer_1 = '='*reportWidth
  spacer_2 = '-'*reportWidth
  if len(boltInstanceNames)>0:
    boltPartNames = [ra.instances[key].partName[len(scriptOwner)+5:] for key in boltInstanceNames]
    tempSort = np.array([x.split('-')+[boltPartNames.count(x)] for x in set(boltPartNames)]  )
    tempSort = tempSort[tempSort[:,1].argsort()]
    boltTable = tempSort[tempSort[:,0].argsort()]
    
    report +=  ['\n',spacer_1, 'Bolting Assist Feedback',spacer_1]
    if len(unmatchedHoles)>0:
      report +=  [fill('An assembly level set named "A - Unpaired faces" has been created with all unpared potential washer faces.\n',reportWidth),'']
      report += [spacer_2]
#    if len(notMidPlaneInstances)>0:
#      report +=  [fill('The following instances were created in region where midplane surfaces were not used.\nThe axial positioning of the bolt instances must be checked.\n\n',reportWidth),'']
#      report += notMidPlaneInstances
    report += ['',spacer_1]
    report += ['Bolts added to the assembly:\n']
    boltTableHeading = ['Size', 'Length', 'Qty']
    report += ['{:7s}{:>7s}{:>5s}'.format(*boltTableHeading)]
    nBolts = 0
    for b in boltTable:
      name = b[0]
      length = ''.join([c if c !='p' else '.' for c in b[1]][:-2])
      number = int(b[2])
      nBolts += number
      report += ['{:7s}{:>7s}{:5}'.format(name, length, number)]
    report += [' '*14+'-'*5]  
    report += ['{:7s}{:7s}{:5}'.format('TOTAL','',nBolts)]
    report += [spacer_1]
    
  else:
    report +=  [fill('An assembly level set named "A - Unpaired faces" has been created with all unpared potential washer faces.\n',reportWidth),'']
    report += [spacer_2]
    report += ['',spacer_1]
    report += [fill('No bolts were added to the model. Possible causes for this include:\n',reportWidth), \
               '- Incorrect units specified' ,
               '- Incorrect washer face partitioning',
               '- Incorrect washer face dimensions in the table',
               '- Absence of matched bolt holes\n']
    report += [spacer_1]
  report = '\n'.join(report)

  print report
  


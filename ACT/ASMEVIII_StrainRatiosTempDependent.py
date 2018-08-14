# script to compute triaxial strain limit for ferritic steels and 
# austinitic stainless steel for varying temperature in model

from abaqus import *
import assembly
from abaqusConstants import *
import numpy
from textRepr import prettyPrint as pp

def triaxialStrainLimitFerriticSteel(Sy, Suts, mises, press):
  """function to compute triaxial strain limit at a point 
     using constants appropriate for ferritic steel"""
  R = Sy/Suts
  M2 = 0.60*(1-R)
  E_Lu = M2
  strainLimit = E_Lu * exp(-(2.2/(1.+M2))*(-press/mises - 1.0/3.0))
  return strainLimit

def triaxialStrainLimitStainlessSteel(Sy, Suts, mises, press):
  """function to compute triaxial strain limit at a point
     using constants appropriate for stainless steel"""
  R = Sy/Suts
  M2 = 0.75*(1-R)
  E_Lu = M2
  strainLimit = E_Lu * exp(-(0.6/(1.+M2))*(-press/mises - 1.0/3.0))
  return strainLimit

def checkMyStrainLimit(elset):
  """check whether PEEQ is within strain limits """
  exceedList = []
  outputList = []
  maxStrainLimit = -1E32
  minStrainLimit =  1E32
  maxPEEQ = 0.0
  S = Stress.getSubset(region=elset)
  P = PEEQ.getSubset(region=elset)
  T = TEMP.getSubset(region=elset)
  PEEQList = [(i, peeq) for i, peeq in enumerate(P.values) if peeq.data > 0.]
  if PEEQList:
    maxPEEQ = max([val.data for i, val in PEEQList])
    for i, val in PEEQList:
       peeq = val.data
       s    = S.values[i]
       t    = T.values[i].data
       instanceName = s.instance.name
       elementLabel = s.elementLabel
       element = ra.instances[instanceName].getElementFromLabel(label=elementLabel)
       materialName = element.sectionCategory.name.split('< ')[1].split(' >')[0]
       if materialName == 'composite':
       	 materialName = 'SA-106B'
       if 'SA-240' in materialName:
       	 matType = 'Stainless'
       else:
       	 matType = 'Ferritic'
       Sy    = numpy.interp(t, materialProps[materialName].T_SY, materialProps[materialName].V_SY)
       Suts   = numpy.interp(t, materialProps[materialName].T_UTS, materialProps[materialName].V_UTS)
       if matType == 'Ferritic':
          strainLimit = triaxialStrainLimitFerriticSteel(Sy=Sy, Suts=Suts, mises=s.mises, press=s.press)
          if strainLimit > maxStrainLimit:
            maxStrainLimit = strainLimit
          if strainLimit < minStrainLimit:
            minStrainLimit = strainLimit
       elif matType == 'Stainless':
          strainLimit = triaxialStrainLimitStainlessSteel(Sy=Sy, Suts=Suts, mises=s.mises, press=s.press)
          if strainLimit > maxStrainLimit:
             maxStrainLimit = strainLimit
          if strainLimit < minStrainLimit:
             minStrainLimit = strainLimit
       #if peeq > strainLimit:
       #   exceedList.append((peeq, strainLimit, i, s.elementLabel))
       #   print i, s.mises, peeq, strainLimit
       outputList.append((strainLimit-peeq, strainLimit, peeq, t, materialName, i))
    print elset.name, min(outputList)
  return outputList, maxStrainLimit, minStrainLimit, maxPEEQ

class matProps():
  def __init__(self, T_SY, V_SY, T_UTS, V_UTS):
    self.T_SY = T_SY
    self.V_SY = V_SY
    self.T_UTS = T_UTS
    self.V_UTS = V_UTS

# define the yield and UTS in terms of temperature and stress values
SA_106B_T_SY = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  \
                425.,  450.,  475.,  500.,   525.]
SA_106B_V_SY = [241E6, 227E6, 220E6, 217E6, 214E6, 210E6, 207E6, 203E6, 198E6, 194E6, 188E6, 183E6, 177E6, 172E6, 167E6, \
                162E6, 158E6, 154E6, 150E6, 146E6,]
SA_106B_T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
SA_106B_V_UTS = [414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 408E6, 382E6, 352E6, 319E6, 285E6, 253E6,]


SA_204B_T_SY = [40.,   65.,   100.,   125.,   150.,   175.,   200.,   225.,   250.,   275.,   300.,   325.,   350.,   375.,   400.,   425.,   450.,   475.,   500.,   525.]
SA_204B_V_SY = [273E6, 266E6, 258E6, 253E6, 249E6, 245E6, 241E6, 237E6, 234E6, 231E6, 228E6, 224E6, 220E6, 216E6, 211E6, 207E6, 200E6, 194E6, 187E6, 179E6,]

SA_204B_T_UTS = [40.,   100.,   150.,   200.,   250.,   300.,   325.,   350.,   375.,   400.,   425.,   450.,   475.,   500.,   525.]
SA_204B_V_UTS = [483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 474E6, 455E6, 432E6, 404E6,]


SA_240_316_T_SY = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  \
                   425.,   450.,   475.,   500.,   525.]
SA_240_316_V_SY = [172E6, 157E6, 145E6, 137E6, 131E6, 125E6, 121E6, 118E6, 114E6, 111E6, 109E6, 107E6, 105E6, 103E6, 101E6, \
                   99.4E6, 97.5E6, 95.7E6, 93.8E6, 92.0E6,]
SA_240_316_T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
SA_240_316_V_UTS = [483E6, 467E6, 441E6, 429E6, 426E6, 426E6, 425E6, 425E6, 424E6, 421E6, 417E6, 413E6, 406E6, 398E6, 387E6,]

materialProps = {}
materialProps['SA-106B']    = matProps(SA_106B_T_SY,    SA_106B_V_SY,    SA_106B_T_UTS,    SA_106B_V_UTS)
materialProps['SA-204B']    = matProps(SA_204B_T_SY,   SA_204B_V_SY,   SA_204B_T_UTS,   SA_106B_V_UTS)
materialProps['SA-240_316'] = matProps(SA_240_316_T_SY, SA_240_316_V_SY, SA_240_316_T_UTS, SA_240_316_V_UTS)

# define the current viewport and ODB visible in it
VP = session.viewports[session.currentViewportName]
odb = VP.displayedObject
ra = odb.rootAssembly

# use the last step and frame in the analysis
stepName = odb.steps.keys()[-1]
Stress   = odb.steps[stepName].frames[-1].fieldOutputs['S'].getSubset(position = ELEMENT_NODAL)
PEEQ     = odb.steps[stepName].frames[-1].fieldOutputs['PEEQ'].getSubset(position = ELEMENT_NODAL)
TEMP     = odb.steps[stepName].frames[-1].fieldOutputs['TEMP'].getSubset(position = ELEMENT_NODAL)

elsetList = [ra.instances['COIL1-1'],
             ra.instances['COIL2-1'], 
             ra.instances['COIL3-1'], 
             ra.instances['COIL4-1'],
             ra.instances['OUTERTUBE-1']]

for elset in elsetList:
   outputList,maxStrainLimit, minStrainLimit, maxPEEQ = checkMyStrainLimit(elset)


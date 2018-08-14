# script to define material properties according to ASME 2
from abaqus import *
import assembly
from abaqusConstants import *
from part import PartType
from assembly import AssemblyType
from visualization import OdbType
import numpy
from textRepr import prettyPrint as pp

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
  ra = model.rootAssembly
  print 'Found Assembly Type'
elif type(displayedObject) == OdbType:
  odb = displayedObject
  print 'Found ODB Type'


def trueStrainValue(St, SY, UTS):
  """return the true plastic strain for a specified 
     true stress value,using ASME VIII Div II Annex 3.D.3 """
  E_1 = (St/A_1)**(1/M_1)
  E_2 = (St/A_2)**(1/M_2)
  H   = 2*(St - (SY+K*(UTS-SY)))/(K*(UTS-SY))
  G_1 = E_1*(1-tanh(H))/2.0
  G_2 = E_2*(1+tanh(H))/2.0
  Et  = G_1 + G_2
  return Et

def stressStrainCurveCarbonSteel(data, SY, UTS, Temp=None):
  """return the post-yield stress strain curve for ferrous metal with C<0.3
     using ASME VIII Div II Annex 3.D.3 """
  global A_1, A_2, M_1, M_2, K
  n = 10                       # number of values in piecewise linear curve
  Eys = 0.002
  Ep  = 2E-5
  R = SY/UTS
  K = 1.5*R**1.5 - 0.5*R**2.5 - R**3.5
  M_1 = (log(R) + (Ep - Eys))/log(log(1+Ep)/log(1+Eys))
  M_2 = 0.6*(1-R)
  UTSt = UTS*exp(M_2)
  A_1 = SY*(1+Eys)/((log(1+Eys))**M_1)
  A_2 = UTS*exp(M_2)/(M_2**M_2)
  dS = (UTSt - SY*(1+Eys))/n
  for i in range(n):
    St = SY*(1+Eys) + i*dS
    if  i == 0:
    	Et = 0.0
    else:
    	Et = trueStrainValue(St, SY, UTS)
    if Temp:
      data.append((St, Et, Temp))
    else:
      data.append((St, Et))
  return data

def stressStrainCurveStainless(data, SY, UTS, Temp=None):
  """return the post-yield stress strain curve for stainless steel
     using ASME VIII Div II Annex 3.D.3 """
  global A_1, A_2, M_1, M_2, K
  n = 10                       # number of values in piecewise linear curve
  Eys = 0.002
  Ep  = 2E-5
  R = SY/UTS
  K = 1.5*R**1.5 - 0.5*R**2.5 - R**3.5
  M_1 = (log(R) + (Ep - Eys))/log(log(1+Ep)/log(1+Eys))
  M_2 = 0.75*(1-R)
  UTSt = UTS*exp(M_2)
  A_1 = SY*(1+Eys)/((log(1+Eys))**M_1)
  A_2 = UTS*exp(M_2)/(M_2**M_2)
  dS = (UTSt - SY*(1+Eys))/n
  for i in range(n):
    St = SY*(1+Eys) + i*dS
    if  i == 0:
    	Et = 0.0
    else:
    	Et = trueStrainValue(St, SY, UTS)
    if Temp:
      data.append((St, Et, Temp))
    else:
      data.append((St, Et))
  return data

def createCarbonSteelMaterialProperty(name, density, PoissonsR, (V_E, T_E), (V_Y, T_Y), (V_UTS, T_UTS)):
  """function to define material property based on ASME II Part D"""
  mat = model.Material(name=name)
  mat.Density(table=((density, ), ))
  PoissonList = [PoissonsR for i in range(len(V_E))]
  mat.Elastic(temperatureDependency=ON, table=zip(V_E, PoissonList, T_E))
  data = []
  for temp in T_UTS:
    SY  = numpy.interp(temp, T_Y,  V_Y)
    UTS = numpy.interp(temp, T_UTS, V_UTS)
    newData = stressStrainCurveCarbonSteel(data=data, SY=SY, UTS=UTS, Temp=temp)
    data = newData
  mat.Plastic(temperatureDependency=ON, table=data)
  

def createStainlessSteelMaterialProperty(name, density, PoissonsR, (V_E, T_E), (V_Y, T_Y), (V_UTS, T_UTS)):
  """function to define material property based on ASME II Part D"""
  mat = model.Material(name=name)
  mat.Density(table=((density, ), ))
  PoissonList = [PoissonsR for i in range(len(V_E))]
  mat.Elastic(temperatureDependency=ON, table=zip(V_E, PoissonList, T_E))
  data = []
  for temp in T_UTS:
    SY  = numpy.interp(temp, T_Y,  V_Y)
    UTS = numpy.interp(temp, T_UTS, V_UTS)
    newData = stressStrainCurveStainless(data=data, SY=SY, UTS=UTS, Temp=temp)
    data = newData
  mat.Plastic(temperatureDependency=ON, table=data)
  

##########################################################################
# Young's modulus

# Carbon steels with C <= 0.3%
T_E = [-200., -125., -75.,  25.,    100., 150.,   200.,  250., 300.,  350.,  400.,  450.,   500., 550.]
V_E = [216E9, 212E9, 209E9, 202E9, 198E9, 195E9, 192E9, 189E9, 185E9, 179E9, 171E9, 162E9, 151E9, 137E9]

# Material group G
T_E = [-200., -125., -75.,  25.,   100.,   150., 200.,  250.,  300.,  350.,  400.,  450.,  500.,  550.,  600.,  650.,  700.]
V_E = [209E9, 204E9, 201E9, 195E9, 189E9, 186E9, 183E9, 179E9, 176E9, 172E9, 169E9, 165E9, 160E9, 156E9, 151E9, 146E9, 140E9,]

##########################################################################
# Thermal expansion coefficient (Column B)

# Group 1
T_Exp = [20.,     50.,     75.,     100.,    125.,   150.,    175.,    200.,    225.,    250.,    275.,    300.,    325.,    \
         350.,    375.,    400.,    425.,    450.,    475.,    500.,    525.,    550.,     575.,    600.,    625.,    650.,  \
         675.,    700.,    725.,    750.,    775.,    800.,    825.]
V_Exp = [11.5E-6, 11.8E-6, 11.9E-6, 12.1E-6, 12.3E-6, 12.4E-6, 12.6E-6, 12.7E-6, 12.9E-6, 13.0E-6, 13.2E-6, 13.3E-6, 13.4E-6, \
         13.6E-6, 13.7E-6, 13.8E-6, 14.0E-6, 14.1E-6, 14.2E-6, 14.4E-6, 14.5E-6, 14.6E-6,  14.7E-6, 14.8E-6, 14.9E-6, 15.0E-6,\
         15.1E-6, 15.1E-6, 15.2E-6, 15.3E-6, 15.3E-6, 15.4E-6, 15.5E-6] 

# Group 3
T_Exp = [20., 50., 75., 100., 125., 150., 175., 200., 225., 250., 275., 300., 325., 350., 375., 400., 425., 450., 475., 500., 525., 550., 575., 600., 625., 650., 675., 700., 725., 750., 775., 800., 825.,]
V_Exp = [15.3E-6, 15.6E-6, 15.9E-6, 16.2E-6, 16.4E-6, 16.6E-6, 16.8E-6, 17.0E-6, 17.2E-6, 17.4E-6, 17.5E-6, 17.7E-6, 17.8E-6, 17.9E-6, 18.0E-6, 18.1E-6, 18.2E-6, 18.3E-6, 18.4E-6, 18.4E-6, 18.5E-6, 18.6E-6, 18.7E-6, 18.8E-6, 18.9E-6, 19.0E-6, 19.1E-6, 19.2E-6, 19.3E-6, 19.4E-6, 19.4E-6, 19.4E-6, 19.4E-6,]


##########################################################################
# Yield strength

# SA-36 (Bar)
T_Y = [40.,    65.,   100.,  125., 150.,   175., 200.,   225., 250.,   275., 300.,  325.,   350., 375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_Y = [248E6, 233E6, 227E6, 223E6, 219E6, 216E6, 213E6, 209E6, 204E6, 199E6, 194E6, 188E6, 183E6, 177E6, 171E6, 166E6, 162E6, 158E6, 154E6, 150E6,]

# SA-333 Grade 6 (Pipe)
T_Y = [40.,    65.,   100.,  125., 150.,   175., 200.,   225., 250.,   275., 300.,  325.,   350., 375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_Y = [241E6, 227E6, 220E6, 217E6, 214E6, 210E6, 207E6, 203E6, 198E6, 194E6, 188E6, 183E6, 177E6, 172E6, 167E6, 162E6, 158E6, 154E6, 150E6, 146E6,]

# SA-106 A
T_Y = [40.,    65.,   100.,  125., 150.,   175., 200.,   225., 250.,   275., 300.,  325.,   350., 375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_Y = [207E6, 195E6, 189E6, 186E6, 183E6, 180E6, 177E6, 174E6, 170E6, 166E6, 161E6, 157E6, 152E6, 148E6, 143E6, 139E6, 135E6, 132E6, 128E6, 125E6,]  


# SA-106 B
T_Y = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,   525.]
V_Y = [241E6, 227E6, 220E6, 217E6, 214E6, 210E6, 207E6, 203E6, 198E6, 194E6, 188E6, 183E6, 177E6, 172E6, 167E6, 162E6, 158E6, 154E6, 150E6, 146E6,]

# SA-204 Grade B
T_Y = [40.,   65.,   100.,   125.,   150.,   175.,   200.,   225.,   250.,   275.,   300.,   325.,   350.,   375.,   400.,   425.,   450.,   475.,   500.,   525.]
V_Y = [273E6, 266E6, 258E6, 253E6, 249E6, 245E6, 241E6, 237E6, 234E6, 231E6, 228E6, 224E6, 220E6, 216E6, 211E6, 207E6, 200E6, 194E6, 187E6, 179E6,]

# SA-516 Grade 55
T_Y = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,   525.]
V_Y = [207E6, 195E6, 189E6, 186E6, 183E6, 180E6, 177E6, 174E6, 170E6, 166E6, 161E6, 157E6, 152E6, 148E6, 143E6, 139E6, 135E6, 132E6, 128E6, 125E6,]

# SA-516 Grade 60
T_Y = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,   525.]
V_Y = [221E6, 208E6, 201E6, 198E6, 195E6, 192E6, 189E6, 185E6, 182E6, 177E6, 172E6, 167E6, 162E6, 157E6, 153E6, 149E6, 144E6, 140E6, 137E6, 133E6,]

# SA-516 Grade 65
T_Y = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,   525.]
V_Y = [241E6, 227E6, 220E6, 217E6, 214E6, 210E6, 207E6, 203E6, 198E6, 194E6, 188E6, 183E6, 177E6, 172E6, 167E6, 162E6, 158E6, 154E6, 150E6, 146E6,]

# SA-516 Grade 70
T_Y = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,   525.]
V_Y = [262E6, 246E6, 239E6, 235E6, 232E6, 228E6, 225E6, 221E6, 216E6, 210E6, 204E6, 199E6, 193E6, 187E6, 181E6, 176E6, 171E6, 167E6, 162E6, 158E6,]

# SA-240 304L (Plate)
T_Y = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,   475.,   500.,   525.]
V_Y = [172E6, 157E6, 146E6, 138E6, 132E6, 126E6, 121E6, 117E6, 114E6, 111E6, 108E6, 106E6, 104E6, 103E6, 101E6, 100E6, 98.9E6, 97.1E6, 95.2E6, 93.0E6,]

# SA-240 304 (Plate)
T_Y = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,   475., 500.,  525.]
V_Y = [207E6, 184E6, 170E6, 161E6, 154E6, 148E6, 144E6, 139E6, 135E6, 132E6, 129E6, 126E6, 123E6, 121E6, 118E6, 117E6, 114E6, 112E6, 110E6, 108E6,]

# SA-240 316L (Plate)
T_Y = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  425.,   450.,   475.,   500.,   525.]
V_Y = [172E6, 157E6, 145E6, 137E6, 131E6, 125E6, 121E6, 118E6, 114E6, 111E6, 109E6, 107E6, 105E6, 103E6, 101E6, 99.4E6, 97.5E6, 95.7E6, 93.8E6, 92.0E6,]

# SA-240 316 (Plate)
T_Y = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_Y = [207E6, 189E6, 176E6, 168E6, 161E6, 154E6, 148E6, 144E6, 139E6, 136E6, 132E6, 129E6, 127E6, 125E6, 123E6, 122E6, 121E6, 120E6, 118E6, 117E6,]


##########################################################################
# Tensile strength

# SA-36 (Bar)
T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [400E6, 400E6, 400E6, 400E6, 400E6, 400E6, 400E6, 400E6, 400E6, 394E6, 369E6, 340E6, 308E6, 275E6, 245E6,]

# SA-333 Grade 6 (Pipe)
T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 408E6, 382E6, 352E6, 319E6, 285E6, 253E6,]

# SA-106 A
T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [331E6, 331E6, 331E6, 331E6, 331E6, 331E6, 331E6, 331E6, 331E6, 326E6, 306E6, 282E6, 255E6, 227E6, 203E6,]


# SA-106 B
T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 408E6, 382E6, 352E6, 319E6, 285E6, 253E6,]

# SA-204 Grade B
T_UTS = [40.,   100.,   150.,   200.,   250.,   300.,   325.,   350.,   375.,   400.,   425.,   450.,   475.,   500.,   525.]
V_UTS = [483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 474E6, 455E6, 432E6, 404E6,]

# SA-516 Grade 55
T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [379E6, 379E6, 379E6, 379E6, 379E6, 379E6, 379E6, 379E6, 379E6, 374E6, 350E6, 322E6, 292E6, 261E6, 232E6,]

# SA-516 Grade 60
T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 408E6, 382E6, 352E6, 319E6, 285E6, 253E6,]

# SA-516 Grade 65
T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [448E6, 448E6, 448E6, 448E6, 448E6, 448E6, 448E6, 448E6, 448E6, 442E6, 414E6, 381E6, 345E6, 308E6, 274E6,]

# SA-516 Grade 70
T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 476E6, 446E6, 411E6, 372E6, 332E6, 296E6,]

# SA-240 304L
T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [483E6, 452E6, 421E6, 406E6, 398E6, 393E6, 392E6, 391E6, 389E6, 386E6, 382E6, 377E6, 372E6, 364E6, 355E6,]

# SA-240 304
T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [517E6, 485E6, 456E6, 442E6, 437E6, 437E6, 437E6, 437E6, 437E6, 436E6, 433E6, 429E6, 422E6, 413E6, 402E6,]

# SA-240 316L
T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [483E6, 467E6, 441E6, 429E6, 426E6, 426E6, 425E6, 425E6, 424E6, 421E6, 417E6, 413E6, 406E6, 398E6, 387E6,]

# SA-240 316
T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [517E6, 516E6, 502E6, 496E6, 495E6, 495E6, 495E6, 495E6, 495E6, 493E6, 489E6, 482E6, 474E6, 463E6, 450E6,]


###############################################################################################################
# CREATE MATERIALS
###############################################################################################################

# SA-36
name = 'SA-36'
density = 7850.
PoissonsR = 0.3

# Carbon steels with C <= 0.3%
T_E = [-200., -125., -75.,  25.,    100., 150.,   200.,  250., 300.,  350.,  400.,  450.,   500., 550.]
V_E = [216E9, 212E9, 209E9, 202E9, 198E9, 195E9, 192E9, 189E9, 185E9, 179E9, 171E9, 162E9, 151E9, 137E9]

T_Y = [40.,    65.,   100.,  125., 150.,   175., 200.,   225., 250.,   275., 300.,  325.,   350., 375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_Y = [248E6, 233E6, 227E6, 223E6, 219E6, 216E6, 213E6, 209E6, 204E6, 199E6, 194E6, 188E6, 183E6, 177E6, 171E6, 166E6, 162E6, 158E6, 154E6, 150E6,]

T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [400E6, 400E6, 400E6, 400E6, 400E6, 400E6, 400E6, 400E6, 400E6, 394E6, 369E6, 340E6, 308E6, 275E6, 245E6,]

createCarbonSteelMaterialProperty(name, density, PoissonsR, (V_E, T_E), (V_Y, T_Y), (V_UTS, T_UTS))

# SA-333 Gr6 
name = 'SA-333 Gr 6'
density = 7850.
PoissonsR = 0.3

# Carbon steels with C <= 0.3%
T_E = [-200., -125., -75.,  25.,    100., 150.,   200.,  250., 300.,  350.,  400.,  450.,   500., 550.]
V_E = [216E9, 212E9, 209E9, 202E9, 198E9, 195E9, 192E9, 189E9, 185E9, 179E9, 171E9, 162E9, 151E9, 137E9]

T_Y = [40.,    65.,   100.,  125., 150.,   175., 200.,   225., 250.,   275., 300.,  325.,   350., 375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_Y = [241E6, 227E6, 220E6, 217E6, 214E6, 210E6, 207E6, 203E6, 198E6, 194E6, 188E6, 183E6, 177E6, 172E6, 167E6, 162E6, 158E6, 154E6, 150E6, 146E6,]

T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 414E6, 408E6, 382E6, 352E6, 319E6, 285E6, 253E6,]

createCarbonSteelMaterialProperty(name, density, PoissonsR, (V_E, T_E), (V_Y, T_Y), (V_UTS, T_UTS))


# SA-516 Gr 70 
name = 'SA-516 Gr 70'
density = 7850.
PoissonsR = 0.3

# Carbon steels with C <= 0.3%
T_E = [-200., -125., -75.,  25.,    100., 150.,   200.,  250., 300.,  350.,  400.,  450.,   500., 550.]
V_E = [216E9, 212E9, 209E9, 202E9, 198E9, 195E9, 192E9, 189E9, 185E9, 179E9, 171E9, 162E9, 151E9, 137E9]

T_Y = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,   525.]
V_Y = [262E6, 246E6, 239E6, 235E6, 232E6, 228E6, 225E6, 221E6, 216E6, 210E6, 204E6, 199E6, 193E6, 187E6, 181E6, 176E6, 171E6, 167E6, 162E6, 158E6,]

T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 483E6, 476E6, 446E6, 411E6, 372E6, 332E6, 296E6,]

createCarbonSteelMaterialProperty(name, density, PoissonsR, (V_E, T_E), (V_Y, T_Y), (V_UTS, T_UTS))


# SA-240 Grade 304L 
name = 'SA-240 Grade 304L'
density = 8000.
PoissonsR = 0.3

# Material group G
T_E = [-200., -125., -75.,  25.,   100.,   150., 200.,  250.,  300.,  350.,  400.,  450.,  500.,  550.,  600.,  650.,  700.]
V_E = [209E9, 204E9, 201E9, 195E9, 189E9, 186E9, 183E9, 179E9, 176E9, 172E9, 169E9, 165E9, 160E9, 156E9, 151E9, 146E9, 140E9,]

T_Y = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,   475.,   500.,   525.]
V_Y = [172E6, 157E6, 146E6, 138E6, 132E6, 126E6, 121E6, 117E6, 114E6, 111E6, 108E6, 106E6, 104E6, 103E6, 101E6, 100E6, 98.9E6, 97.1E6, 95.2E6, 93.0E6,]

T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [483E6, 452E6, 421E6, 406E6, 398E6, 393E6, 392E6, 391E6, 389E6, 386E6, 382E6, 377E6, 372E6, 364E6, 355E6,]

createStainlessSteelMaterialProperty(name, density, PoissonsR, (V_E, T_E), (V_Y, T_Y), (V_UTS, T_UTS))






# SA-240 Grade 316L 
name = 'SA-240 Grade 316L'
density = 8000.
PoissonsR = 0.3

# Material group G

T_E = [-200., -125., -75.,  25.,   100.,   150., 200.,  250.,  300.,  350.,  400.,  450.,  500.,  550.,  600.,  650.,  700.]
V_E = [209E9, 204E9, 201E9, 195E9, 189E9, 186E9, 183E9, 179E9, 176E9, 172E9, 169E9, 165E9, 160E9, 156E9, 151E9, 146E9, 140E9,]

T_Y = [40.,   65.,   100.,  125.,  150.,  175.,  200.,  225.,  250.,  275.,  300.,  325.,  350.,  375.,  400.,  425.,   450.,   475.,   500.,   525.]
V_Y = [172E6, 157E6, 145E6, 137E6, 131E6, 125E6, 121E6, 118E6, 114E6, 111E6, 109E6, 107E6, 105E6, 103E6, 101E6, 99.4E6, 97.5E6, 95.7E6, 93.8E6, 92.0E6,]

T_UTS = [40.,   100,   150.,  200.,  250.,  300.,  325.,  350.,  375.,  400.,  425.,  450.,  475.,  500.,  525.]
V_UTS = [483E6, 467E6, 441E6, 429E6, 426E6, 426E6, 425E6, 425E6, 424E6, 421E6, 417E6, 413E6, 406E6, 398E6, 387E6,]

createStainlessSteelMaterialProperty(name, density, PoissonsR, (V_E, T_E), (V_Y, T_Y), (V_UTS, T_UTS))



















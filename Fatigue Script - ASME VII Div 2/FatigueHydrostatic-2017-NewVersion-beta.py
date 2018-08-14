# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 09:14:03 2016

@author: feas

ASME VIII Div 2 Fatigue calcs


It is very important to:
    - Add the correct material data in the Section V.1. of this script.
    - Update the function 4 in Section IV. according to ASME BPVC.VIII.2-2017 Annex 3-F.1.2; Add the name of the material in the right place.
    - Check that the right set of parameters is selected in Section V.2.

    I.      Imports
    
    II.     Odb Files Paths
    
    III.    Suppress previous files
    
    IV.     Initialization of classes and functions
        1. Material Properties
        2. Loading
        3. Eval of parameter X
        4. Damage evaluation
        5. von Mises Stress Calculations
        6. Fatigue penalty factor, Kek
        7. Allowable limit on the primary plus secondary stress range, Sps
        
    V.      Initialization of Parameters
        1. Mechanical Properties
        2. Other parameters
        
    VI.     ODB files Selection
    
    VII.    Steps selection
    
    VIII.   Frames selection
    
    IX.     Creation of the fatigue Step and its Frames
    
    X.      Creation of the Stress Differences
    
    XI.     Loading Definition
    
    XII.    List of instances
    
    XIII.   Creation of a dictionary of elements containing the material names
    
    XIV.    Sections
    
    XV.     Main Loop
    
    XVI.    Save and Finish
    
    XVII.   Notes on this code
    
"""
#################################################################################
# I. Imports 
#################################################################################

from caeModules import *
from textRepr import prettyPrint as pp
from VectorModule import Vector
#import pickle

from abaqus import *
from abaqusConstants import *
from textRepr import prettyPrint as pp
import sys, os, csv, shutil
import numpy as np
#from numpy import NaN, Inf, arange, isscalar, asarray, array, math,random
from caeModules import *
from part import *
from assembly import *
from visualization import *
import timeit
import time
import cPickle
import pickle


from operator import itemgetter


print '\n\n\nStart \n'
t0 = timeit.default_timer()
tic = time.time()

showStopButtonInGui()

#################################################################################
# II. Odb Files Paths                                                           #
#################################################################################

currDir = os.getcwd()

# Select all odb files in the current directory
odbNameList = [f for f in os.listdir('.') if f.endswith('.odb')]

#odbAccPath     = r'H:\Consult\UniqueHydra\2016\SPHL 18\SPHL18-Fatigue-H-Acc-P.odb'
#odbThermPath   = r'H:\Consult\UniqueHydra\2016\SPHL 18\SPHL18-Fatigue-H-Thermal.odb'
#odbPressPath   = r'H:\Consult\UniqueHydra\2016\SPHL 18\SPHL18-Fatigue-H-Pressure.odb'
#odbHydroPath   = r'H:\Consult\UniqueHydra\2016\SPHL 18\SPHL18-Fatigue-A-Hydrostatic.odb'
#resultsPath    = r'H:\Consult\UniqueHydra\2016\SPHL 18\SavedFields\SPHL24-Fatigue-H-Results.odb'
resultsPath     = currDir+'\\SavedFields\\\ResultFields.odb'


#################################################################################
# III. Suppress previous files                                                  #
#################################################################################

# Close previous fatigue resultsOdb
try:
    odbResults = session.odbs[resultsPath]
    odbResults.close()
except:
    pass

# Remove lock files
for odbFile in odbNameList:
    odbPath = currDir+'\\'+odbFile
    try: 
        os.remove(odbPath.replace('.odb','.lck'))
    except:
        pass

# Suppress and Create Result Directory
try:
    shutil.rmtree('SavedFields')
except:
    pass

os.mkdir('SavedFields')


#################################################################################
# IV. Initialization of classes and functions                                   #
#################################################################################

# 1.    Material Properties
class matProps():
    """Each material is classified and its properties are stored as methods"""
    def __init__(self, T_SY, V_SY, T_UTS, V_UTS, T_E, V_E, T_Smax = [0], V_Smax = [0]):
        self.T_SY = T_SY
        self.V_SY = V_SY
        self.T_UTS = T_UTS
        self.V_UTS = V_UTS
        self.T_E = T_E
        self.V_E = V_E
        self.T_Smax = T_Smax
        self.V_Smax = V_Smax

# 2.    Loading
class Loading():
    """Each load case is classified and its specifications and results are stored as methods"""
    def __init__(self, nDesign, temp, stress, x=1):
        self.nDesign = nDesign
        self.temp = temp
        self.stress = stress
        self.x = x

# 3.    Eval of parameter X
# N = design number of design cycles
def intPointFLife_a1(Y):
    ## 3-F.1.2 (a) (1)
    if 10**Y >= 20:
        exponent = (-4706.5245 + 1813.6228*Y + 6785.5644/Y - 368.12404*Y**2 - 5133.7345/Y**2 + 30.708204*Y**3 + 1596.1916/Y**3)     # Eq (3-F.2)
    elif 10**Y < 20:
        exponent = (38.1309 - 60.1705*Y**2 + 25.0352*Y**4)/(1 + 1.80224*Y**2 - 4.68904*Y**4 +2.26536*Y**6)                          # Eq (3-F.3)
    
    if exponent>11.0:
        exponent = 11.0
    return exponent

def intPointFLife_a2(Y):
    ## 3-F.1.2 (a) (2)
    if 10**Y >= 43:
        exponent = (5.37689 - 5.25401*Y + 1.14427*Y**2)/(1 - 0.960816*Y + 0.291399*Y**2 - 0.0562968*Y**3)       # Eq (3-F.4)
        
    elif 10**Y < 43:
        exponent = (-9.41749 + 14.7982*Y - 5.94*Y**2)/(1 - 3.46282*Y + 3.63495*Y**2 - 1.21849*Y**3)             # Eq (3-F.5)
    
    if exponent>11.0:
        exponent = 11.0
    return exponent
    
def intPointFLife_b(Y):
    ## 3-F.1.2 (b)
    if 10**Y >= 14.4:
        exponent = (17.0181 - 19.8713*Y + 4.21366*Y**2)/(1 - 0.1720606*Y - 0.633592*Y**2)       # Eq (3-F.7)
    elif 10**Y <14.4:
        exponent = (-0.331096 + ((4.3261*log(Y))/(Y**2)))**-1                                     # Eq (3-F.8)
    
    if exponent>11.0:
        exponent = 11.0
    if exponent<0:
        print "oups"
        print Y, exponent
    
    return exponent

def intPointFLife_c1(Y):
    ## 3-F.1.2 (c) (1)
    exponent = -2.632 + (0.1186/log(Y)) + (15.12*log(Y)/Y**2) + (7.087/Y**2)       # Eq (3-F.10)
    
    if exponent<0:
        print exponent
    if exponent>11.0:
        exponent = 11.0
    return exponent
    
def intPointFLife_c2(Y):
    ## 3-F.1.2 (c) (2)
    if 10**Y >= 24.5:
        exponent = 8.580044 - 1.889784*Y - (8.261383*log(Y)/Y)       # Eq (3-F.11)
    elif 10**Y < 24.5:
        exponent = 5.89029 - 0.2280247*Y - (6.649501*log(Y)/Y)       # Eq (3-F.12)
    
    if exponent>11.0:
        exponent = 11.0        
    return exponent

def intPointFLife_c3(Y):
    ## 3-F.1.2 (c) (3)
    if 10**Y >= 46:
        exponent = -884.9989 + (8936.214/Y) - (36034.88/Y**2) + (72508.69/Y**3) - (72703.36/Y**4) + (29053.66/Y**5)       # Eq (3-F.13)
    elif 10**Y < 46:
        exponent = -17.50197 + (109.168/Y) - (236.7921/Y**2) + (257.9938/Y**3) - (137.1654/Y**4) + (28.55546/Y**5)        # Eq (3-F.14)
    
    if exponent>11.0:
        exponent = 11.0
    return exponent

def intPointFLife_d(Y):
    ## 3-F.1.2 (d)
    if 10**Y >= 35.9:
        exponent = (-42.08579 + 12.514054*Y)/(1 - 4.3290016*Y + 0.60540862*Y**2)
    elif 10**Y < 35.9:
        exponent = (9.030556 - 8.1906623*Y)/(1 - 0.36077181*Y - 0.47064984*Y**2)
    
    if exponent>11.0:
        exponent = 11.0
    return exponent

# 4.    Damage evaluation    
def elementDamage2017(S_element, Et, materialName, UTSt, nDesign=1.):
    ## 3.F.1.2
    ## All Stress values are in MPa 
    ## UTSt, Y, S, Et
    
    Cusm = 6.895                                    # Sa must be in ksi in order to evaluate Y
    
    damageList = []
    if materialName == 'S355-ELAST':                # 3-F.1.2 (a) Carbon, Low Alloy, Series 4XX, High Alloy, and High Tensile Strength Steels
        for S in S_element:
            Y = log10(195.0E3*(S/(Et*Cusm)))
            if UTSt <= 552 and S>40:                                # 3-F.1.2 (a) (1)
                damage          = nDesign/(10**intPointFLife_a1(Y))
                damageList      += [damage]
            elif UTSt >= 793 and UTSt <= 892 and S>40:              # 3-F.1.2 (a) (2)
                damage          = nDesign/(10**intPointFLife_a2(Y))
                damageList      += [damage]
            elif UTSt > 552 and UTSt < 793 and S>40:                # The fatigue curve values may be interpolated for intermediate values of the ultimate tensile strength.
                UTSList         = [552,               793]
                exponentList    = [intPointFLife_a1(Y), intPointFLife_a2(Y)]
                damage          = nDesign/(10**np.interp(UTSt, UTSList, exponentList))
                damageList      += [damage]
            elif UTSt < 793 and S<=40:                              # Values of stresses below the curve in Fig. 3-F.1M not considered for damage calculations
                damage          = nDesign/(10.**11)
                damageList      += [damage]
            else :
                print "UTSt is out of the norm's applicable bracket"
    
    elif materialName == 'SA-240 Grade-304-Elast' or materialName == 'SA-240 Grade-304-PS-Elast': # 3-F.1.2 (b) Series 3XX High Alloy Steels, Nickel-Chromium-Iron Alloy, Nickel-Iron-Chromium Alloy, and Nickel-Copper Alloy
        for S in S_element:
            Y = log10(195.0E3*(S/(Et*Cusm)))
            if S>95:
                damage          = nDesign/(10**intPointFLife_b(Y)) 
                damageList      += [damage]
            elif S<=95:
                damage          = nDesign/(10**11)
                damageList      += [damage]
    
    elif materialName == '':                            # 3-F.1.2 (c) Wrought 70-30 Copper-Nickel
        for S in S_element:
            Y = log10(138.0E3*(S/(Et*Cusm)))
            if UTSt <= 134 and S>30:                                               # 3-F.1.2 (c) (1)
                damage          = nDesign/(10**intPointFLife_c1(Y))
                damageList      += [damage]
            elif UTSt == 207 and S>30:                                             # 3-F.1.2 (c) (2)
                damage          = nDesign/(10**intPointFLife_c2(Y))
                damageList      += [damage]
            elif UTSt == 310 and S>30:                                             # 3-F.1.2 (c) (3)
                damage          = nDesign/(10**intPointFLife_c3(Y))
                damageList      += [damage]
            elif UTSt > 134 and UTSt < 207 and S>30:                             # Interpolation
                UTSList         = [134,               207]
                exponentList    = [intPointFLife_c1(Y), intPointFLife_c2(Y)]
                damage          = nDesign/(10**np.interp(UTSt, UTSList, exponentList))
                damageList      += [damage]
            elif UTSt > 207 and UTSt < 310 and S>30:                             # Interpolation
                UTSList         = [207,               310]
                exponentList    = [intPointFLife_c2(Y), intPointFLife_c3(Y)]
                damage          = nDesign/(10**np.interp(UTSt, UTSList, exponentList))
                damageList      += [damage]
            elif UTSt<310 and S<=30:
                damage          = nDesign/(10**11)
                damageList      += [damage]
            else :
                print "UTS is out of the norm's applicable bracket"
    elif materialName == '':                            # 3-F.1.2 (d) Nickel-Chromium-Molybdenum-Iron, Alloys X, G, C-4 and C-276
        for S in S_element:
            if S>90:
                Y = log10(195.0E3*(S/Et*Cusm))
                damage          = nDesign/(10**intPointFLife_d(Y))
                damageList      += [damage]             # 3-F.1.2 (e) is ignored since the bolts are not considered for the fatigue analysis
            elif S<=90:
                damage          = nDesign/(10**11)
                damageList      += [damage]
    #print damageList
    return damageList


# 5.    von Mises Stress Calculations
def misesCalc(S):
    if len(S) == 4:                                     # Shell Elements
        mises = (((S[0]-S[1])**2 + 
                (S[1]-S[2])**2 +
                (S[2]-S[0])**2 +
                6*(S[3]**2+ 0 + 0))/2.)**0.5
    elif len(S)==6:                                     # Solid Elements
        mises = (((S[0]-S[1])**2 + 
                (S[1]-S[2])**2 +
                (S[2]-S[0])**2 +
                6*(S[3]**2+S[4]**2 + S[5]**2))/2.)**0.5
    else:                                               # Non structural Elements
        mises = 0
    return mises

    
# 6.    Fatigue penalty factor, Kek
def calcKek(Snk, Sps, m, n):
    """
    Calculating K_e,k from ASME VIII, 5.5.3.2, Step 4 b
    
    m = 2
    n = 0.2 from section V.2. of this script
    """
    
    if Snk <= Sps:
        Kek = 1
    elif Snk < m*Sps:
        Kek = (1+(1-n)/(n*(m-1)))*(Snk/Sps-1)
    else:
        Kek = 1/n
    return Kek  

    
#7.     Allowable limit on the primary plus secondary stress range, Sps
def calcSps(Smax, SY, UTS):
    """
    ASME VIII allowable limit on 
     Explained in paragraph 5.5.6.1.d) 
     Sps: allowable limit on the primary plus secondary stress range.
    """
    
    v1 = Smax*3.
    v2 = 2*SY
    if SY/UTS > 0.7:
        Sps = v2
    else:
        Sps = max([v1,v2])
    return Sps

#################################################################################
# V. Initialization of Parameters                                               #
#################################################################################
#   1. Mechanical Properties
# Values found in ASME Section II Part D

    # SA 240 316
SA_240_316_T_SY         = [40.,     65. ]               # Temperature
SA_240_316_V_SY         = [207E6,   189E6]              # Yield Stess at given temperature
SA_240_316_T_UTS        = [40.,     100.]
SA_240_316_V_UTS        = [517E6,   516E6]              # Ultimate tensile stress at given temperature
SA_240_316_T_E          = [-75,     25,     100]
SA_240_316_V_E          = [201E9,   195E9,  189E9]      # Young Modulus at given temperature
SA_240_316_T_Smax       = [-30.,    65.]
SA_240_316_V_Smax       = [138E6,   138E6]              # Allowable Design Stress in Tension

    # SA 182 S32205
SA_182_S32205_T_SY      = [40.,     65.]
SA_182_S32205_V_SY      = [483.0E6, 449.0E6]
SA_182_S32205_T_UTS     = [40.,     100.]
SA_182_S32205_V_UTS     = [655E6,   655E6]
SA_182_S32205_T_E       = [-75.,    25,     100]
SA_182_S32205_V_E       = [209E9,   200E9,  194E9]
SA_182_S32205_T_Smax    = [40.,     65.]
SA_182_S32205_V_Smax    = [273E6,   273E6]

    # SA 240 S32205
SA_240_S32205_T_SY      = [40.,     65.]
SA_240_S32205_V_SY      = [448.2E6, 417.3E6]
SA_240_S32205_T_UTS     = [40.,     100.]
SA_240_S32205_V_UTS     = [655E6,   655E6]
SA_240_S32205_T_E       = [-75.,    25,     100]
SA_240_S32205_V_E       = [209E9,   200E9,  194E9]
SA_240_S32205_T_Smax    = [40,      65.]
SA_240_S32205_V_Smax    = [273E6,   273E6]

    # S355
S355_T_SY               = [40.,     65.]
S355_V_SY               = [448.2E6, 417.3E6]
S355_T_UTS              = [40.,     100.]
S355_V_UTS              = [655E6,   655E6]
S355_T_E                = [-75.,    25,     100]
S355_V_E                = [209E9,   200E9,  194E9]
S355_T_Smax             = [40,      65.]
S355_V_Smax             = [273E6,   273E6]

    # SA 240 Grade 304
SA_240_G304_T_SY        = [40.,     100.,       150.,       200.,       250.,       300.,       325.,       350.,       375.,       400.,       425.,       450.,       475.,       500.,       525.]
SA_240_G304_V_SY        = [207.4E6, 170.3E6,    154.3E6,    144.3E6,    135.3E6,    129.3E6,    126.3E6,    123.2E6,    121.2E6,    118.2E6,    117.2E6,    114.2E6,    112.2E6,    110.2E6,    108.2E6]
SA_240_G304_T_UTS       = [40.,     100.,       150.,       200.,       250.,       300.,       325.,       350.,       375.,       400.,       425.,       450.,       475.,       500.,       525.]
SA_240_G304_V_UTS       = [750.3E6, 727.5E6,    686.8E6,    674.0E6,    673.9E6,    680.2E6,    683.3E6,    686.5E6,    688.6E6,    689.9E6,    685.4E6,    681.1E6,    670.1E6,    655.4E6,    637.0E6]
SA_240_G304_T_E         = [-200.,   -125.,      -75.,       25.,        100.,       150.,       200.,       250.,       300.,       350.,       400.,       450.,       500.,       550.,       600.,   650.,   700.]
SA_240_G304_V_E         = [209E9,   204E9,      201E9,      195E9,      189E9,      186E9,      183E9,      179E9,      176E9,      172E9,      169E9,      165E9,      160E9,      156E9,      151E9,  146E9,  140E9]
SA_240_G304_T_Smax      = [-30,     65,         100,        125,        150,        175,        200,        225,        250,        275,        300,        325,        350,        375,        400,    425,    450,   475]
SA_240_G304_V_Smax      = [138E6,   138E6,      138E6,      138E6,      138E6,      134E6,      129E6,      125E6,      122E6,      119E6,      116E6,      113E6,      111E6,      109E6,      107E6,  105E6,  103E6, 101E6]

    # SA 240 Grade 304 Pressure Stretched
SA_240_G304PS_T_SY      = [25.,	 	65.]
SA_240_G304PS_V_SY      = [405.8E6, 417.3E6]
SA_240_G304PS_T_UTS     = [25., 	100.]
SA_240_G304PS_V_UTS     = [588E6, 	655E6]
SA_240_G304PS_T_E       = [-200.,   -125.,  -75.,   25.,    100.,   150.,   200.,   250.,   300.,   350.,   400.,   450.,   500.,   550.,   600.,   650.,   700.]
SA_240_G304PS_V_E       = [209E9,   204E9,  201E9,  195E9,  189E9,  186E9,  183E9,  179E9,  176E9,  172E9,  169E9,  165E9,  160E9,  156E9,  151E9,  146E9,  140E9]
SA_240_G304PS_T_Smax    = [-30,     475,]                                         # Code Case 2596-1, Table 1
SA_240_G304PS_V_Smax    = [270E6,   270E6,]


materialProps = {}                              # Dictionary
materialProps['SA-240-316-elast']               = matProps(SA_240_316_T_SY,     SA_240_316_V_SY,    SA_240_316_T_UTS,       SA_240_316_V_UTS,       SA_240_316_T_E,     SA_240_316_V_E,     SA_240_316_T_Smax,      SA_240_316_V_Smax   )
materialProps['SA-182-S32205-elast']            = matProps(SA_182_S32205_T_SY,  SA_182_S32205_V_SY, SA_182_S32205_T_UTS,    SA_182_S32205_V_UTS,    SA_182_S32205_T_E,  SA_182_S32205_V_E,  SA_182_S32205_T_Smax,   SA_182_S32205_V_Smax)
materialProps['SA-240-S32205-elast']            = matProps(SA_240_S32205_T_SY,  SA_240_S32205_V_SY, SA_240_S32205_T_UTS,    SA_240_S32205_V_UTS,    SA_240_S32205_T_E,  SA_240_S32205_V_E,  SA_240_S32205_T_Smax,   SA_240_S32205_V_Smax)
materialProps['SA-240-S32205-DENSITYMOD-elast'] = matProps(SA_240_S32205_T_SY,  SA_240_S32205_V_SY, SA_240_S32205_T_UTS,    SA_240_S32205_V_UTS,    SA_240_S32205_T_E,  SA_240_S32205_V_E,  SA_240_S32205_T_Smax,   SA_240_S32205_V_Smax)
materialProps['S355-ELAST']                     = matProps(S355_T_SY,           S355_V_SY,          S355_T_UTS,             S355_V_UTS,             S355_T_E,           S355_V_E,           S355_T_Smax,            S355_V_Smax         )
materialProps['SA-240 Grade-304-Elast']         = matProps(SA_240_G304_T_SY,    SA_240_G304_V_SY,   SA_240_G304_T_UTS,      SA_240_G304_V_UTS,      SA_240_G304_T_E,    SA_240_G304_V_E,    SA_240_G304_T_Smax,     SA_240_G304_V_Smax  )
materialProps['SA-240 Grade-304-PS-Elast']      = matProps(SA_240_G304PS_T_SY,  SA_240_G304PS_V_SY, SA_240_G304PS_T_UTS,    SA_240_G304PS_V_UTS,    SA_240_G304PS_T_E,  SA_240_G304PS_V_E,  SA_240_G304PS_T_Smax,   SA_240_G304PS_V_Smax)


#   2. Other parameters

m_fatigue = 2.      # Value from ASME VIII, Table 5.13
n_fatigue = 0.2     # Value from ASME VIII, Table 5.13
Kf = 1.7            # Weld fatigue factor, Table 5.11 and Table 5.12

#################################################################################
# VI. ODB files Selection                                                       #
#################################################################################


VP              = session.viewports[session.currentViewportName]
displayedObject = VP.displayedObject

copyTime = time.time()
shutil.copy(currDir+'\\'+odbNameList[0], resultsPath)                   # Copy Acceleration odb to a Result Odb
print 'Copy Time: %s'%round((time.time()-copyTime)/(60),3)

resultsOdb      = openOdb(resultsPath, readOnly=False)                  # Open the Result Odb
resultsOdb.save()


odbList = []
for odbName in odbNameList:
    odbPath = currDir+'\\'+odbName
    try:
        odbOpened = session.odbs[odbPath]
        odbOpened.close()
    except:
        pass
    odbList.append(openOdb(odbPath, readOnly=True))


session.viewports['Viewport: 1'].setValues(displayedObject=odbList[0])
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF, ))


# ra = odbAcc.rootAssembly

scratchOdb 	= session.ScratchOdb(odb=odbList[0])

#################################################################################
# VII. Steps selection                                                          #
#################################################################################

stepDict = {}

for odb in odbList:
    stepDict[odb.name] = [odb.steps[odb.steps.keys()[0]],odb.steps[odb.steps.keys()[1]]]

#################################################################################
# VIII. Frames selection                                                        #
#################################################################################


frameDict = {}

for odb in odbList:
    frameDict[odb.name] = [stepDict[odb.name][0].frames[-1],stepDict[odb.name][1].frames[-1]]


stressFieldDict = {}
for odb in odbList:
    stressFieldDict[odb.name] = [frameDict[odb.name][0].fieldOutputs['S'].getSubset(position=ELEMENT_NODAL),
               frameDict[odb.name][1].fieldOutputs['S'].getSubset(position=ELEMENT_NODAL)]


VP.odbDisplay.basicOptions.setValues(sectionResults=USE_TOP)
VP.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF, ))


#################################################################################
# IX. Creation of the fatigue Step and its Frames                               #
#################################################################################


if 'Fatigue Step' in resultsOdb.steps.keys():
    fatigueStep = resultsOdb.steps['Fatigue Step']
else:
    fatigueStep = resultsOdb.Step(name='Fatigue Step', description='Fatigue step', domain=TIME, timePeriod=1.0)

if len(fatigueStep.frames) < 1:
    fatigueFrame = fatigueStep.Frame(frameId=0, frameValue=0.0, 
        description='Fatigue Frame')
else:
    fatigueFrame = fatigueStep.frames[0]

resultsOdb.save()
resultsOdb.close()
resultsOdb  = openOdb(resultsPath, readOnly=False)

fatigueStep     = resultsOdb.steps['Fatigue Step']
fatigueFrame    = fatigueStep.frames[0]

#################################################################################
# X. Creation of the Stress Differences                                         #
#################################################################################

for odb in odbList:
    fatigueField = fatigueFrame.FieldOutput(name=odb.name.split('/')[-1].split('.odb')[0], 
        description='Stress due to change in load', 
        field=stressFieldDict[odb.name][1]-stressFieldDict[odb.name][0])



#################################################################################
# XI. Loading Definition                                                        #
#################################################################################

SPHL_life   = 20.                               #SPHL Design life, in years

loading     = {}                                # Nb of days of use, Temperature, Stress Field
for odb in odbList:
    loading[odb.name.split('/')[-1].split('.odb')[0]] = Loading(1, 
        25., fatigueFrame.fieldOutputs[odb.name.split('/')[-1].split('.odb')[0]])       # 1 cycle, mises stress difference between the two loading cases

# Interpolation of material properties for the loading temperature
Interpolated_E      = {}
Interpolated_SY     = {}
Interpolated_Smaxt  = {}
Interpolated_UTSt   = {}
for loadCase in loading.keys():
    Interpolated_E[loadCase]        = {}
    Interpolated_SY[loadCase]       = {}
    Interpolated_Smaxt[loadCase]    = {}
    Interpolated_UTSt[loadCase]     = {}
    for materialName in materialProps.keys():
        Interpolated_E[loadCase][materialName]      = np.interp(loading[loadCase].temp, materialProps[materialName].T_E, materialProps[materialName].V_E)
        Interpolated_SY[loadCase][materialName]     = np.interp(loading[loadCase].temp, materialProps[materialName].T_SY, materialProps[materialName].V_SY)
        Interpolated_Smaxt[loadCase][materialName]  = np.interp(loading[loadCase].temp, materialProps[materialName].T_Smax, materialProps[materialName].V_Smax)
        Interpolated_UTSt[loadCase][materialName]   = np.interp(loading[loadCase].temp, materialProps[materialName].T_UTS, materialProps[materialName].V_UTS)


#################################################################################
# XII. List of instances                                                        #
#################################################################################

instanceList = [inst for inst in odbList[0].rootAssembly.instances.keys()]

try:
    instanceList.remove('ASSEMBLY')
except:
    pass

#instanceList = [ 'A-SPHL-COMBINED-1']


ra = odbList[0].rootAssembly

BeforeFirstLoop = time.time() - tic
print 'Before First Loop Duration: %g minutes'%(round((BeforeFirstLoop)/(60),3))

tic = time.time()


#################################################################################
# XIII. Dictionaries                                                           #
#################################################################################

showStopButtonInGui()


#   1. Element dictionary and Material list
elementDict     = {}
materialList    = []

for instanceName in [k for k in instanceList if '' in k]:
    instance = ra.instances[instanceName]
    print instanceName
    if not elementDict.has_key(instanceName):                   # If elemtDict doesnt have the key instanceName
        elementDict[instanceName] = {}
    matAssignments = {}
    for assignment in instance.sectionAssignments:
        setName = assignment.sectionName.split('_')[-1]
        matAssignments[setName] = [e.label for e in instance.elementSets[setName].elements]
    for elm in instance.elements[:]:
        elmLabel = elm.label
        if elmLabel%25000 == 0:
            print elmLabel
        if elm.sectionCategory.name != 'coupling':
            for assignment in instance.sectionAssignments:
                setName = assignment.sectionName.split('_')[-1]
                if elm.label in matAssignments[setName]:
                    materialName = odbList[0].sections[assignment.sectionName].material
                    elementDict[instanceName][elmLabel] = materialName
                    if not materialName in materialList:
                        materialList.append(materialName)
                    break


#    2. Allowable limit on the primary plus secondary stress range
Sps = {}
for materialName in materialList:
    for loadKey in loading.keys():
        Sps[loadKey][materialName] = calcSps(Interpolated_Smaxt[loadKey][materialName], Interpolated_SY[loadKey][materialName], Interpolated_UTSt[loadKey][materialName])


FirstLoopTime = time.time() - tic
print 'First Loop Duration: %g minutes'%(round((FirstLoopTime)/(60),3))

tic = time.time()

KekExceed = []


#################################################################################
# XIV. Sections                                                                 #
#################################################################################

secCatS355              = odbList[0].sectionCategories['shell < S355-ELAST > < 5 section points >']
try:
    secCatSA240304      = odbList[0].sectionCategories['shell < SA-240 Grade-304-Elast > < 5 section points >']
    spBotSA240304       = secCatSA240304.sectionPoints[0]
    spMidSA240304       = secCatSA240304.sectionPoints[2]
    spTopSA240304       = secCatSA240304.sectionPoints[4]
except:
    secCatSA240304PS    = odbList[0].sectionCategories['solid < SA-240 Grade-304-PS-Elast >']

try:
    secCatSA240304PS    = odbList[0].sectionCategories['shell < SA-240 Grade-304-PS-Elast > < 5 section points >']
    spBotSA240304PS     = secCatSA240304PS.sectionPoints[0]
    spMidSA240304PS     = secCatSA240304PS.sectionPoints[2]
    spTopSA240304PS     = secCatSA240304PS.sectionPoints[4]
except:
    secCatSA240304PS    = odbList[0].sectionCategories['solid < SA-240 Grade-304-PS-Elast >']


spBot                   = secCatS355.sectionPoints[0]                   # The only set
spMid                   = secCatS355.sectionPoints[2]                   # Of data that
spTop                   = secCatS355.sectionPoints[4]                   # Is used


#################################################################################
# XV. Main Loop                                                                 #
#                                                                               #
# Instances                                                                     #
#   Load Cases                                                                  #
#       Elements                                                                #
#################################################################################


##### Loadings loop
for loadKey in [k for k in loading.keys() if '' in k]:                  # Only Select certain loads between quotes
    print loadKey
    fatigueKey = 'Damage-%s'%(loadKey)
    if fatigueKey in fatigueFrame.fieldOutputs.keys():
        fatigueField = fatigueFrame.fieldOutputs[fatigueKey]            # Update the field if already exists
    else:
        fatigueField = fatigueFrame.FieldOutput(name=fatigueKey,        # Create it otherwise
            description='damage due to cyclic stress', type=SCALAR )
##### Instances Loop
    for instanceKey in [k for k in instanceList if '' in k]:
        instance        = ra.instances[instanceKey]
        print instanceKey 

        stress          = loading[loadKey].stress
        
        data            = []                                    # Results list for solid elements
        dataShellTop    = []                                    # for shell elements (Top)
        dataShellBottom = []                                    # Bottom
##### Elements Loop
        for element in instance.elements[:]:
            elementLabel = element.label
            if elementLabel%25000 == 0:
                print elementLabel
            if element.sectionCategory.name != 'coupling':
                materialName    = elementDict[instanceKey][elementLabel]
                
                stressValues    = stress.getSubset(region=element).values               # Stress tensor for current element
                if element.type in ['S3', 'S3R', 'S4', 'S4R']:                          #seperate out shell elements
### Note:
### The first 4 values of the stress field are 'SNEG' or point number 1
### The last 4 values of the stress field are 'SPOS' or point number 5
###
                    S_element   = [misesCalc(s.data) for s in stressValues]             # Mises evaluation of the stress difference for the element
                    Spk         = S_element                                             # Eq 5.28 and 5.29
                    
                    Kek         = [calcKek(Spk[n], Sps[loadKey][materialName], m_fatigue, n_fatigue, ) for n in range(len(S_element))]     # Fatigue penalty factor, Eqs (5.31) to (5.33) 
                    if max(Kek) > 1:
                        KekExceed += [[loadKey, instanceKey, elementLabel, max(Kek)]]
                    ### All stresses from here are in MPa as per ASME
                    Sa = [Kf*KekN*s_eN/2E6 for KekN,s_eN in zip(Kek,Spk)]               # Salt,k in 5.5.3.2, Step 4, (d), Eq 5.36 and Sa in 3-F.1.1 
                    intPoints = len(S_element)
                    s1 = Sa[:intPoints/2]                              # SNEG
                    s2 = Sa[intPoints/2:]                              # SPOS
                    damageBottom    = elementDamage2017(s1, Interpolated_E[loadKey][materialName]/1E6, materialName, Interpolated_UTSt[loadKey][materialName]/1E6) 
                    damageTop       = elementDamage2017(s2, Interpolated_E[loadKey][materialName]/1E6, materialName, Interpolated_UTSt[loadKey][materialName]/1E6)
                    dataShellTop    += [[elementLabel, damageTop]]
                    dataShellBottom += [[elementLabel, damageBottom]]
                elif len(stressValues) > 2:                                             #catch all 3D elements
                    S_element = [misesCalc(s.data) for s in stressValues]
                    Spk = S_element
                    Kek = [calcKek(Spk[n], Sps[loadKey][materialName], m_fatigue, n_fatigue, ) for n in range(len(S_element))]
                    if max(Kek) > 1:
                        KekExceed += [[loadKey, instanceKey, elementLabel]]
                    ### All stresses from here are in MPa as per ASME
                    Sa = [Kf*KekN*s_eN/2E6 for KekN,s_eN in zip(Kek,Spk)]
                    damage = elementDamage2017(Sa, Interpolated_E[loadKey][materialName]/1E6, materialName, Interpolated_UTSt[loadKey][materialName]/1E6)
                    data += [[elementLabel, damage]]
                else:                                                                   #internal elements such as couplings
                    damage = [1./1E11]*len(S_element)
                    data += [[elementLabel, damage]]
        
        ## Sort the data in order to add it to the fatigue field
        labels = [d[0] for d in data ]
        values = [d[1] for d in data ]
        values = [[item] for sublist in values for item in sublist]
        data.sort(key=itemgetter(0))
        
        labelsShellTop = [d[0] for d in dataShellTop]
        valuesShellTop = [d[1] for d in dataShellTop]
        valuesShellTop = [[item] for sublist in valuesShellTop for item in sublist]
        dataShellTop.sort(key=itemgetter(0))
        
        labelsShellBottom = [d[0] for d in dataShellBottom]
        valuesShellBottom = [d[1] for d in dataShellBottom]
        valuesShellBottom = [[item] for sublist in valuesShellBottom for item in sublist]
        dataShellBottom.sort(key=itemgetter(0))
        
        
        ## Add the data to the Fatigue field
        try:
            fatigueField.addData(position=ELEMENT_NODAL, instance=instance, labels=labels, data=values)
            print '\n\n%s successfuly added'%fatigueField.name
        except Exception as e:
            print e
            pass
        
        try:
            fatigueField.addData(position=ELEMENT_NODAL, instance=instance,
                labels=labelsShellTop, data=valuesShellTop, sectionPoint=spTop)
        except Exception as e:
            print e
            pass
        
        try:
            fatigueField.addData(position=ELEMENT_NODAL, instance=instance,
                labels=labelsShellBottom, data=valuesShellBottom, sectionPoint=spBot)
        except Exception as e:
            print e
            pass

SecondLoopTime  = time.time() - tic
print 'Second Loop Duration: %g minutes'%(round((SecondLoopTime)/(60),3))

tic             = time.time()


fatigueFrame    = resultsOdb.steps['Fatigue Step'].frames[0]


damageDict      = {}

# for odb in odbList:
   # damageDict[odb.name.split('/')[-1].split('.odb')[0]] = fatigueFrame.fieldOutputs[odb.name.split('/')[-1].split('.odb')[0]]
   # fatigueField           = fatigueFrame.FieldOutput(name='Damage-%s'%odb.name.split('/')[-1].split('.odb')[0], 
       # description='Damage with full pressure cycles', field=damageDict[odb.name.split('/')[-1].split('.odb')[0]])




#################################################################################
# XVI. Save and Finish                                                          #
#################################################################################
# Save and Update the Results Odb
resultsOdb.save()
resultsOdb.close()

resultsOdb      = openOdb(resultsPath, readOnly=True)

t1 = timeit.default_timer()
t = t1-t0
print 'Time to process: %g minutes'%(round((t)/(60),3))


#================================================================================
#================================================================================
#================================================================================
#================================================================================

#################################################################################
# XVII. Notes on this code                                                       #
#################################################################################
""" 

When trying to prove the damage values evaluated via this code, do not forget 
that the stress field values are calculated at Integration Points and then 
interpolated between elements in order to show values at Nodes. 

Thus the stress difference is evaluated at Integration Point by Abaqus and then 
interpolated to the Nodes, explaining the potential discrepancy between handcalcs
and Abaqus. 

"""


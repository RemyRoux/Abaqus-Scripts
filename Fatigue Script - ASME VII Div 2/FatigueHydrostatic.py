# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 09:14:03 2016

@author: feas

ASME VIII Div 2 Fatigue calcs
 
"""


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

#################################################################################
# Odb Files Paths
#################################################################################

currDir = os.getcwd()

odbNameList = [f for f in os.listdir('.') if f.endswith('.odb')]

#odbAccPath 	=     r'H:\Consult\UniqueHydra\2016\SPHL 18\SPHL18-Fatigue-H-Acc-P.odb'
#odbThermPath 	= r'H:\Consult\UniqueHydra\2016\SPHL 18\SPHL18-Fatigue-H-Thermal.odb'
#odbPressPath 	= r'H:\Consult\UniqueHydra\2016\SPHL 18\SPHL18-Fatigue-H-Pressure.odb'
#odbHydroPath 	= r'H:\Consult\UniqueHydra\2016\SPHL 18\SPHL18-Fatigue-A-Hydrostatic.odb'
#resultsPath     = r'H:\Consult\UniqueHydra\2016\SPHL 18\SavedFields\SPHL24-Fatigue-H-Results.odb'
resultsPath     = currDir+'\\SavedFields\\\ResultFields.odb'


#################################################################################
# Suppress previous files
#################################################################################

try:
	odbResults 		= session.odbs[resultsPath]
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

# Suppress Result Directory
try:
	shutil.rmtree('SavedFields')
except:
	pass

os.mkdir('SavedFields')


#################################################################################
# Initialization of classes and functions 
#################################################################################

# Material Properties
class matProps():
	def __init__(self, T_SY, V_SY, T_UTS, V_UTS, T_E, V_E, T_Smax = [0], V_Smax = [0]):
		self.T_SY = T_SY
		self.V_SY = V_SY
		self.T_UTS = T_UTS
		self.V_UTS = V_UTS
		self.T_E = T_E
		self.V_E = V_E
		self.T_Smax = T_Smax
		self.V_Smax = V_Smax

# Loading
class Loading():
	def __init__(self, nDesign, temp, stress, x=1):
		self.nDesign = nDesign
		self.temp = temp
		self.stress = stress
		self.x = x

# N = design number of design cycles
def intPointFLife(Y, C):
    ## 3.F.1.2
	exponent = (C[0] + C[2]*Y + C[4]*Y**2 + C[6]*Y**3 + C[8]*Y**4 + C[10]*Y**5) /  \
				(  1  + C[1]*Y + C[3]*Y**2 + C[5]*Y**3 + C[7]*Y**4 +  C[9]*Y**5)
	return 10**exponent


def elementDamage(S_element, Et, nDesign=1.):
    ## 3.F.1.2
	Cus = 6.894757
	damageList = []
	Efc = 195
	#Y_element = [ for s in S_element]
	for S in S_element:
		Y = S/Cus*Efc/Et
		if Y >= 43.5:
			Cval = CValues['3F3A']
			damage = nDesign/intPointFLife(Y, Cval)
			#print '3F3A',Y, nDesign/damage/1E6, damage
			#print Cval
		elif Y >= 28.4:
			Cval = CValues['3F3B']
			damage = nDesign/intPointFLife(Y, Cval)
			#print '3F3B',Y, nDesign/damage/1E6, damage
			#print Cval
		elif Y >= 13.6:
			Cval = CValues['3F3C']
			damage = nDesign/intPointFLife(Y, Cval)
			#print '3F3C',Y, nDesign/damage/1E6, damage
			#print Cval
		else:
			damage = nDesign/1E11
			#print '1/inf ',Y, nDesign/damage/1E6, damage 
		damageList += [damage]
	return damageList

# von Mises Stress Calculations
def misesCalc(S):
	if len(S) == 4: 									# Shell Elements
		mises = (((S[0]-S[1])**2 + 
				(S[1]-S[2])**2 +
				(S[2]-S[0])**2 +
				6*(S[3]**2+ 0 + 0))/2.)**0.5
	elif len(S)==6: 									# Solid Elements
		mises = (((S[0]-S[1])**2 + 
				(S[1]-S[2])**2 +
				(S[2]-S[0])**2 +
				6*(S[3]**2+S[4]**2 + S[5]**2))/2.)**0.5
	else: 											# Non structural Elements
		mises = 0
	return mises


#################################################################################
# Initialization of Material Properties Parameters
#################################################################################

	# SA 240 316
SA_240_316_T_SY 		= [40., 		65. ] 			# Temperature
SA_240_316_V_SY 		= [207E6, 	189E6] 				# Yield Stess at given temperature
SA_240_316_T_UTS 		= [40., 		100.]
SA_240_316_V_UTS 		= [517E6, 	516E6] 				# Ultimate tensile stress at given temperature
SA_240_316_T_E 		= [-75, 		25, 		100]
SA_240_316_V_E 		= [201E9, 	195E9, 	189E9] 		# Young Modulus at givent temperature
SA_240_316_T_Smax 	= [-30., 	65.]
SA_240_316_V_Smax 	= [138E6, 	138E6]

	# SA 182 S32205
SA_182_S32205_T_SY 	= [40.,	 	65.]
SA_182_S32205_V_SY 	= [483.0E6, 	449.0E6]
SA_182_S32205_T_UTS 	= [40., 		100.]
SA_182_S32205_V_UTS 	= [655E6, 	655E6]
SA_182_S32205_T_E 	= [-75., 	25, 	100]
SA_182_S32205_V_E 	= [209E9, 	200E9, 	194E9]
SA_182_S32205_T_Smax 	= [40.,	 	65.]
SA_182_S32205_V_Smax 	= [273E6, 	273E6]

	# SA 240 S32205
SA_240_S32205_T_SY 	= [40.,	 	65.]
SA_240_S32205_V_SY 	= [448.2E6, 	417.3E6]
SA_240_S32205_T_UTS 	= [40., 		100.]
SA_240_S32205_V_UTS 	= [655E6, 	655E6]
SA_240_S32205_T_E 	= [-75., 	25, 	100]
SA_240_S32205_V_E 	= [209E9, 	200E9, 	194E9]
SA_240_S32205_T_Smax 	= [40, 	65.]
SA_240_S32205_V_Smax 	= [273E6, 	273E6]

	# S355
S355_T_SY 		= [40.,	 	65.]
S355_V_SY 		= [448.2E6, 	417.3E6]
S355_T_UTS 		= [40., 		100.]
S355_V_UTS 		= [655E6, 	655E6]
S355_T_E 		= [-75., 	25, 	100]
S355_V_E 		= [209E9, 	200E9, 	194E9]
S355_T_Smax 	= [40, 	65.]
S355_V_Smax 	= [273E6, 	273E6]

	# SA 240 Grade 304
SA_240_G304_T_SY 		= [40.,     100.,       150.,       200.,       250.,       300.,       325.,       350.,       375.,       400.,       425.,       450.,       475.,       500.,       525.]
SA_240_G304_V_SY 		= [207.4E6, 170.3E6,    154.3E6,    144.3E6,    135.3E6,    129.3E6,    126.3E6,    123.2E6,    121.2E6,    118.2E6,    117.2E6,    114.2E6,    112.2E6,    110.2E6,    108.2E6]
SA_240_G304_T_UTS 	= [40.,     100.,       150.,       200.,       250.,       300.,       325.,       350.,       375.,       400.,       425.,       450.,       475.,       500.,       525.]
SA_240_G304_V_UTS 	= [750.3E6, 727.5E6,    686.8E6,    674.0E6,    673.9E6,    680.2E6,    683.3E6,    686.5E6,    688.6E6,    689.9E6,    685.4E6,    681.1E6,    670.1E6,    655.4E6,    637.0E6]
SA_240_G304_T_E 		= [-200.,   -125.,      -75.,       25.,        100.,       150.,       200.,       250.,       300.,       350.,       400.,       450.,       500.,       550.,       600.,   650.,   700.]
SA_240_G304_V_E 		= [209E9,   204E9,      201E9,      195E9,      189E9,      186E9,      183E9,      179E9,      176E9,      172E9,      169E9,      165E9,      160E9,      156E9,      151E9,  146E9,  140E9]
SA_240_G304_T_Smax 	= [-30,     65,         100,        125,        150,        175,        200,        225,        250,        275,        300,        325,        350,        375,        400,    425,    450,    475]
SA_240_G304_V_Smax 	= [138E6,   138E6,      138E6,      138E6,      138E6,      134E6,      129E6,      125E6,      122E6,      119E6,      116E6,      113E6,      111E6,      109E6,      107E6,  105E6,   103E6, 101E6]

	# SA 240 Grade 304 Pressure Stretched
SA_240_G304PS_T_SY 	= [25.,	 	65.]
SA_240_G304PS_V_SY 	= [405.8E6, 	417.3E6]
SA_240_G304PS_T_UTS 	= [25., 		100.]
SA_240_G304PS_V_UTS 	= [588E6, 	655E6]
SA_240_G304PS_T_E 	= [-200.,    -125.,  -75.,   25.,    100.,   150.,   200.,   250.,   300.,   350.,   400.,   450.,   500.,   550.,   600.,   650.,   700.]
SA_240_G304PS_V_E 	= [209E9,    204E9,  201E9,  195E9,  189E9,  186E9,  183E9,  179E9,  176E9,  172E9,  169E9,  165E9,  160E9,  156E9,  151E9,  146E9,  140E9]
SA_240_G304PS_T_Smax 	= [-30,     475,]                                         # Code Case 2596-1
SA_240_G304PS_V_Smax 	= [270E6,   270E6,]


materialProps = {} 							# Dictionary
materialProps['SA-240-316-elast'] 		= matProps(SA_240_316_T_SY,     SA_240_316_V_SY,     SA_240_316_T_UTS,     SA_240_316_V_UTS,     SA_240_316_T_E,     SA_240_316_V_E, SA_240_316_T_Smax,     SA_240_316_V_Smax)
materialProps['SA-182-S32205-elast'] 		= matProps(SA_182_S32205_T_SY,  SA_182_S32205_V_SY,  SA_182_S32205_T_UTS,  SA_182_S32205_V_UTS,  SA_182_S32205_T_E,  SA_182_S32205_V_E,SA_182_S32205_T_Smax, SA_182_S32205_V_Smax)
materialProps['SA-240-S32205-elast'] 		= matProps(SA_240_S32205_T_SY,  SA_240_S32205_V_SY,  SA_240_S32205_T_UTS,  SA_240_S32205_V_UTS,  SA_240_S32205_T_E,  SA_240_S32205_V_E,SA_240_S32205_T_Smax, SA_240_S32205_V_Smax)
materialProps['SA-240-S32205-DENSITYMOD-elast'] = matProps(SA_240_S32205_T_SY, SA_240_S32205_V_SY, SA_240_S32205_T_UTS,  SA_240_S32205_V_UTS, SA_240_S32205_T_E, SA_240_S32205_V_E,SA_240_S32205_T_Smax, SA_240_S32205_V_Smax)
materialProps['S355-ELAST'] = matProps(S355_T_SY, S355_V_SY, S355_T_UTS,  S355_V_UTS, S355_T_E, S355_V_E,S355_T_Smax, S355_V_Smax)
materialProps['SA-240 Grade-304-Elast'] = matProps(SA_240_G304_T_SY, SA_240_G304_V_SY, SA_240_G304_T_UTS, SA_240_G304_V_UTS, SA_240_G304_T_E, SA_240_G304_V_E, SA_240_G304_T_Smax, SA_240_G304_V_Smax)
materialProps['SA-240 Grade-304-PS-Elast'] = matProps(SA_240_G304PS_T_SY, SA_240_G304PS_V_SY, SA_240_G304PS_T_UTS, SA_240_G304PS_V_UTS, SA_240_G304PS_T_E, SA_240_G304PS_V_E,SA_240_G304PS_T_Smax, SA_240_G304PS_V_Smax)

# ASME VIII Annex 3F Table 3-f.3 
# Coefficients for Fatigue Curve - Lists of 11 coefficients
CValues = {}
CValues['3F3A']=[7.51758875043914E+00,  6.88459945920227E-03, -1.17154779858942E-01, -5.34461114227662E-04, -1.15656913741840E-04, 5.26980606334142E-06, 1.13296399893502E-05, -1.69303414202370E-09, -1.69690667384140E-08, -4.75527285553112E-12, 4.36470451306334E-12]
CValues['3F3B']=[1.24406974820959E+01, -1.17978768653245E-01, -2.42518707189356E+00, -3.66857021254674E-03, 1.56897725492030E-01, 9.88040783949096E-04, -3.17788211261938E-03, -4.33540326039428E-05, -3.28149487646145E-05, 6.04517847666627E-07, 1.37849707570938E-06]
CValues['3F3C']=[6.39204604038968E+00, -2.73851238132920E-01, -1.71472090051975E+00, 3.01145863104466E-02, 1.81163839759392E-01, -1.72385273685904E-03, -9.70025958997666E-03, 5.43729918334179E-05, 2.80448097214502E-04, -7.94122155367560E-07, -3.81236155222453E-06]



#################################################################################
#  ODB files Selection
#################################################################################

VP 				= session.viewports[session.currentViewportName]
displayedObject 	= VP.displayedObject

copyTime = time.time()
shutil.copy(currDir+'\\'+odbNameList[0], resultsPath) 					# Copy Acceleration odb to a Result Odb
print 'Copy Time: %s'%round((time.time()-copyTime)/(60),3)

resultsOdb 		= openOdb(resultsPath, readOnly=False)					# Open the Result Odb
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
# Steps selection
#################################################################################

stepDict = {}

for odb in odbList:
    stepDict[odb.name] = [odb.steps[odb.steps.keys()[0]],odb.steps[odb.steps.keys()[1]]]

#################################################################################
# Frames selection
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
# Creation of the fatigue Step and its Frames
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
resultsOdb	= openOdb(resultsPath, readOnly=False)

fatigueStep 	= resultsOdb.steps['Fatigue Step']
fatigueFrame 	= fatigueStep.frames[0]

#################################################################################
# Creation of the Stress Differences 
#################################################################################

for odb in odbList:
    fatigueField = fatigueFrame.FieldOutput(name=odb.name.split('/')[-1].split('.odb')[0], 
        description='Stress due to change in load', 
        field=stressFieldDict[odb.name][1]-stressFieldDict[odb.name][0])



#################################################################################
# Loading Definition 
#################################################################################

SPHL_life 	= 20.   #SPHL Design life, in years

loading 		= {} 											# Nb of days of use, Temperature, Stress Field
for odb in odbList:
    loading[odb.name.split('/')[-1].split('.odb')[0]] = Loading(1, 
        25., fatigueFrame.fieldOutputs[odb.name.split('/')[-1].split('.odb')[0]]) 				# 1 cycle

# Interpolation of material properties for the loading temperature
Interpolated_E 		= {}
Interpolated_SY 		= {}
Interpolated_Smaxt 	= {}
Interpolated_UTSt 	= {}
for loadCase in loading.keys():
	Interpolated_E[loadCase] 		= {}
	Interpolated_SY[loadCase] 		= {}
	Interpolated_Smaxt[loadCase] 	= {}
	Interpolated_UTSt[loadCase] 	= {}
	for materialName in materialProps.keys():
		Interpolated_E[loadCase][materialName] 		= np.interp(loading[loadCase].temp, materialProps[materialName].T_E, materialProps[materialName].V_E)
		Interpolated_SY[loadCase][materialName] 	= np.interp(loading[loadCase].temp, materialProps[materialName].T_SY, materialProps[materialName].V_SY)
		Interpolated_Smaxt[loadCase][materialName] 	= np.interp(loading[loadCase].temp, materialProps[materialName].T_Smax, materialProps[materialName].V_Smax)
		Interpolated_UTSt[loadCase][materialName] 	= np.interp(loading[loadCase].temp, materialProps[materialName].T_UTS, materialProps[materialName].V_UTS)


#################################################################################
# List of instances
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
# Creation of a dictionary of elements containing the material names
#################################################################################

elementDict = {}

for instanceName in [k for k in instanceList if '' in k]:
	instance = ra.instances[instanceName]
	print instanceName
	if not elementDict.has_key(instanceName): 					# If elemtDict doesnt have the key instanceName
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
					break
				materialName = odbList[0].sections[assignment.sectionName].material
			elementDict[instanceName][elmLabel] = materialName

FirstLoopTime = time.time() - tic
print 'First Loop Duration: %g minutes'%(round((FirstLoopTime)/(60),3))

tic = time.time()

def calcKek(Snk, Sps, m, n):
	"""
	Calculating K_e,k from ASME VIII, 5.5.3.2
	"""
	if Snk <= Sps:
		Kek = 1
	elif Snk < m*Sps:
		Kek = 1+(1-n)/(n*(m-1))*(Snk/Sps-1)
	else:
		Kek = 1/n
	return Kek  

def calcSps(Smax, SY, UTS):
	"""
	ASME VIII allowable limit on 
     Explained in paragraph 5.5.6.1.d) 
     Sps: allowable limit on the primary plus secondary stress range, it is the max between:
     - 
     
	"""
	v1 = Smax*3.
	v2 = 2*SY
	if SY/UTS > 0.7:
		Sps = v2
	else:
		Sps = max([v1,v2])
	return Sps

m_fatigue = 2. 		# Value from ASME VIII
n_fatigue = 0.2 		# Value from ASME VIII
Kf = 1.7 			# Weld fatigue factor

KekExceed = []


#################################################################################
# Sections
#################################################################################

secCatS355          = odbList[0].sectionCategories['shell < S355-ELAST > < 5 section points >']
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



spBot               = secCatS355.sectionPoints[0]						# The only set
spMid               = secCatS355.sectionPoints[2]						# Of data that
spTop               = secCatS355.sectionPoints[4]						# Is used



#################################################################################
# Main Loop
# 
# Instances
# 	Load Cases
# 		Elements
#################################################################################

##### Loadings loop
for loadKey in [k for k in loading.keys() if '' in k]: 					# Only Select certain loads between quotes
	print loadKey
	fatigueKey = 'Damage-%s'%(loadKey)
	if fatigueKey in fatigueFrame.fieldOutputs.keys():
		fatigueField=fatigueFrame.fieldOutputs[fatigueKey]
	else:
		fatigueField = fatigueFrame.FieldOutput(name=fatigueKey,
			description='damage due to cyclic stress', type=SCALAR )
##### Instances Loop
	for instanceKey in [k for k in instanceList if '' in k]:
		instance = ra.instances[instanceKey]
		print instanceKey
#		if 'Hydro' in loadKey:
#			stress = S_H
#		else:
		stress = loading[loadKey].stress
		
		data 			= []									# Results list for solid elements
		dataShellTop 	= []									# for shell elements (Top)
		dataShellBottom 	= []									# Bottom
##### Elements Loop
		for element in instance.elements[:]:
			elementLabel = element.label
#			if elementLabel < 1000:
			if elementLabel%25000 == 0:
				print elementLabel
			if element.sectionCategory.name != 'coupling':
				materialName 	= elementDict[instanceKey][elementLabel]
				Et 			= Interpolated_E[loadKey][materialName]
				SYt 			= Interpolated_SY[loadKey][materialName]
				Smaxt 		= Interpolated_Smaxt[loadKey][materialName]
				UTSt 		= Interpolated_UTSt[loadKey][materialName]
				
				stressValues 	= stress.getSubset(region=element).values
#				stressFieldTest 	= stress.getSubset(region=element)
				if element.type in ['S3', 'S3R', 'S4', 'S4R']: 		#seperate out shell elements
### Note:
### The first 4 values of the stress field are 'SNEG' or point number 1
### The last 4 values of the stress field are 'SPOS' or point number 5
###
					S_element 	= [misesCalc(s.data) for s in stressValues]
					Spk 		= S_element
					Sps 		= calcSps(Smaxt, SYt, UTSt)
					Kek 		= [calcKek(Spk[n], Sps, m_fatigue, n_fatigue, ) for n in range(len(S_element))]
					if max(Kek) > 1:
						KekExceed += [[loadKey, instanceKey, elementLabel]]
					Sa = [Kf*KekN*s_eN/2E6 for KekN,s_eN in zip(Kek,Spk)]
					intPoints = len(S_element)
					s1 = Sa[:intPoints/2]                              # SNEG
					s2 = Sa[intPoints/2:]                              # SPOS
					damageBottom 	= elementDamage(s1, Et/1E9) 
					damageTop 		= elementDamage(s2, Et/1E9)
					dataShellTop 	+= [[elementLabel, damageTop]]
					dataShellBottom 	+= [[elementLabel, damageBottom]]
				elif len(stressValues) > 2: 						#catch all 3D elements
					S_element = [misesCalc(s.data) for s in stressValues]
					Spk = S_element
					Sps = calcSps(Smaxt, SYt, UTSt)
					Kek = [calcKek(Spk[n], Sps, m_fatigue, n_fatigue, ) for n in range(len(S_element))]
					if max(Kek) > 1:
						KekExceed += [[loadKey, instanceKey, elementLabel]]
					Sa = [Kf*KekN*s_eN/2E6 for KekN,s_eN in zip(Kek,Spk)]
					damage = elementDamage(Sa, Et/1E9)
					data += [[elementLabel, damage]]
				else: 									#internal elements such as couplings
					damage = [1./1E11]*len(S_element)
					test=damage
					data += [[elementLabel, damage]]
		
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

SecondLoopTime = time.time() - tic
print 'Second Loop Duration: %g minutes'%(round((SecondLoopTime)/(60),3))

tic = time.time()


fatigueFrame 			= resultsOdb.steps['Fatigue Step'].frames[0]


damageDict = {}

#for odb in odbList:
#    damageDict[odb.name.split('/')[-1].split('.odb')[0]] = fatigueFrame.fieldOutputs[odb.name.split('/')[-1].split('.odb')[0]]
#    fatigueField 			= fatigueFrame.FieldOutput(name='Damage-%s'%odb.name.split('/')[-1].split('.odb')[0], 
#        description='Damage with full pressure cycles', field=damageDict[odb.name.split('/')[-1].split('.odb')[0]])





# Save and Update the Results Odb
resultsOdb.save()
resultsOdb.close()

resultsOdb 		= openOdb(resultsPath, readOnly=True)

t1 = timeit.default_timer()
t = t1-t0
print 'Time to process: %g minutes'%(round((t)/(60),3))


#==========================================================================================
#==========================================================================================
#==========================================================================================
#==========================================================================================



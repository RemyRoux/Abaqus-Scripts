# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 09:55:03 2016

@author: feas

Specifications: 
- Identify the odbs to be upgraded in a directory
- Upgrade these odbs
- Report the elapsed time and the name of the upgraded odb
"""

import os 
import sys
import timeit
import time
import datetime

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



tic = time.time()
eta = False

###############################################################################
## Go through the Directory and look for old versions
###############################################################################

print '\n\n\n\nStart\n\n'

odbToUp = []

### Collect the choice of the user
userChoice = getInputs(fields 	= ('Choose your directory','Current Directory'), 
				dialogTitle 	= 'CHOOSE YOUR DIRECTORY', 
				label 		='Paste the path of the directory to be checked\nOr choose the current directory\n\nFolders in ETA are accepted')

#### Current Directory
if userChoice[0]	=='Current Directory':
	folder 		= os.getcwd()
	odbList 		= [each for each in os.listdir(folder) if each.endswith('.odb')]
	odbList 		= [a.split('.')[0] for a in odbList]
	print 'The selected directory contains the following Odb(s): \n%s'%odbList

	#### Open each odb and check its version
	for odbName in odbList:
		inval 		= False
		corrupt 		= False

		# remove the lock file if it exists
		try:
			os.remove(odbName+'.lck')
		except:
			pass

		# Open the odb
		try:
			currOdb 	= openOdb(odbName+'.odb', readOnly=True)
		except OdbError: 													# Odb can be either corrupted or to be upgraded
			inval 	= True

		if inval 	== True:
			# Upgrade the odb
			try:
				print '\nUpgrading: %s'%(odbName)
				upgradeOdb(odbName+'.odb',odbName+'-Up.odb')
				odbToUp.append(odbName)

			except:														# Odb corrupted
				print '\n\n'+'='*70+'\nThe odb: %s is probably corrupted. \nPlease open it manually and confirm\n'%(odbName)+'='*70
				corrupt = True
				pass

			# Rename the odb if the upgrade is successful
			if corrupt == False:
				os.rename(odbName+'.odb', odbName+'-old.odb')
				os.rename(odbName+'-Up.odb',odbName+'.odb')


#### Custom Path to the odb
else:
	folder = userChoice[0]


	#### If folder in ETA:
# Copies the odb in the folder in the Current Directory
# Upgrades odb in the Current Directory
	if folder.split('\\')[2] 	=='ETA':
		eta 					= True
		odbList 				= [each for each in os.listdir(folder) if each.endswith('.odb')]
		odbList 				= [a.split('.')[0] for a in odbList]
		print 'The selected directory contains: \n%s'%odbList
		currDir 				= os.getcwd()

		# Create the results directory in the current directory
		try:
			os.mkdir('Imported-Upgraded from ETA')
		except WindowsError:
			pass
		
		#### Open each odb and check its version
		for odbName in odbList:
			inval 	= False
			corrupt 	= False

			# remove the lock file
			try:
				os.remove(odbName+'.lck')
			except:
				pass

			# Open the odb and copy it to current directory
			try:
				currOdb 	= openOdb(odbName+'.odb', readOnly = True)
			except OdbError:
				inval 	= True

				print '\nCopying: %s \nfrom: \n%s \nto: \n%s'%(odbName,
					folder, currDir+'\\'+'Imported-Upgraded from ETA')

				shutil.copy(folder+'\\'+odbName+'.odb',
					currDir+'\\'+'Imported-Upgraded from ETA'+'\\'+odbName+'.odb')

			if inval == True:
				# Upgrade the odb
				try:
					print '\nUpgrading: %s'%(odbName)
					upgradeOdb(currDir+'\\'+'Imported-Upgraded from ETA'+'\\'+odbName+'.odb',
						currDir+'\\'+'Imported-Upgraded from ETA'+'\\'+odbName+'-Up.odb')
					odbToUp.append(odbName)
				except OdbError:
					corrupt = True
					print '\n\n'+'='*70+'\nThe odb: %s is probably corrupted. \nPlease try to open it manually and confirm\n'%(odbName)+'='*70
					pass
				if corrupt == False :
					os.rename(currDir+'\\'+'Imported-Upgraded from ETA'+'\\'+odbName+'.odb',currDir+'\\'+'Imported-Upgraded from ETA'+'\\'+odbName+'-old.odb')
					os.rename(currDir+'\\'+'Imported-Upgraded from ETA'+'\\'+odbName+'-Up.odb',currDir+'\\'+'Imported-Upgraded from ETA'+'\\'+odbName+'.odb')


	#### If folder on the machine
	else:
		odbList = [each for each in os.listdir(folder) if each.endswith('.odb')]
		odbList = [a.split('.')[0] for a in odbList]
		print 'The selected directory contains: \n%s'%odbList

		#### Open each odb and check its version
		for odbName in odbList:
			inval 	= False
			corrupt 	= False

			try:
				os.remove(odbName+'.lck')
			except:
				pass	

			try:
				currOdb = openOdb(odbName+'.odb', readOnly = True)
			except OdbError:
				inval = True

			if inval == True:
				# Upgrade the odb
				try:
					print '\nUpgrading: %s'%(odbName)
					upradeOdb(folder+'\\'+odbName+'.odb',folder+'\\'+odbName+'-Up.odb')
					odbToUp.append(odbName)
				except OdbError:
					corrupt = True
					print '\n\n'+'='*70+'\nThe odb: %s is probably corrupted. \nPlease try to open it manually and confirm\n'%(odbName)+'='*70
					pass
				if corrupt == False:
					os.rename(folder+'\\'+odbName+'.odb',folder+'\\'+odbName+'-old.odb')
					os.rename(folder+'\\'+odbName+'-Up.odb',folder+'\\'+odbName+'.odb')

#### Report
print '\nUpgraded Odb(s):\n'
for odbName in odbToUp:
	print odbName+'\n'

###############################################################################
## Delete Old Odb Files
###############################################################################

delFiles = getInputs(fields = ('Delete Source files? Y/N','N'), 
		dialogTitle = 'Delete source files?',)

if (delFiles[0] == 'Y' or delFiles[0] == 'y'):
	# Remove old file in the directory
	if eta != True:
		for odbName in odbToUp:
			os.remove(folder+'\\'+odbName+'-old.odb')
			print '\nRemoved File: %s'%(folder+'\\'+odbName+'-old.odb')

	# Remove old files on ETA and in the current directory
	elif eta == True:
		for odbName in odbToUp:
			os.remove(folder+'\\'+odbName+'.odb')
			print '\nRemoved File: %s'%(folder+'\\'+odbName+'.odb')
			os.remove(currDir+'\\'+'Imported-Upgraded from ETA'+'\\'+odbName+'-old.odb')
			print '\nRemoved File: %s'%(currDir+'\\'+'Imported-Upgraded from ETA'+'\\'+odbName+'-old.odb')

	print '\n\nDone'
	t1 = time.time() - tic
	print '\nElapsed Time: %g minutes'%(round(t1/60.,3))
else:
	print 'Done'
	t1 = time.time() - tic
	print '\nElapsed Time: %g minutes'%(round(t1/60.,3))
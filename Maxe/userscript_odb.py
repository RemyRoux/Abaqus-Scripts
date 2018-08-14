#"""
#userscript_odb.py
#
#Script to read the maximum U1 at midpoint in U1 in mm and convert to inches.
#
#Author : Jegan Chinnaraju, DS Simulia 
#Version : 1.0
#Date : 6/1/2013
#
#usage:
#abaqus python userscript_odb.py
#"""
#
#
import odbAccess
from odbAccess import *
import __main__
import operator
from abaqusConstants import *
import numpy
#
def xyDataFFT(xyData):
  """perform fft on xyData and produce frequency spectrum output data """
  signalData = numpy.array([dataPair[1] for dataPair in xyData.data if dataPair[0]>0.1], dtype=float)
  timeData = [dataPair[0] for dataPair in xyData.data if dataPair[0]>0.1]
  timeIncData = []
  for i in range(len(timeData)-1):				
    timeIncData.append(timeData[i+1] - timeData[i])
  fourier = numpy.abs(numpy.fft.fft(signalData))
  n = signalData.size
  timeStep = sum(timeIncData)/len(timeIncData)
  freq = numpy.fft.fftfreq(n, d=timeStep)
  description = 'FourierSpectrum %s'%xyData.positionDescription
  elementLabel = xyData.positionDescription.split(' ')[-1]
  newData = []
  newData.append((freq[0],fourier[0]/n))
  for i in range(1,n/2-1):
    newData.append((freq[i],2*fourier[i]/n))
  newData.append( (freq[n/2-1],fourier[n/2-1]/n)) 
  session.XYData(data=newData, name='Spectrum_%s'%elementLabel)
  maxValue = sorted(newData[1:], key=lambda dat: dat[1])[-1]
  return maxValue
#
#
# S T A R T
# 
############if __name__ == '__main__':
  odbName = 'Round.odb'
  odb = odbAccess.openOdb(path=odbName,readOnly=True)
  instance = odb.rootAssembly.instances['VOLUME-1']
  outputSet = instance.elementSets['HISTORYOUTPUT']
  step = odb.steps['Flow']
  isData = False
  for element in outputSet.elements:
    elementLabel = element.label
    historyPoint = odbAccess.HistoryPoint(element=element)
    if step.getHistoryRegion(point=historyPoint).historyOutputs.has_key('PRESSURE'):
      isData = True
      history = step.getHistoryRegion(point=historyPoint).historyOutputs['PRESSURE']
      historyData = history.data
      historyName = history.name
      historyDescription = history.description
      session.XYData(data=historyData, name='%s-%s'%(historyName, elementLabel),
           positionDescription='%s at element %s'%(historyDescription, elementLabel))
    #
########if isData:
paramsFile=open('user_params.txt','w')
outputList = []
for xyDataName, xyData in session.xyDataObjects.items():
  if 'Spectrum' not in xyDataName:
     outputList.append((xyDataName, xyDataFFT(xyData)))
     maxAmplitude = sorted(outputList, key=lambda dat: dat[1][1])[-1]
     minFrequency = outputList[1][0]
      #
  paramsFile.write("Maximum_Amplitude"+"\t"+ str(maxAmplitude)+"\n")
#
#paramsFile.write("Minimum_frequency\t%s\n"%minFrequency)
#paramsFile.write("Maximum_amplitude"+"\t%s\n"%maxAmplitude)
      #
  paramsFile.close()
  #
  odb.close()



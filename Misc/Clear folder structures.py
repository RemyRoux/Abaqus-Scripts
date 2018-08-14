# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 11:00:37 2015

@author: feas
"""
import numpy as np
import os
from os.path import join, getsize
from distutils.util import strtobool


from time import time as _time
AgeLimitDays = 90
AgeLimit = AgeLimitDays*60*60*24   #90 day age limit for ODB files

topFolder = 'E:\Consult'
#topFolder = 'W:\Consult\GRW'
#topFolder = 'D:\Consult\UniqueHydra\2016\SPHL 24 man\FEA\Jobs'

extensions = ['.023', '.abq', '.cid', '.com', '.dat', '.ipm', '.lck', '.log',
              '.mdl', '.msg', '.pac', '.prt', '.res', '.sel', '.sim', '.stt']
              
extensions += ['.odb']              
extensions += ['.sta']              

## add something to handel upgraded odbs with "old.odb"
## add RESTART.zip
excludePhrase = 'Ratchet'
flist = os.walk(topFolder, topdown = False)
delList = []
time_now = _time()
count = 0
size = 0.
skippedSize = 0.
print '\n','-'*40,'\n'
print 'Files with the following extensions will be deleted:'
print ('{:}, '*(len(extensions)-1) + '{:}').format(*extensions)
print '\nOnly files where the base file name (name without extension)\
\nis repeated will be deleted this is to minimise the risk of deleting\
\nnon-Abaqus files with any of these extensions'
print '\n','-'*40,'\n'
print 'ODB Output files to be deleted:'
#allnames = []
for root, dirs, files in os.walk(topFolder):
  
  for name in files:
    fname = join(root, name)
#    allnames += [fname]
    if fname[-4:] in extensions and excludePhrase not in fname:
      if '.odb' in extensions:
        if fname[-4:] == '.odb': 
          if (time_now-os.path.getmtime(fname)) > AgeLimit:
            if '.inp' in [each[-4:] for each in os.listdir(root) if each.startswith(name[:-4])]:
              fsize = getsize(fname)
              size += fsize
              print '{:>5.1f}GB  {}'.format(fsize/1024/1024/1024,fname)
              
              delList += [fname]
              count += 1
            else:
              fsize = getsize(fname)
              skippedSize += fsize
              print '{:>5.1f}GB  -SKIP-  {}'.format(fsize/1024/1024/1024,fname)
      elif len([each for each in os.listdir(root) if each.startswith(name[:-4])]) > 2:
        delList += [fname]
        count += 1
        size += getsize(fname)


print '\n', '-'*40
print 'Number of files to delete: {}'.format(count)
print 'Total disk space to be freed: {:.1f}GB'.format(size/1024/1024/1024)
print 'Total size of skipped files as no inp for odb: {:.1f}GB'.format(skippedSize/1024/1024/1024)
print '-'*40

if len(delList)>0:
##  print 'Continue with delete? Files will be PERMANENTLY deleted.'
##  confirm = raw_input()
##  try:
##    confirm = strtobool(confirm)
##  except:
##      confirm = False
##  
##  if confirm:
##    print 1
    for fname in delList:
      print fname
      try:
        os.remove(fname)
      except:
        print fname
        pass
    



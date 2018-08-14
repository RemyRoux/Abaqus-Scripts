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
AgeLimitDays = 30
AgeLimit = AgeLimitDays*60*60*24   #90 day age limit for ODB files

#topFolder = r'H:\Consult'
#topFolder = 'O:'
#topFolder = r'Q:\UniqueHydra\2016\SPHL 12 Man\FEA\Jobs'
topFolder = r'E:\Consult'

extensions = ['.023', '.cid', '.com', '.ipm', '.lck', '.log',
              '.msg', '.pac',  '.sel',  '.sta']

timed_ext = [ '.abq', '.dat', '.res','_RESTART.zip','.mdl','.sim','old.odb', '.stt', '.prt', '.odb']              

## add something to handel upgraded odbs with "old.odb"
## add RESTART.zip
excludePhrase = 0
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
allnames = []
for root, dirs, files in os.walk(topFolder):
  for name in files:
    fname = join(root, name)
    if excludePhrase == 0 or excludePhrase not in fname:
      allnames += [fname]
      if fname[-4:] in extensions:
        if len([each for each in os.listdir(root) if each.startswith(name[:-4])]) > 3:
          delList += [fname]
          count += 1
          size += getsize(fname)
      elif fname[-4:] in timed_ext or '_RESTART' in fname:
        
        if (time_now-os.path.getmtime(fname)) > AgeLimit:
#          if '.inp' in [each[-4:] for each in os.listdir(root) if each.startswith(name[:-4])]:
#          keepme = [each[-4:] for each in os.listdir(root) if each.startswith(name[:-4]) or each.startswith(name[:-12])]
          if '.inp' in [each[-4:] for each in os.listdir(root) if each.startswith(name[:-4]) or each.startswith(name[:-12])]:
            fsize = getsize(fname)
            size += fsize
            if '.odb' in fname:
              print '{:>5.1f}GB  {}'.format(fsize/1024/1024/1024,fname)
            delList += [fname]
            count += 1
          else:
            fsize = getsize(fname)
            skippedSize += fsize
            print '{:>5.1f}GB  -SKIP-  {}'.format(fsize/1024/1024/1024,fname)
      


print '\n', '-'*40
print 'Number of files to delete: {}'.format(count)
print 'Total disk space to be freed: {:.1f}GB'.format(size/1024/1024/1024)
print 'Total size of skipped files as no inp for odb: {:.1f}GB'.format(skippedSize/1024/1024/1024)
print '-'*40
#
if len(delList)>0:
###  print 'Continue with delete? Files will be PERMANENTLY deleted.'
###  confirm = raw_input()
###  try:
###    confirm = strtobool(confirm)
###  except:
###      confirm = False
###  
###  if confirm:
###    print 1
#    for fname in delList:
#      print fname
       try:
         os.remove(fname)
       except:
         print fname
         pass
##    
#


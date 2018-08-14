# Script to run sequence of jobs sequentially on either Windows or Linux
# Use:  abaqus Python Runall.py <enter>

import os 
import time 
import glob

t0 = time.clock()

abqCmd = 'abq2016'

folder = os.getcwd()
joblist = [each for each in os.listdir(folder) if each.endswith('.inp')]

joblist = [a.split('.')[0] for a in joblist]

with open(folder+'\JobExecution.txt',"w") as fInp:
  for j in joblist:
    fInp.write(j+'\n')

print 'Jobs in queue:%i'%len(joblist)
k=0

line1 = []
Bool=True
while Bool:
  with open(folder+'\JobExecution.txt',"r+") as fInp:
    line1 = fInp.readlines()
  #line1[k].rstrip('\n')  
  time.sleep(.1)
  print(line1,line1[k],k,len(line1))  
  if line1[k][0] != '#':
    cmd = '%s j=%s cpus=4 DOUBLE interactive ask_delete=OFF > %s.log'%(abqCmd, line1[k], line1[k]) # after CPU write double to get a double precision
# cpus = x because the parallelization is not specified in the inp file
# interactive means that the jobs will run one after the other
    print cmd
    time.sleep(1.)
    os.system(cmd)
    with open(folder+'\JobExecution.txt',"r+") as fInp:
      line1[k] = '#'+line1[k]
      fInp.writelines(line1)
  if line1[k] == '#END':
    Bool = False
  time.sleep(1.)  
  if k<len(line1)-1:  
    k+=1
    
t1 = time.clock()
total = round((t1-t0)/(60*60),2)

print 'All jobs have been run' 
print 'Time to completeion: %g hours'%total

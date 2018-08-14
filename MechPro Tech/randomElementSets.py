# Script to create element sets based on % distribution
from textRepr import prettyPrint as pp
import random

N_150mm = 3591
N_100mm = 7271
N_50mm  = 38778
n_200mm = 2020
n_150mm = 3591
n_100mm = 8079
n_50mm  = 32315

N_total = float(N_150mm + N_100mm + N_50mm + n_200mm + n_150mm + n_100mm + n_50mm)

elset = {}
elset['N_150mm'] = []
elset['N_100mm'] = []
elset['N_50mm'] = []
elset['n_200mm'] = []
elset['n_150mm'] = []
elset['n_100mm'] = []
elset['n_50mm'] = []

for i in range(1,95645):
  rnd = random.random()
  if rnd <= N_150mm/N_total:
    elset['N_150mm'].append(i)
  elif rnd > N_150mm/N_total and rnd <= (N_150mm+N_100mm)/N_total:
    elset['N_100mm'].append(i)
  elif rnd > (N_150mm+N_100mm)/N_total and rnd <= (N_150mm+N_100mm+N_50mm)/N_total:
    elset['N_50mm'].append(i)
  elif rnd > (N_150mm+N_100mm+N_50mm)/N_total and rnd <= (N_150mm+N_100mm+N_50mm+n_200mm)/N_total:
    elset['n_200mm'].append(i)
  elif rnd > (N_150mm+N_100mm+N_50mm+n_200mm)/N_total and rnd <= (N_150mm+N_100mm+N_50mm+n_200mm+n_150mm)/N_total:
    elset['n_150mm'].append(i)
  elif rnd > (N_150mm+N_100mm+N_50mm+n_200mm+n_150mm)/N_total and rnd <= (N_150mm+N_100mm+N_50mm+n_200mm+n_150mm+n_100mm)/N_total:
    elset['n_100mm'].append(i)
  elif rnd > (N_150mm+N_100mm+N_50mm+n_200mm+n_150mm+n_100mm)/N_total and rnd <= (N_150mm+N_100mm+N_50mm+n_200mm+n_150mm+n_100mm+n_50mm)/N_total:
    elset['n_50mm'].append(i)
  else:
    print 'Number %i not assigned into an element set'%i

print 'N150mm %s, %s'%(len(elset['N_150mm'])/N_total, N_150mm/N_total)
print 'N100mm %s, %s'%(len(elset['N_100mm'])/N_total, N_100mm/N_total)
print 'N50mm %s, %s'%(  len(elset['N_50mm'])/N_total,   N_50mm/N_total)
print 'n200mm %s, %s'%(len(elset['n_200mm'])/N_total, n_200mm/N_total)
print 'n150mm %s, %s'%(len(elset['n_150mm'])/N_total, n_150mm/N_total)
print 'n100mm %s, %s'%(len(elset['n_100mm'])/N_total, n_100mm/N_total)
print 'n50mm %s, %s'%(  len(elset['n_50mm'])/N_total,   n_50mm/N_total)

file = open('elementSets.txt', 'w')
for key, elementList in elset.items():
  if len(elementList) > 0:
    file.write('*Elset, elset=%s \n'%key)
    myList = [elementList[i:i+10] for i in range(0,len(elementList), 10)]
    for subList in myList:
    	if len(subList) == 10:
    		file.write('%s, \n'%str(subList).strip('[]'))
    	else:
    		file.write('%s\n'%str(subList).strip('[]'))

file.close()


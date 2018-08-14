from textRepr import prettyPrint as pp


file = open('elementSets.txt', 'w')
for key, set in part.sets.items():
  if '0MM' in key:
     elementList = [val.label for val in set.elements]
     if len(elementList) > 0:
       file.write('*Elset, elset=%s \n'%key)
       myList = [elementList[i:i+10] for i in range(0,len(elementList), 10)]
       for subList in myList:
    	if len(subList) == 10:
    		file.write('%s, \n'%str(subList).strip('[]'))
    	else:
    		file.write('%s\n'%str(subList).strip('[]'))

file.close()


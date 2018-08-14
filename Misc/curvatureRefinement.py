# Script to redefine curvature refinement for all parts in the active model
#
# Developed for GRW by FEAS in November 2010

# set up Abaqus defaults
from abaqus import *
from abaqusConstants import *
from caeModules import *

# define model name based on what is currently in the active viewport
VP = session.viewports[session.currentViewportName]
modelName = VP.displayedObject.modelName

# Loop through all parts in the model and change from default
for partName, part in mdb.models[modelName].parts.items():
  try:
    part.setValues(geometryRefinement=FINE)
  except:
    print 'The geometry cannot be refined for part %s'%partName

# update the assembly to reflect the new part settings 
mdb.models[modelName].rootAssembly.regenerate()

# print output to alert user that all parts have been updated.
print 'Curvature refinement reset to FINE for all parts in ', modelName
 

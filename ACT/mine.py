from abaqus import *
from abaqusConstants import *
from textRepr import prettyPrint as pp


# define model name based on what is currently in the active viewport
VP = session.viewports[session.currentViewportName]
modelName = VP.displayedObject.modelName
model = mdb.models[modelName]
ra = model.rootAssembly

for i in range(78,120):
  print i
  region1=ra.instances['Spacer-'+str(i)].sets['Refpt']
  region2=ra.instances['Spacer-'+str(i)].surfaces['CoupledSurface']
  model.Coupling(name='SpacerCoupling-'+str(i), controlPoint=region1, surface=region2, 
      influenceRadius=WHOLE_SURFACE, couplingType=DISTRIBUTING, 
      weightingMethod=UNIFORM, localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, 
      ur2=ON, ur3=ON)


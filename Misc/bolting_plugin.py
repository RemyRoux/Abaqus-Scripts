from abaqusGui import *
from abaqusConstants import ALL
import osutils, os
from kernelAccess import mdb, session
boltDiamList =    [4  , 5  , 6  , 8  , 10 , 12 , 14 , 16 , 20 , 24 , 30 , 36 ]   # Modify with GUI
washerThickList = [0.7, 0.9, 1.4, 1.4, 1.8, 2.3, 2.3, 2.7, 2.7, 3.7, 3.7, 4.4] # Modify with GUI
washerODList =    [9,   10 , 12 , 16 , 20 , 24 , 28 , 30 , 37 , 44 , 56 , 66 ] # Modify with GUI    

setBolts = tuple(zip(boltDiamList, washerODList,washerThickList))
rows, cols = len(setBolts), len(setBolts[0])


###########################################################################
# Class definition
###########################################################################

class Bolting_plugin(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='Main',
            objectName='boltingProcedures', registerQuery=False)
        pickedDefault = ''
        
        if not self.radioButtonGroups.has_key('UnitsSel'):
            self.UnitsSelKw1 = AFXIntKeyword(None, 'UnitsSelDummy', True)
            self.UnitsSelKw2 = AFXStringKeyword(self.cmd, 'UnitsSel', True)
            self.radioButtonGroups['UnitsSel'] = (self.UnitsSelKw1, self.UnitsSelKw2, {})
        self.radioButtonGroups['UnitsSel'][2][23] = 'mm'
        if not self.radioButtonGroups.has_key('UnitsSel'):
            self.UnitsSelKw1 = AFXIntKeyword(None, 'UnitsSelDummy', True)
            self.UnitsSelKw2 = AFXStringKeyword(self.cmd, 'UnitsSel', True)
            self.radioButtonGroups['UnitsSel'] = (self.UnitsSelKw1, self.UnitsSelKw2, {})
        self.radioButtonGroups['UnitsSel'][2][24] = 'm'
        self.UnitsSelKw1.setValue(24)
        
        self.modelNameKw = AFXStringKeyword(self.cmd, 'modelName', True, 'Model-1')
        self.washerElsetNameKw = AFXStringKeyword(self.cmd, 'washerElsetName', True, 'All')
        self.pretensionStepNameKw = AFXStringKeyword(self.cmd, 'pretensionStepName', True, 'boltPretension')
        self.boltMaterialNameKw = AFXStringKeyword(self.cmd, 'boltMaterialName', True)
        self.boltMaterialProofKw = AFXFloatKeyword(self.cmd, 'boltMaterialProof', True, 580E6)
        self.boltMaterialPretensionKw = AFXFloatKeyword(self.cmd, 'boltMaterialPretension', True, 0.75)
        self.boltInputKw = AFXTableKeyword(self.cmd, 'boltInput', True)
        self.boltInputKw.setColumnType(-1, AFXTABLE_TYPE_FLOAT)
        self.boltInputKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.boltInputKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.boltInputKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        for row in range(rows):
          for col in range(cols):
             self.boltInputKw.setValue(row,col, str(setBolts[row][col]))
        self.boltLengthIncrementKw = AFXFloatKeyword(self.cmd, 'boltLengthIncrement', True, 1)
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import boltingDB
        return boltingDB.BoltingDB(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def doCustomChecks(self):

        # Try to set the appropriate radio button on. If the user did
        # not specify any buttons to be on, do nothing.
        #
        
        for kw1,kw2,d in self.radioButtonGroups.values():
            try:
                value = d[ kw1.getValue() ]
                kw2.setValue(value)
            except:
                pass
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def okToCancel(self):

        # No need to close the dialog when a file operation (such
        # as New or Open) or model change is executed.
        #
        return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Register the plug-in
#

from kernelAccess import mdb, session

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Bolting Assist', 
    object=Bolting_plugin(toolset),
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    kernelInitString='import boltingProcedures',
    applicableModules=ALL,
    version='1.2',
    author='FEAS (PTY) Ltd',
    description='Plug-in to assist with creating bolted assemblies',
    helpUrl='feas@feas.co.za'
)

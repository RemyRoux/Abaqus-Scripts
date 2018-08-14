from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os



thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

boltDiamList =    [4  , 5  , 6  , 8  , 10 , 12 , 14 , 16 , 20 , 24 , 30 , 36 ] # Modify with GUI
washerThickList = [0.7, 0.9, 1.4, 1.4, 1.8, 2.3, 2.3, 2.7, 2.7, 3.7, 3.7, 4.4] # Modify with GUI
washerODList =    [9,   10 , 12 , 16 , 20 , 24 , 28 , 30 , 37 , 44 , 56 , 66 ] # Modify with GUI    

setBolts = tuple(zip(boltDiamList, washerThickList,washerODList))
rows, cols = len(setBolts), len(setBolts[0])

###########################################################################
# Class definition
###########################################################################

class BoltingDB(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

      # Construct the base class.
      #
      AFXDataDialog.__init__(self, form, 'FEAS Bolting Assist',
          self.OK|self.APPLY|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
      
      okBtn = self.getActionButton(self.ID_CLICKED_OK)
      okBtn.setText('OK')
          
      applyBtn = self.getActionButton(self.ID_CLICKED_APPLY)
      applyBtn.setText('Apply')
      
      ## General   
      GroupBox_1 = FXGroupBox(p=self, text='General Settings', opts=FRAME_GROOVE|LAYOUT_FILL_X)
      VAligner_1 = AFXVerticalAligner(p=GroupBox_1, opts=0, x=0, y=0, w=0, h=0,
          pl=0, pr=0, pt=0, pb=0)
      
      # Model combo box
      self.ComboBox_1 = AFXComboBox(p=VAligner_1, ncols=0, nvis=1,
                                        text='Model:\
                                        \tSelect the model to be used.',
                                        tgt=form.modelNameKw, sel=0)
      self.ComboBox_1.setMaxVisible(10)
      names = mdb.models.keys()
      names.sort()
      for name in names:
          self.ComboBox_1.appendItem(name)
      if not form.modelNameKw.getValue() in names:
          form.modelNameKw.setValue( names[0] )
      msgCount = 13
      form.modelNameKw.setTarget(self)
      form.modelNameKw.setSelector(AFXDataDialog.ID_LAST+msgCount)
      msgHandler = str(self.__class__).split('.')[-1] + '.onComboBox_2MaterialsChanged'
      exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler) )
      
      #Units selection radio buttons
      HFrame_1 = FXHorizontalFrame(p=VAligner_1, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
      l = FXLabel(p=HFrame_1, text='Units used in model: \
                                    \tSelect what units were used in the model', opts=JUSTIFY_LEFT)
      FXRadioButton(p=HFrame_1, text='mm', tgt=form.UnitsSelKw1, sel=23)
      FXRadioButton(p=HFrame_1, text='m', tgt=form.UnitsSelKw1, sel=24)      
      
      # Bolt face set name
      AFXTextField(p=VAligner_1, ncols=20,
                   labelText='Bolting sets name:\
                   \tEnter the part-level set name to be used.\nAll shells in this set are inspected and potential washer fasec identiefied ', tgt=form.washerElsetNameKw, sel=0)
      # Name of pretension analysis step             
      AFXTextField(p=VAligner_1, ncols=20,
                   labelText='Pretension Step Name\
                   \tEnter the analysis step name where pretension is to be applied. \nIf the step is not the first step, it is created.', tgt=form.pretensionStepNameKw, sel=0)
      GroupBox_2 = FXGroupBox(p=self, text='Bolt settings', opts=FRAME_GROOVE)
      VAligner_2 = AFXVerticalAligner(p=GroupBox_2, opts=0, x=0, y=0, w=0, h=0,
          pl=0, pr=0, pt=0, pb=0)
      # Material name slectyor
      self.ComboBox_2 = AFXComboBox(p=VAligner_2, ncols=0, nvis=1,
                                    text='Material:\
                                    \tSelect the material to use for the bolts',
                                    tgt=form.boltMaterialNameKw, sel=0)
      self.ComboBox_2.setMaxVisible(10)
      
      self.form = form
      # Bolt proof stress value    
      AFXTextField(p=VAligner_2, ncols=12,
                    labelText='Bolt proof stress [Pa]\
                    \tEnter the bolt material proof stress',
                    tgt=form.boltMaterialProofKw, sel=0)
      
      # Pretension loading factor    
      AFXTextField(p=VAligner_2, ncols=12,
                   labelText='Pretension Factor\
                   \tEnter the fraction of proof stress to which the bolts must be pretensioned',
                   tgt=form.boltMaterialPretensionKw, sel=0)
      
      ## Bolt details             
      if isinstance(GroupBox_2, FXHorizontalFrame):
          FXVerticalSeparator(p=GroupBox_2, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=2, pb=2)
      else:
          FXHorizontalSeparator(p=GroupBox_2, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=2, pb=2)
      l = FXLabel(p=GroupBox_2, text='Enter bolt parameter for all bolt diameters potentially in the model. ', opts=JUSTIFY_LEFT)
      l = FXLabel(p=GroupBox_2, text='NOTE: Enter values in mm', opts=JUSTIFY_LEFT)
      vf = FXVerticalFrame(GroupBox_2, FRAME_SUNKEN|FRAME_THICK|LAYOUT_FILL_X,
          0,0,0,0, 0,0,0,0)
      # Note: Set the selector to indicate that this widget should not be
      #       colored differently from its parent when the 'Color layout managers'
      #       button is checked in the RSG Dialog Builder dialog.
      
      # Bolt Table
      vf.setSelector(99)
      
      table = AFXTable(vf, rows+1, cols, rows, cols, form.boltInputKw, 0, AFXTABLE_EDITABLE|LAYOUT_FILL_X)
      table.setPopupOptions(AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE|AFXTable.POPUP_INSERT_ROW|AFXTable.POPUP_DELETE_ROW|AFXTable.POPUP_READ_FROM_FILE|AFXTable.POPUP_WRITE_TO_FILE)
      table.setLeadingRows(1)
      table.setColumnWidth(0, 120)
      table.setColumnType(0, AFXTable.FLOAT)
      table.setColumnWidth(1, 120)
      table.setColumnType(1, AFXTable.FLOAT)
      table.setColumnWidth(2, 120)
      table.setColumnType(2, AFXTable.FLOAT)
      table.setLeadingRowLabels('Bolt OD\n[mm]\tWasher OD\n[mm]\tWasher Tickness\n[mm]')
      table.setStretchableColumn( table.getNumColumns()-1 )
      table.showHorizontalGrid(True)
      table.showVerticalGrid(True)
      table.setColumnJustify(-1, AFXTable.CENTER)
      # Bolt increment
#      if isinstance(GroupBox_2, FXHorizontalFrame):
#          FXVerticalSeparator(p=GroupBox_2, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=2, pb=2)
#      else:
      FXHorizontalSeparator(p=GroupBox_2, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=2, pb=2)
      AFXTextField(p=GroupBox_2, ncols=3,
                   labelText='Bolt length increment in mm:\tEnter the minimum length increment when creating bolt parts',
                   tgt=form.boltLengthIncrementKw, sel=0)
      FXHorizontalSeparator(p=GroupBox_2, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=2, pb=2)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):

        AFXDataDialog.show(self)

        # Register a query on materials
        #
        self.currentModelName = getCurrentContext()['modelName']
        self.form.modelNameKw.setValue(self.currentModelName)
        mdb.models[self.currentModelName].materials.registerQuery(self.updateComboBox_2Materials)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def hide(self):

        AFXDataDialog.hide(self)

        mdb.models[self.currentModelName].materials.unregisterQuery(self.updateComboBox_2Materials)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onComboBox_2MaterialsChanged(self, sender, sel, ptr):

        self.updateComboBox_2Materials()
        return 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_2Materials(self):

        modelName = self.form.modelNameKw.getValue()

        # Update the names in the Materials combo
        #
        self.ComboBox_2.clearItems()
        names = mdb.models[modelName].materials.keys()
        names.sort()
        for name in names:
            self.ComboBox_2.appendItem(name)
        if names:
            if not self.form.boltMaterialNameKw.getValue() in names:
                self.form.boltMaterialNameKw.setValue( names[0] )
        else:
            self.form.boltMaterialNameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )


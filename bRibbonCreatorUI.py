from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

from RibbonTool import bRibbonCreator

import maya.cmds as mc
import maya.OpenMayaUI as omui


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class RibbonCreatorController(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(RibbonCreatorController, self).__init__(parent)

        self.setWindowTitle("RibbonCreator")
        self.setMinimumWidth(370)
        self.setMinimumHeight(738)

        self.name = ""
        self.vWidth = 0
        self.uLength = 0
        self.uPatches = 0
        self.surfaceDegree = 1
        self.controlJointsNumber = 0
        self.ribbonType = "Normal"

        self.rootSize = 0
        self.ctrlsSize = 0

        self.init_ui()
        self.create_layout()
        self.create_connections()

        self.nameIsEmpty = True

        self.canCreateRibbon = False

    def init_ui(self):
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load("D:\Animations\Qt\RibbonMaker.ui", parentWidget=None)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui)

    def create_connections(self):

        self.ui.surfaceDegreeCB.currentIndexChanged.connect(self.on_surfaceDegree_select)
        self.ui.createPB.clicked.connect(self.on_create_pressed)
        self.ui.ribbonTypeCB.activated.connect(self.on_ribbonType_select)

        self.ui.lengthS.valueChanged.connect(self.length_slider_correlation)
        self.ui.widthS.valueChanged.connect(self.width_slider_correlation)
        self.ui.upatchesS.valueChanged.connect(self.U_patches_slider_correlation)

        self.ui.ctrlsSizeS.valueChanged.connect(self.Ctrls_Size_correlation)
        self.ui.rootSizeS.valueChanged.connect(self.Root_Size_correlation)

    def create_slider(self, minimum, maximum):
        pass

    def on_create_pressed(self):

        if len(self.ui.nameLE.text()) == 0:
            self.nameIsEmpty = True
            return
        self.name = self.ui.nameLE.text()
        self.nameIsEmpty = False

        self.uLength = float(self.ui.lengthLE.text())
        self.vWidth = float(self.ui.widthLE.text())
        self.uPatches = int(self.ui.upatchesLE.text())
        self.controlJointsNumber = int(self.ui.ctrlJointsLE.text())

        self.ctrlsSize = float(self.ui.ctrlsSizeLE.text())
        self.rootSize = float(self.ui.rootSizeLE.text())

        capturedElement = mc.ls(sl=1)
        print(capturedElement)
        if len(capturedElement) > 1 or len(capturedElement) == 0:

            bRibbonCreator.Ribbon(name=self.name, VWidth=self.vWidth, U_Patches=self.uPatches,
                                  ULength=self.uLength, surfaceDegree=self.surfaceDegree,
                                  ribbonType=self.ribbonType, controlJointsNumber=self.controlJointsNumber, rootSize= self.rootSize
                                  , ctrlsSize= self.ctrlsSize)
        else:
            obj = capturedElement[0]
            print("Testing  translateTo and rotateTo ::" + obj)
            bRibbonCreator.Ribbon(name=self.name, VWidth=self.vWidth, U_Patches=self.uPatches,
                                  ULength=self.uLength, surfaceDegree=self.surfaceDegree,
                                  ribbonType=self.ribbonType, controlJointsNumber=self.controlJointsNumber,
                                  translateTo=obj, rotateTo=obj, rootSize= self.rootSize
                                  , ctrlsSize= self.ctrlsSize)

    def on_surfaceDegree_select(self, index):

        self.surfaceDegree = int(self.ui.surfaceDegreeCB.currentText())

    def on_ribbonType_select(self, index):
        self.ribbonType = self.ui.ribbonTypeCB.currentText()

    def length_slider_correlation(self, value):
        self.ui.lengthLE.setText(str(value))

    def width_slider_correlation(self, value):
        self.ui.widthLE.setText(str(value))

    def U_patches_slider_correlation(self, value):
        self.ui.uPatchesLE.setText(str(value))

    def Ctrls_Size_correlation(self, value):
        self.ui.ctrlsSizeLE.setText(str(value))

    def Root_Size_correlation(self, value):
        self.ui.rootSizeLE.setText(str(value))


if __name__ == "__main__":
    ribbonCreatorUI = RibbonCreatorController()
    ribbonCreatorUI.show()

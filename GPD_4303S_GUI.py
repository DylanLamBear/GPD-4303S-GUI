"""
Name: GPD-4303S-GUI.py
Created: 3/18/2024
Author: Dylan Lambert
Purpose: Create backend code for a GUI the allows for digital interfacing with the GPD-4303S power supplies
"""

"""
Other Python Modules To Install Beyond (PyVISA, PyVISA-py, PyUSB) (Likely will need zeroconf, but try all)
- PySerial (to interface with Serial instruments)
- PyUSB (to interface with USB instruments)
- linux-gpib (to interface with gpib instruments, only on linux)
- gpib-ctypes (to interface with GPIB instruments on Windows and Linux)
- psutil (to discover TCPIP devices across multiple interfaces)
- zeroconf (for HiSLIP and VICP devices discovery)
- pyvicp (to enable the Teledyne LeCroy proprietary VICP protocol)
"""

import sys
import time
import threading
from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QCloseEvent
import pyvisa
import GPD_4303S_GUI_UI


class GPD_4303S(QtWidgets.QMainWindow, GPD_4303S_GUI_UI.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.PSstate = {} # No need to initalize, the power supply will tell us this
        self.ChannelSettings = {} # Necessary to initialize
        self.SavedSettings = [{},{},{},{}] # Create a lit of dictionaries that is the saved memory settings
        self.setupUi(self)
        self.RM = pyvisa.ResourceManager("@py")
        self.GPD_4303S_RM = self.RM.open_resource('ASRL4::INSTR')
        self.GPD_4303S_RM.baud_rate = 115200
        self.ReadState() # Read Out Information About the connected GPD-4303S power supply
        self.IdentifyPS()
        self.PSReset() # Channel Settings Initialized Here
        self.UpdateSettingInterface()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.MeasureOutputs)
        self.actionExit.triggered.connect(self.GUI_Shutdown)
        self.pushButtonOutput.clicked.connect(self.OutputToggle)
        self.actionSave_State_1.triggered.connect(self.SaveState1)
        self.actionSave_State_2.triggered.connect(self.SaveState2)
        self.actionSave_State_3.triggered.connect(self.SaveState3)
        self.actionSave_State_4.triggered.connect(self.SaveState4)
        self.actionLoad_State_1.triggered.connect(self.LoadState1)
        self.actionLoad_State_2.triggered.connect(self.LoadState2)
        self.actionLoad_State_3.triggered.connect(self.LoadState3)
        self.actionLoad_State_4.triggered.connect(self.LoadState4)
        self.actionReset.triggered.connect(self.PSReset)
        self.pushButtonV1Set.clicked.connect(self.V1Set)
        self.pushButtonV2Set.clicked.connect(self.V2Set)
        self.pushButtonV3Set.clicked.connect(self.V3Set)
        self.pushButtonV4Set.clicked.connect(self.V4Set)
        self.pushButtonA1Set.clicked.connect(self.A1Set)
        self.pushButtonA2Set.clicked.connect(self.A2Set)
        self.pushButtonA3Set.clicked.connect(self.A3Set)
        self.pushButtonA4Set.clicked.connect(self.A4Set)

    def LoadState1(self):
        self.GPD_4303S_RM.write("RCL1")
        self.textEditMSG.setText("LOADED STATE1")
        self.ChannelSettings = self.SavedSettings[0].copy()
        self.UpdateSettingInterface()

    def LoadState2(self):
        self.GPD_4303S_RM.write("RCL2")
        self.textEditMSG.setText("LOADED STATE2")
        self.ChannelSettings = self.SavedSettings[1].copy()
        self.UpdateSettingInterface()

    def LoadState3(self):
        self.GPD_4303S_RM.write("RCL3")
        self.textEditMSG.setText("LOADED STATE3")
        self.ChannelSettings = self.SavedSettings[2].copy()
        self.UpdateSettingInterface()

    def LoadState4(self):
        self.GPD_4303S_RM.write("RCL4")
        self.textEditMSG.setText("LOADED STATE4")
        self.ChannelSettings = self.SavedSettings[3].copy()
        self.UpdateSettingInterface()

    def SaveState1(self):
        self.GPD_4303S_RM.write("SAV1")
        self.textEditMSG.setText("SAVED TO STATE1")
        self.SavedSettings[0] = self.ChannelSettings.copy()

    def SaveState2(self):
        self.GPD_4303S_RM.write("SAV2")
        self.textEditMSG.setText("SAVED TO STATE2")
        self.SavedSettings[1] = self.ChannelSettings.copy()
    
    def SaveState3(self):
        self.GPD_4303S_RM.write("SAV3")
        self.textEditMSG.setText("SAVED TO STATE3")
        self.SavedSettings[2] = self.ChannelSettings.copy()

    def SaveState4(self):
        self.GPD_4303S_RM.write("SAV4")
        self.textEditMSG.setText("SAVED TO STATE4")
        self.SavedSettings[3] = self.ChannelSettings.copy()

    def PSReset(self): # set both the amp limit setting and voltage setting for all channels to zero
        if(self.PSstate["Output"] == "ON"): # On exit, if power supply is on, turn off output
            self.OutputToggle()
        self.GPD_4303S_RM.write("ISET1:0") # Set All Current and Voltage Channels to Zero
        self.GPD_4303S_RM.write("ISET2:0")
        self.GPD_4303S_RM.write("ISET3:0")
        self.GPD_4303S_RM.write("ISET4:0")
        self.GPD_4303S_RM.write("VSET1:0")
        self.GPD_4303S_RM.write("VSET2:0")
        self.GPD_4303S_RM.write("VSET3:0")
        self.GPD_4303S_RM.write("VSET4:0")
        self.ChannelSettings["V1"] = 0.0
        self.ChannelSettings["V2"] = 0.0
        self.ChannelSettings["V3"] = 0.0
        self.ChannelSettings["V4"] = 0.0
        self.ChannelSettings["A1"] = 0.0
        self.ChannelSettings["A2"] = 0.0
        self.ChannelSettings["A3"] = 0.0
        self.ChannelSettings["A4"] = 0.0
        self.UpdateSettingInterface()
        self.UpdateState()

    def A1Set(self):
        UserInput = self.lineEditA1IN.text()
        self.lineEditA1IN.clear()
        self.textEditMSG.setText("SET A1")
        try:
            InputFloat = float(UserInput)
            InputFloat = round(InputFloat, 3)
            self.GPD_4303S_RM.write("ISET1:" + str(InputFloat))
            self.ChannelSettings["A1"] = str(InputFloat)
            if(self.PSstate["Output"] == "OFF"):
                self.UpdateSettingInterface()
        except:
            self.textEditMSG.setText("Invalid A1 Input")
    
    def A2Set(self):
        UserInput = self.lineEditA2IN.text()
        self.lineEditA2IN.clear()
        self.textEditMSG.setText("SET A3")
        try:
            InputFloat = float(UserInput)
            InputFloat = round(InputFloat, 3)
            self.GPD_4303S_RM.write("ISET2:" + str(InputFloat))
            self.ChannelSettings["A2"] = str(InputFloat)
            if(self.PSstate["Output"] == "OFF"):
                self.UpdateSettingInterface()
        except:
            self.textEditMSG.setText("Invalid A2 Input")

    def A3Set(self):
        UserInput = self.lineEditA3IN.text()
        self.lineEditA3IN.clear()
        self.textEditMSG.setText("SET A3")
        try:
            InputFloat = float(UserInput)
            InputFloat = round(InputFloat, 3)
            self.GPD_4303S_RM.write("ISET3:" + str(InputFloat))
            self.ChannelSettings["A3"] = str(InputFloat)
            if(self.PSstate["Output"] == "OFF"):
                self.UpdateSettingInterface()
        except:
            self.textEditMSG.setText("Invalid A3 Input")

    def A4Set(self):
        UserInput = self.lineEditA4IN.text()
        self.lineEditA4IN.clear()
        self.textEditMSG.setText("SET A4")
        try:
            InputFloat = float(UserInput)
            InputFloat = round(InputFloat, 3)
            self.GPD_4303S_RM.write("ISET4:" + str(InputFloat))
            self.ChannelSettings["A4"] = str(InputFloat)
            if(self.PSstate["Output"] == "OFF"):
                self.UpdateSettingInterface()
        except:
            self.textEditMSG.setText("Invalid A4 Input")

    def V1Set(self):
        UserInput = self.lineEditV1IN.text()
        self.lineEditV1IN.clear()
        self.textEditMSG.setText("SET V1")
        try:
            InputFloat = float(UserInput)
            InputFloat = round(InputFloat, 3)
            self.GPD_4303S_RM.write("VSET1:" + str(InputFloat))
            self.ChannelSettings["V1"] = str(InputFloat)
            if(self.PSstate["Output"] == "OFF"):
                self.UpdateSettingInterface()
        except:
            self.textEditMSG.setText("Invalid V1 Input")

    def V2Set(self):
        UserInput = self.lineEditV2IN.text()
        self.lineEditV2IN.clear()
        self.textEditMSG.setText("SET V2")
        try:
            InputFloat = float(UserInput)
            InputFloat = round(InputFloat, 3)
            self.GPD_4303S_RM.write("VSET2:" + str(InputFloat))
            self.ChannelSettings["V2"] = str(InputFloat)
            if(self.PSstate["Output"] == "OFF"):
                self.UpdateSettingInterface()
        except:
            self.textEditMSG.setText("Invalid V2 Input")

    def V3Set(self):
        UserInput = self.lineEditV3IN.text()
        self.lineEditV3IN.clear()
        self.textEditMSG.setText("SET V3")
        try:
            InputFloat = float(UserInput)
            InputFloat = round(InputFloat, 3)
            self.GPD_4303S_RM.write("VSET3:" + str(InputFloat))
            self.ChannelSettings["V3"] = str(InputFloat)
            if(self.PSstate["Output"] == "OFF"):
                self.UpdateSettingInterface()
        except:
            self.textEditMSG.setText("Invalid V3 Input")

    def V4Set(self):
        UserInput = self.lineEditV4IN.text()
        self.lineEditV4IN.clear()
        self.textEditMSG.setText("SET V4")
        try:
            InputFloat = float(UserInput)
            InputFloat = round(InputFloat, 3)
            self.GPD_4303S_RM.write("VSET4:" + str(InputFloat))
            self.ChannelSettings["V4"] = str(InputFloat)
            if(self.PSstate["Output"] == "OFF"):
                self.UpdateSettingInterface()
        except:
            self.textEditMSG.setText("Invalid V4 Input")

    def UpdateSettingInterface(self):
        self.lineEditV1.setText(str(self.ChannelSettings["V1"]))
        self.lineEditV2.setText(str(self.ChannelSettings["V2"]))
        self.lineEditV3.setText(str(self.ChannelSettings["V3"]))
        self.lineEditV4.setText(str(self.ChannelSettings["V4"]))
        self.lineEditA1.setText(str(self.ChannelSettings["A1"]))
        self.lineEditA2.setText(str(self.ChannelSettings["A2"]))
        self.lineEditA3.setText(str(self.ChannelSettings["A3"]))
        self.lineEditA4.setText(str(self.ChannelSettings["A4"]))

    def OutputToggle(self):
        if(self.PSstate["Output"] == "OFF"):
            self.GPD_4303S_RM.write("OUT1")
            self.timer.start(1000)
            self.textEditMSG.setText("Output ON")
        elif(self.PSstate["Output"] == "ON"):
            self.GPD_4303S_RM.write("OUT0")
            self.textEditMSG.setText("Output OFF")
            self.timer.stop()
            self.UpdateSettingInterface()
        self.ReadState()

    def MeasureOutputs(self):
        Voltage1 = self.GPD_4303S_RM.query("VOUT1?")[:5]
        Voltage2 = self.GPD_4303S_RM.query("VOUT2?")[:5]
        Voltage3 = self.GPD_4303S_RM.query("VOUT3?")[:5]
        Voltage4 = self.GPD_4303S_RM.query("VOUT4?")[:5]
        Current1 = self.GPD_4303S_RM.query("IOUT1?")[:5]
        Current2 = self.GPD_4303S_RM.query("IOUT2?")[:5]
        Current3 = self.GPD_4303S_RM.query("IOUT3?")[:5]
        Current4 = self.GPD_4303S_RM.query("IOUT4?")[:5]
        self.lineEditV1.setText(str(Voltage1))
        self.lineEditV2.setText(str(Voltage2))
        self.lineEditV3.setText(str(Voltage3))
        self.lineEditV4.setText(str(Voltage4))
        self.lineEditA1.setText(str(Current1))
        self.lineEditA2.setText(str(Current2))
        self.lineEditA3.setText(str(Current3))
        self.lineEditA4.setText(str(Current4))
    
    def ReadState(self):
        Status = self.GPD_4303S_RM.query('STATUS?')
        # Power Supply Channel Control Mode Status
        if(int(Status[0]) == 1):
            self.PSstate["C1CCCV"] = "CV"
        else:
            self.PSstate["C1CCCV"] = "CC"

        # Power Supply Channel Control Mode Status
        if(int(Status[1]) == 1):
            self.PSstate["C2CCCV"] = "CV"
        else:
            self.PSstate["C2CCCV"] = "CC"

        # Power Supply Tracking Status
        if(int(Status[2]),int(Status[3])) == (0,1):
            self.PSstate["Track"] = "Independent"
        elif(int(Status[2]),int(Status[3])) == (1,1):
            self.PSstate["Track"] = "Series"
        elif(int(Status[2]),int(Status[3]) == (1,0)):
            self.PSstate["Track"] = "Parallel"

        # Power Supply Beep Status
        if(int(Status[4]) == 1):
            self.PSstate["Beep"] = "ON"
        else:
            self.PSstate["Beep"] = "OFF"

        # Power Supply Output Status
        if(int(Status[5]) == 1):
            self.PSstate["Output"] = "ON"
        else:
            self.PSstate["Output"] = "OFF"

        # Baud Rate Status
        if(int(Status[6]),int(Status[7])) == (0,0):
            self.PSstate["BaudRate"] = "115200"
        elif(int(Status[6]),int(Status[7])) == (0,1):
            self.PSstate["BaudRate"] = "57600"
        elif(int(Status[6]),int(Status[7]) == (1,0)):
            self.PSstate["BaudRate"] = "9600"
        self.UpdateState()

    def IdentifyPS(self):
        IDN = self.GPD_4303S_RM.query('*IDN?')
        Split_IDN = str(IDN).split(",")
        Split_IDN[2] = Split_IDN[2][3:] # Remove Extra Characters
        Split_IDN[3] = Split_IDN[3][:5]
        self.PSstate["Mfr."] = Split_IDN[0]
        self.PSstate["Model"] = Split_IDN[1]
        self.PSstate["SN"] = Split_IDN[2]
        self.PSstate["FWVer"] = Split_IDN[3]
        self.UpdateState("IDN")

    def UpdateState(self,Update="State"):
        if(Update == "State"):
            self.tableWidget.setItem(0,1,QtWidgets.QTableWidgetItem(self.PSstate["Output"])) # Output State
            self.tableWidget.setItem(1,1,QtWidgets.QTableWidgetItem(self.PSstate["C1CCCV"])) # C1 CC/CV
            self.tableWidget.setItem(2,1,QtWidgets.QTableWidgetItem(self.PSstate["C2CCCV"])) # C2 CC/CV
            self.tableWidget.setItem(3,1,QtWidgets.QTableWidgetItem(self.PSstate["BaudRate"])) # Baud Rate
            self.tableWidget.setItem(4,1,QtWidgets.QTableWidgetItem(self.PSstate["Track"])) # Track
            self.tableWidget.setItem(5,1,QtWidgets.QTableWidgetItem(self.PSstate["Beep"])) # Beep
        elif(Update == "IDN"):
            self.tableWidget.setItem(6,1,QtWidgets.QTableWidgetItem(self.PSstate["Mfr."])) # Mfr.
            self.tableWidget.setItem(7,1,QtWidgets.QTableWidgetItem(self.PSstate["Model"])) # Model
            self.tableWidget.setItem(8,1,QtWidgets.QTableWidgetItem(self.PSstate["SN"])) # SN
            self.tableWidget.setItem(9,1,QtWidgets.QTableWidgetItem(self.PSstate["FWVer"])) # FWVer

    def GUI_Shutdown(self): # Close the UI after stopping PyVISA services
        if(self.PSstate["Output"] == "ON"): # On exit, if power supply is on, turn off output
            self.OutputToggle()
        self.timer.stop()
        self.GPD_4303S_RM.close()
        self.RM.close()
        self.close()

    def closeEvent(self, event): # Direct an X button close to the actionExit close
        self.GUI_Shutdown()


if __name__=="__main__": # Send application to computer, wait for user exit
    app = QtWidgets.QApplication(sys.argv) 
    GPD_4303S_INST = GPD_4303S()
    GPD_4303S_INST.show()
    sys.exit(app.exec())
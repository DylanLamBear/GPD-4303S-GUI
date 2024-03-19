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
from PyQt6 import QtWidgets
from PyQt6.QtGui import QCloseEvent
import pyvisa
import GPD_4303S_GUI_UI

class GPD_4303S(QtWidgets.QMainWindow, GPD_4303S_GUI_UI.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.PSstate = {}# No need to initalize, the power supply will tell us this
        self.setupUi(self)
        self.RM = pyvisa.ResourceManager("@py")
        self.GPD_4303S_RM = self.RM.open_resource('ASRL4::INSTR')
        self.GPD_4303S_RM.baud_rate = 115200
        self.ReadState()
        self.IdentifyPS()
        self.actionExit.triggered.connect(self.GUI_Shutdown)

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
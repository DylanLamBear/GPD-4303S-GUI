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
        self.setupUi(self)
        #self.RM = pyvisa.ResourceManager("@py")
        #self.GPD_4303S_RM = self.RM.open_resource('ASRL4::INSTR')
        self.actionExit.triggered.connect(self.GUI_Shutdown)

    def GUI_Shutdown(self): # Close the UI after stopping PyVISA services
        #self.GPD_4303S_RM.close()
        #self.RM.close()
        self.close()

    def closeEvent(self, event): # Direct an X button close to the actionExit close
        self.GUI_Shutdown()


if __name__=="__main__": # Send application to computer, wait for user exit
    app = QtWidgets.QApplication(sys.argv) 
    GPD_4303S_INST = GPD_4303S()
    GPD_4303S_INST.show()
    sys.exit(app.exec())
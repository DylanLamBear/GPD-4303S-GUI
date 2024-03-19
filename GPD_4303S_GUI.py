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
import pyvisa
import GPD_4303S_GUI_UI



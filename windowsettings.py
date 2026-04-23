import ctypes
import platform
import ctypes
from ctypes import wintypes

def get_win_scale():
    if platform.system().lower()=="windows":
        shcore = ctypes.windll.shcore

        monitor_handle = ctypes.windll.user32.MonitorFromWindow(0, 1) 

        scale_factor = wintypes.UINT()
        shcore.GetScaleFactorForMonitor(monitor_handle, ctypes.byref(scale_factor))

        return float(scale_factor.value)/100
    else:
        return 1

def darkmode(window, darkmode=False):
    if darkmode:
        if platform.system().lower()=="windows" or platform.system().lower()=="linux":
            window.setStyleSheet("""
            QWidget {
                background-color: #282a36;
            }
            QLabel, QPushButton, QComboBox, QLineEdit {
                color: white;
            }
            QComboBox QAbstractItemView { /* Styles for dropdown items */
                color: white;
                background-color: #282a36;
                selection-background-color: #555; /* Highlight color for selected item */
            }
            QPushButton:hover, QComboBox:hover {
                border: 1px solid white; /* Example border style */
            }
            QPushButton, QComboBox,QLineEdit{
                background-color: #44475c;
            }
        """)
        if platform.system().lower()=="windows":
            hwnd = int(window.winId())
            color = ctypes.c_int(0x000001)
            if int(platform.version().split(".")[2])<22000:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(color), ctypes.sizeof(color))
            else:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(color), ctypes.sizeof(color))
def immersivedarkmode(window):
    if platform.system().lower()=="windows":
        hwnd = int(window.winId())
        ctypes.windll.user32.SetWindowLongW(hwnd, -16, ctypes.windll.user32.GetWindowLongW(hwnd, -16) & ~0x00010000)
        ctypes.windll.user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0004 | 0x0020)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(ctypes.c_int(2)), ctypes.sizeof(ctypes.c_int))
def nofullscreen(window):
    if platform.system().lower()=="windows":
        hwnd = int(window.winId())
        GWL_STYLE = -16
        WS_MAXIMIZEBOX = 0x00010000
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        style &= ~WS_MAXIMIZEBOX
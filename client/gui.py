import os
import base64
import threading
import socketio
import sys
import time
import math
import hashlib
from queue import Queue

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from tkinter.ttk import Progressbar
from datetime import datetime
from emoji_dict import EMOJI_DICT

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from logs.db_logger import log_event

FONT = "Georgia"
SERVER_API_URL = "http://localhost:8080"
CHUNK_SIZE = 49152 # 48KB









def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def setup_window(window, title, width, height):
    window.title(title)
    window.configure(width=width, height=height)
    center_window(window, width, height)
    window.resizable(True, True)


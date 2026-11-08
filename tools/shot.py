# -*- coding: utf-8 -*-
"""读 FloatPad 自报的几何信息，截取它所在区域用于外观核对"""
import ctypes
import os

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from PIL import ImageGrab

HERE = os.path.dirname(os.path.abspath(__file__))
GEOM = os.path.join(HERE, "_geom.txt")

with open(GEOM, "r", encoding="utf-8") as f:
    x, y, w, h = [int(v) for v in f.read().split()]

u = ctypes.windll.user32
sw, sh = u.GetSystemMetrics(0), u.GetSystemMetrics(1)
pad = 20

out = os.path.join(HERE, "_shot.png")
img = ImageGrab.grab(bbox=(max(0, x - pad), max(0, y - pad),
                           min(sw, x + w + pad), min(sh, y + h + pad)))
img.save(out)
print("GEOM x=%d y=%d w=%d h=%d | SCREEN=%dx%d | SHOT=%s %s"
      % (x, y, w, h, sw, sh, out, img.size))

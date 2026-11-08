# -*- coding: utf-8 -*-
"""生成无黑框启动的快捷方式 FloatPad.lnk"""
import os
import win32com.client

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = r"D:\ANOCONDA\pythonw.exe"
SCRIPT = os.path.join(HERE, "floatpad.pyw")
LNK = os.path.join(HERE, "FloatPad.lnk")

shell = win32com.client.Dispatch("WScript.Shell")
sc = shell.CreateShortCut(LNK)
sc.TargetPath = TARGET
sc.Arguments = '"%s"' % SCRIPT
sc.WorkingDirectory = HERE
sc.IconLocation = TARGET + ",0"
sc.Description = "FloatPad 桌面置顶速记小窗"
sc.WindowStyle = 1
sc.Save()

print("LNK_OK:", LNK, os.path.exists(LNK), os.path.getsize(LNK), "bytes")

# -*- coding: utf-8 -*-
"""以脱离父进程的方式启动 FloatPad"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PY = r"D:\ANOCONDA\pythonw.exe"
SCRIPT = os.path.join(HERE, "floatpad.pyw")

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NO_WINDOW = 0x08000000

p = subprocess.Popen(
    [PY, SCRIPT],
    cwd=HERE,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW,
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    close_fds=True,
)
print("LAUNCHED_PID=%d" % p.pid)

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 09:04:48 2016

@author: feas

This aims at initializing the variables in Abaqus CAE
"""

import win32api, win32con

A = win32api.MessageBox(0,'Please make sure that is closed', 'Error', win32con.MB_OKCANCEL | win32con.MB_ICONQUESTION | 0x00001000)

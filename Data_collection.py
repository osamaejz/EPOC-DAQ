# BCI Data collection
import os
import ctypes
import sys
from ctypes import *
from numpy import *
import numpy as np
import time
from time import gmtime, strftime
import random
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from ctypes.util import find_library
print (ctypes.util.find_library('edk.dll'))
print (os.path.exists('edk.dll'))
libEDK = ctypes.CDLL("edk.dll",'ascii')
print(libEDK)

#import vlc

class CollectData:
    def __init__(self):  
        
        self.exit = 0
        self.ED_COUNTER = 0
        self.ED_INTERPOLATED=1
        self.ED_RAW_CQ=2
        self.ED_AF3=3
        self.ED_F7=4
        self.ED_F3=5
        self.ED_FC5=6
        self.ED_T7=7
        self.ED_P7=8
        self.ED_O1=9
        self.ED_O2=10
        self.ED_P8=11
        self.ED_T8=12
        self.ED_FC6=13
        self.ED_F4=14
        self.ED_F8=15
        self.ED_AF4=16
        self.ED_GYROX=17
        self.ED_GYROY=18
        self.ED_TIMESTAMP=19
        self.ED_ES_TIMESTAMP=20
        self.ED_FUNC_ID=21
        self.ED_FUNC_VALUE=22
        self.ED_MARKER=23
        self.ED_SYNC_SIGNAL=24

        self.targetChannelList = [self.ED_RAW_CQ,self.ED_AF3, self.ED_F7, self.ED_F3, self.ED_FC5, self.ED_T7,self.ED_P7, self.ED_O1, self.ED_O2, self.ED_P8, self.ED_T8,self.ED_FC6, self.ED_F4, self.ED_F8, self.ED_AF4, self.ED_GYROX, self.ED_GYROY, self.ED_TIMESTAMP, self.ED_FUNC_ID, self.ED_FUNC_VALUE, self.ED_MARKER, self.ED_SYNC_SIGNAL]
        self.eEvent      = libEDK.EE_EmoEngineEventCreate()
        self.eState      = libEDK.EE_EmoStateCreate()
        self.userID            = ctypes.c_uint(0)
        self.nSamples   = ctypes.c_uint(0)
        self.nSam       = ctypes.c_uint(0)
        self.nSamplesTaken  = ctypes.pointer(self.nSamples)
        self.data     = ctypes.pointer(ctypes.c_double(0))
        self.user     = ctypes.pointer(self.userID)
        self.composerPort          = ctypes.c_uint(1726)
        self.secs      = ctypes.c_float(1)
        self.datarate    = ctypes.c_uint(0)
        self.readytocollect    = False
        self.option      = ctypes.c_int(0)
        self.state     = ctypes.c_int(0) 

        print (libEDK.EE_EngineConnect("Emotiv Systems-5"))
        #if libEDK.EE_EngineConnect("Emotiv Systems-5") != 0:
        #print ("Emotiv Engine start up failed.")

        print ("Start receiving EEG Data! Press any key to stop logging...\n")

        self.hData = libEDK.EE_DataCreate()
        libEDK.EE_DataSetBufferSizeInSec(self.secs)

        print ("Buffer size in secs:")
        

   
    def data_acq(self):
        while (1):
            state = libEDK.EE_EngineGetNextEvent(self.eEvent)
            if state == 0:
                eventType = libEDK.EE_EmoEngineEventGetType(self.eEvent)
                libEDK.EE_EmoEngineEventGetUserId(self.eEvent, self.user)
                if eventType == 16:
                    libEDK.EE_DataAcquisitionEnable(self.userID,True)
                    self.readytocollect = True
            
            if self.readytocollect==True:
                libEDK.EE_DataUpdateHandle(0, self.hData)
                libEDK.EE_DataGetNumberOfSample(self.hData,self.nSamplesTaken)
                print(self.nSamplesTaken[0])
                if self.nSamplesTaken[0] == 128:
                    self.nSam=self.nSamplesTaken[0]
                    arr=(ctypes.c_double*self.nSamplesTaken[0])()
                    ctypes.cast(arr, ctypes.POINTER(ctypes.c_double))                        
                    data = array('d')
                    y = np.zeros((128,14))
                    for sampleIdx in range(self.nSamplesTaken[0]):
                        x = np.zeros(14)
                        for i in range(1,15):
                            libEDK.EE_DataGet(self.hData,self.targetChannelList[i],byref(arr), self.nSam)
                            x[i-1] = arr[sampleIdx]
                            
                        y[sampleIdx] = x
                        
                    
                    y = np.transpose(y)

                    fig = plt.plot(y[0])
                    

                    check = 0
                    a, b = [], []
                    a.append(check)
                    b.append(y[0])

                    plt.plot(a, b, color = 'b')
                    plt.show()

                    check += 1
                    

                        


                    
            time.sleep(1.02)

            if self.exit==1:
                self.disconnect_engine()
                print("Engine Disconnected")
                break

    def disconnect_engine(self):
        libEDK.EE_DataFree(self.hData)
        libEDK.EE_EngineDisconnect()
        libEDK.EE_EmoStateFree(self.eState)
        libEDK.EE_EmoEngineEventFree(self.eEvent)

    def disconnect(self):
        self.exit=1

cd = CollectData()
cd.data_acq()    

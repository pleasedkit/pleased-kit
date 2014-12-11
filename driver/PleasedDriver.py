#!/usr/bin/env python2
import copy
import sys
import threading
import time
import u6

class PleasedDriver:
    started = False
    elect_num = 0
    data = dict()
    t1 = None
    lock = None
    def __init__(self, elect_num):
        self.elect_num = elect_num
        self.data = self.initData()
        #INSTANTIATE THE U6 OBJECT
        self.lj = u6.U6()
        self.lj.configU6()
        #STOP A PREVIOUS STREAM IF SOMETHING WENT WRONG ON PREVIOUS ACQUISITION
        try: self.lj.streamStop()
        except: pass
        self.lj.streamConfig(
                NumChannels = elect_num,
                ResolutionIndex = 2, #2	4000 15.9 13.7 +-2.5 < 250
                #SamplesPerPacket = 25,
                #SettlingFactor = 0,
                #InternalStreamClockFrequency = 0, #4MHz
                #DivideClockBy256 = False,
                #ScanInterval = 40000,
                ChannelNumbers = range(elect_num), #CHOOSE THE ADC CHANNELS TO USE
                ChannelOptions = [16 for i in range(elect_num) ], #CONFIGURE THE TYPE OF ACQUISITION: single-ended, gain 10 (i.e. +1V,-1V)
                ScanFrequency = 100, #SET THE FREQUENCY OF SAMPLES: 1KHz for each channel
                #SampleFrequency = None
                )

    def initData(self):
        d = {"AIN"+str(n): [] for n in range(self.elect_num) }
        return d

    def acquireData(self):
        if not self.started:
            self.lj.streamStart()
            self.started = True
            try:
                self.t1 = threading.Thread(target=self.do_acquire)
                self.lock = threading.Lock()
                self.t1.start();
            except:
                pass

    def do_acquire(self):
        try:
            for r in self.lj.streamData():
                if not self.started:
                    break
                if r['errors'] or r['numPackets'] != self.lj.packetsPerRequest or r['missed']:
                    print "error: errors = '%s', numpackets = %d, missed = '%s'" % (r['errors'], r['numPackets'], r['missed'])
                else:
                    self.lock.acquire()
                    for n in range(self.elect_num):
                        self.data["AIN"+str(n)].extend(r["AIN"+str(n)])
                    self.lock.release()
        finally:
            pass

    def readData(self):
        self.lock.acquire()
        ret = copy.deepcopy(self.data)
        self.data = self.initData()
        self.lock.release()
        return ret

    def close(self):
        self.started = False
        try:
            self.t1.join()
        finally:
            pass
        self.lj.streamStop()
        self.lj.close()

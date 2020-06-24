import serial
import sys
import os

import binascii
import json

auchCRCHi = [
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81,
0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
0x40]

auchCRCLo = [
0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, 0x07, 0xC7, 0x05, 0xC5, 0xC4,
0x04, 0xCC, 0x0C, 0x0D, 0xCD, 0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A, 0x1E, 0xDE, 0xDF, 0x1F, 0xDD,
0x1D, 0x1C, 0xDC, 0x14, 0xD4, 0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, 0xF2, 0x32, 0x36, 0xF6, 0xF7,
0x37, 0xF5, 0x35, 0x34, 0xF4, 0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29, 0xEB, 0x2B, 0x2A, 0xEA, 0xEE,
0x2E, 0x2F, 0xEF, 0x2D, 0xED, 0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, 0x61, 0xA1, 0x63, 0xA3, 0xA2,
0x62, 0x66, 0xA6, 0xA7, 0x67, 0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68, 0x78, 0xB8, 0xB9, 0x79, 0xBB,
0x7B, 0x7A, 0xBA, 0xBE, 0x7E, 0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71, 0x70, 0xB0, 0x50, 0x90, 0x91,
0x51, 0x93, 0x53, 0x52, 0x92, 0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B, 0x99, 0x59, 0x58, 0x98, 0x88,
0x48, 0x49, 0x89, 0x4B, 0x8B, 0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, 0x43, 0x83, 0x41, 0x81, 0x80,
0x40]

def hexOut(rsp):
    print(''.join(format(x, '02x') for x in rsp))

def crc16Lo(data) :
    uchCRCHi = 0xFF   # high byte of CRC initialized
    uchCRCLo = 0xFF   # low byte of CRC initialized
    uIndex   = 0x0000 # will index into CRC lookup table
    for ch in data :
        uIndex   = uchCRCLo ^ ch
        uchCRCLo = uchCRCHi ^ auchCRCHi[uIndex]
        uchCRCHi = auchCRCLo[uIndex]
    return (uchCRCLo)

def crc16Hi(data) :
    uchCRCHi = 0xFF   # high byte of CRC initialized
    uchCRCLo = 0xFF   # low byte of CRC initialized
    uIndex   = 0x0000 # will index into CRC lookup table

    for ch in data :
        uIndex   = uchCRCLo ^ ch
        uchCRCLo = uchCRCHi ^ auchCRCHi[uIndex]
        uchCRCHi = auchCRCLo[uIndex]
    return (uchCRCHi)

##########################################################################
class M230:

    # Private objects
    def __init__(self, tty = "/dev/ttyUSB0", netaddr = 0, debug = False):
        self._netaddr = netaddr
        self._ser = None
        self._tty = tty
        self._debug = debug
        self.fail = False

        self.data = dict()
        self.data['Energy'] = dict()
        self.data['PhaseA'] = dict()
        self.data['PhaseB'] = dict()
        self.data['PhaseC'] = dict()
 
        self.connect()
        self.getConnect()
        self.openChannel()
        self.getSN()
        self.getFreq()
        self.getEn0()
        self.getEn1()
        self.getEn2()

        self.getU()
        self.getI()
        self.getCosF()
        self.getP()

    def connect(self):
        try:
            self._ser = serial.Serial(self._tty, 9600, timeout=2)
            self._netaddr = 0
            return True
        except Exception as ex:
            print('Failed to open {}'.format(self._tty), ex)
            self.fail = True
            pass
        return False

    #########################################################################   open chanal
    def openChannel(self):
         if self.fail: return False
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn = [ int(self._netaddr),0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01]
             self._ser.write([ int(self._netaddr),0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01 , crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(4)
             if(rsp[0] == int(self._netaddr) ):
                 return True
         except Exception as e:
             print ('openChannel', e)
             self.fail = True
             pass
         return False

    ########################################################################    A+ A- R+ R- Sum
    def getEn0(self):
         if self.fail: return False
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn = [ int(self._netaddr),0x05,0x00,0x00]
             self._ser.write([ int(self._netaddr),0x05,0x00,0x00, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(19)

             self.data['Energy']['Sum'] = dict()
             x = self.data['Energy']['Sum'] 
             x['Active_plus']  = (int(rsp[2]<<24) + int(rsp[1]<<16) + int(rsp[4]<<8) + int(rsp[3])) / 1000.0
             x['Active_minus'] =  ((int(rsp[6]<<24) + int(rsp[5]<<16) + int(rsp[8]<<8) + int(rsp[7]))^0xFFFFFFFF) / 1000.0
             x['Reactive_plus']  = (int(rsp[10]<<24) + int(rsp[9]<<16) + int(rsp[12]<<8) + int(rsp[11])) / 1000.0
             x['Reactive_minus']  = ((int(rsp[14]<<24) + int(rsp[13]<<16) + int(rsp[16]<<8) + int(rsp[15]))^0xFFFFFFFF) / 1000.0
             return True
         except Exception as e:
             print ('getEn0- ', e)
             self.fail = True
             pass
         return False

    ########################################################################    A+ A- R+ R- T1
    def getEn1(self):
         if self.fail: return False
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn = [ int(self._netaddr),0x05,0x00,0x01]
             self._ser.write([ int(self._netaddr),0x05,0x00,0x01, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(19)

             self.data['Energy']['Day'] = dict()
             x = self.data['Energy']['Day'] 
             x['Active_plus']  = (int(rsp[2]<<24) + int(rsp[1]<<16) + int(rsp[4]<<8) + int(rsp[3])) / 1000.0
             x['Active_minus'] =  ((int(rsp[6]<<24) + int(rsp[5]<<16) + int(rsp[8]<<8) + int(rsp[7]))^0xFFFFFFFF) / 1000.0
             x['Reactive_plus']  = (int(rsp[10]<<24) + int(rsp[9]<<16) + int(rsp[12]<<8) + int(rsp[11])) / 1000.0
             x['Reactive_minus']  = ((int(rsp[14]<<24) + int(rsp[13]<<16) + int(rsp[16]<<8) + int(rsp[15]))^0xFFFFFFFF) / 1000.0
             return True
         except Exception as e:
             print ('getEn1- ', e)
             self.fail = True
             pass
         return False

    ########################################################################    A+ A- R+ R- T1
    def getEn2(self):
         if self.fail: return False
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn = [ int(self._netaddr),0x05,0x00,0x02]
             self._ser.write([ int(self._netaddr),0x05,0x00,0x02, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(19)

             self.data['Energy']['Night'] = dict()
             x = self.data['Energy']['Night'] 
             x['Active_plus']  = (int(rsp[2]<<24) + int(rsp[1]<<16) + int(rsp[4]<<8) + int(rsp[3])) / 1000.0
             x['Active_minus'] =  ((int(rsp[6]<<24) + int(rsp[5]<<16) + int(rsp[8]<<8) + int(rsp[7]))^0xFFFFFFFF) / 1000.0
             x['Reactive_plus']  = (int(rsp[10]<<24) + int(rsp[9]<<16) + int(rsp[12]<<8) + int(rsp[11])) / 1000.0
             x['Reactive_minus']  = ((int(rsp[14]<<24) + int(rsp[13]<<16) + int(rsp[16]<<8) + int(rsp[15]))^0xFFFFFFFF) / 1000.0
             return True
         except Exception as e:
             print ('getEn1- ', e)
             self.fail = True
             pass
         return False

    ########################################################################    A+ A- R+ R- T1
    def getEn3(self):
         if self.fail: return False
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn = [ int(self._netaddr),0x05,0x00,0x03]
             self._ser.write([ int(self._netaddr),0x05,0x00,0x03, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(19)
             Aplus  = int(rsp[2]<<24) + int(rsp[1]<<16) + int(rsp[4]<<8) + int(rsp[3])
             Aminus =  int(rsp[6]<<24) + int(rsp[5]<<16) + int(rsp[8]<<8) + int(rsp[7])
             Rplus  =  int(rsp[10]<<24) + int(rsp[9]<<16) + int(rsp[12]<<8) + int(rsp[11])
             Rminus  = int(rsp[14]<<24) + int(rsp[13]<<16) + int(rsp[16]<<8) + int(rsp[15])
         except Exception as e:
             print ('getEn3- ', e)
             self.fail = True
         return Aplus / 1000.0, (Aminus^0xFFFFFFFF) / 1000.0, Rplus / 1000.0, (Rminus^0xFFFFFFFF) / 1000.0

    ########################################################################    A+ A- R+ R- T1
    def getEn4(self):
         if self.fail: return False
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn = [ int(self._netaddr),0x05,0x00,0x04]
             self._ser.write([ int(self._netaddr),0x05,0x00,0x04, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(19)
             Aplus  = int(rsp[2]<<24) + int(rsp[1]<<16) + int(rsp[4]<<8) + int(rsp[3])
             Aminus =  int(rsp[6]<<24) + int(rsp[5]<<16) + int(rsp[8]<<8) + int(rsp[7])
             Rplus  =  int(rsp[10]<<24) + int(rsp[9]<<16) + int(rsp[12]<<8) + int(rsp[11])
             Rminus  = int(rsp[14]<<24) + int(rsp[13]<<16) + int(rsp[16]<<8) + int(rsp[15])
         except Exception as e:
             print ('getEn4- ', e)
             self.fail = True
         return Aplus / 1000.0, (Aminus^0xFFFFFFFF) / 1000.0, Rplus / 1000.0, (Rminus^0xFFFFFFFF) / 1000.0

    #########################################################################     try to find unit
    def getConnect(self):
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn = [ int(self._netaddr), 0x00]
             self._ser.write([ int(self._netaddr), 0x00 , crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp = self._ser.read(4)

             if(rsp[0] == int(self._netaddr) ):
                 return True
         except Exception as e:
             print ('getConnect error', e)
             self.fail = True
             pass
         return False

    ########################################################################    get U
    def getU(self):
         if self.fail: return False
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn = [ int(self._netaddr),0x08,0x16,0x11]
             self._ser.write([ int(self._netaddr),0x08,0x16,0x11, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(12)

             self.data['PhaseA']['U']  = (int(rsp[1]<<16) + int(rsp[3]<<8) + int(rsp[2])) / 100.0
             self.data['PhaseB']['U']  = (int(rsp[4]<<16) + int(rsp[6]<<8) + int(rsp[5])) / 100.0
             self.data['PhaseC']['U']  = (int(rsp[7]<<16) + int(rsp[9]<<8) + int(rsp[8])) / 100.0
             return True
         except Exception as e:
             print ('getU- ', e)
             self.fail = True
             pass
         return False

    ########################################################################    get U
    def getI(self):
         if self.fail: return False
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn = [ int(self._netaddr),0x08,0x16,0x21]
             self._ser.write([ int(self._netaddr),0x08,0x16,0x21, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(12)

             self.data['PhaseA']['I']  = (int(rsp[1]<<16) + int(rsp[3]<<8) + int(rsp[2])) / 1000.0
             self.data['PhaseB']['I']  = (int(rsp[4]<<16) + int(rsp[6]<<8) + int(rsp[5])) / 1000.0
             self.data['PhaseC']['I']  = (int(rsp[7]<<16) + int(rsp[9]<<8) + int(rsp[8])) / 1000.0
             return True
         except Exception as e:
             print ('getI- ', e)
             self.fail = True
             pass
         return False

    ########################################################################    get P
    def getP(self):
        if self.fail: return False
        try:
            self.data['PhaseA']['P'] = round(self.data['PhaseA']['U'] * self.data['PhaseA']['I'], 2)
            self.data['PhaseB']['P'] = round(self.data['PhaseB']['U'] * self.data['PhaseB']['I'], 2)
            self.data['PhaseC']['P'] = round(self.data['PhaseC']['U'] * self.data['PhaseC']['I'], 2)
            self.data['Power_Total'] = round(self.data['PhaseA']['P'] + self.data['PhaseB']['P'] + self.data['PhaseC']['P'], 2)
            return True
        except Exception as e:
            print('getP-', e)
            self.fail = True
            pass
        return False

    def getP_cnt(self):
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn = [ int(self._netaddr),0x08,0x16,0x00]
             self._ser.write([ int(self._netaddr),0x08,0x16,0x00, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(15)

             bt1=str(bin(rsp[1]))[2:].zfill(8)
             bt4=str(bin(rsp[4]))[2:].zfill(8)
             bt7=str(bin(rsp[7]))[2:].zfill(8)
             bt10=str(bin(rsp[10]))[2:].zfill(8)
             P  = int(rsp[3]<<8) + int(rsp[2])
             if( bt1[1] == '1'): P = P        #   0x40
             if( bt1[0] == '1'): P = P * -1   #   0x80
             P1  = int(rsp[6]<<8) + int(rsp[5])
             if( bt4[1] == '1'): P1 = P1        #   0x40
             if( bt4[0] == '1'): P1 = P1 * -1   #   0x80
             P2  = int(rsp[9]<<8) + int(rsp[8])
             if( bt7[1] == '1'): P2 = P2        #   0x40
             if( bt7[0] == '1'): P2 = P2 * -1   #   0x80
             P3  = int(rsp[12]<<8) + int(rsp[11])
             if( bt10[1] == '1'): P3 = P3        #   0x40
             if( bt10[0] == '1'): P3 = P3 * -1   #   0x80
         except Exception as e:
             print ('getP- ', e)
             self.fail = True
         return P / 10000.0, P1 / 10000.0, P2 / 10000.0, P3 / 10000.0

    ########################################################################    get PS
    def getPS(self):
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn =  [ int(self._netaddr),0x08,0x16,0x08]
             self._ser.write([ int(self._netaddr),0x08,0x16,0x08, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(15)

             bt1=str(bin(rsp[1]))[2:].zfill(8)
             bt4=str(bin(rsp[4]))[2:].zfill(8)
             bt7=str(bin(rsp[7]))[2:].zfill(8)
             bt10=str(bin(rsp[10]))[2:].zfill(8)
             P  = int(rsp[3]<<8) + int(rsp[2])
             if( bt1[1] == '1'): P = P        #   0x40
             if( bt1[0] == '1'): P = P * -1   #   0x80
             P1  = int(rsp[6]<<8) + int(rsp[5])
             if( bt4[1] == '1'): P1 = P1        #   0x40
             if( bt4[0] == '1'): P1 = P1 * -1   #   0x80
             P2  = int(rsp[9]<<8) + int(rsp[8])
             if( bt7[1] == '1'): P2 = P2        #   0x40
             if( bt7[0] == '1'): P2 = P2 * -1   #   0x80
             P3  = int(rsp[12]<<8) + int(rsp[11])
             if( bt10[1] == '1'): P3 = P3        #   0x40
             if( bt10[0] == '1'): P3 = P3 * -1   #   0x80
         except Exception as e:
             print ('getPS- ', e)
             self.fail = True
         return P / 10000.0, P1 / 10000.0, P2 / 10000.0, P3 / 10000.0

    ########################################################################    get PQ
    def getPQ(self):
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn =  [ int(self._netaddr),0x08,0x16,0x04]
             self._ser.write([ int(self._netaddr),0x08,0x16,0x04, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(15)

             bt1=str(bin(rsp[1]))[2:].zfill(8)
             bt4=str(bin(rsp[4]))[2:].zfill(8)
             bt7=str(bin(rsp[7]))[2:].zfill(8)
             bt10=str(bin(rsp[10]))[2:].zfill(8)
             P  = int(rsp[3]<<8) + int(rsp[2])
             if( bt1[1] == '1'): P = P        #   0x40
             if( bt1[0] == '1'): P = P * -1   #   0x80
             P1  = int(rsp[6]<<8) + int(rsp[5])
             if( bt4[1] == '1'): P1 = P1        #   0x40
             if( bt4[0] == '1'): P1 = P1 * -1   #   0x80
             P2  = int(rsp[9]<<8) + int(rsp[8])
             if( bt7[1] == '1'): P2 = P2        #   0x40
             if( bt7[0] == '1'): P2 = P2 * -1   #   0x80
             P3  = int(rsp[12]<<8) + int(rsp[11])
             if( bt10[1] == '1'): P3 = P3        #   0x40
             if( bt10[0] == '1'): P3 = P3 * -1   #   0x80
         except Exception as e:
             print ('getPQ- ', e)
             self.fail = True
         return P / 10000.0, P1 / 10000.0, P2 / 10000.0, P3 / 10000.0

    ########################################################################    get cosF
    def getCosF(self):
         if self.fail: return False
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn =  [ int(self._netaddr),0x08,0x16,0x30]
             self._ser.write([ int(self._netaddr),0x08,0x16,0x30, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(15)

             bt1=str(bin(rsp[1]))[2:].zfill(8)
             bt4=str(bin(rsp[4]))[2:].zfill(8)
             bt7=str(bin(rsp[7]))[2:].zfill(8)
             bt10=str(bin(rsp[10]))[2:].zfill(8)
             P  = int(rsp[3]<<8) + int(rsp[2])
             if( bt1[1] == '1'): P = P        #   0x40
             if( bt1[0] == '1'): P = P * -1   #   0x80
             P1  = int(rsp[6]<<8) + int(rsp[5])
             if( bt4[1] == '1'): P1 = P1        #   0x40
             if( bt4[0] == '1'): P1 = P1 * -1   #   0x80
             P2  = int(rsp[9]<<8) + int(rsp[8])
             if( bt7[1] == '1'): P2 = P2        #   0x40
             if( bt7[0] == '1'): P2 = P2 * -1   #   0x80
             P3  = int(rsp[12]<<8) + int(rsp[11])
             if( bt10[1] == '1'): P3 = P3        #   0x40
             if( bt10[0] == '1'): P3 = P3 * -1   #   0x80

             self.data['PhaseA']['CosPhi'] = P1 / 10.0
             self.data['PhaseB']['CosPhi'] = P2 / 10.0
             self.data['PhaseC']['CosPhi'] = P3 / 10.0
             self.data['CosPhi'] = P / 10.0
             return True

         except Exception as e:
             print ('getCosF- ', e)
             self.fail = True
             pass
         return False

    ########################################################################    get Angle
    def getAngle(self):
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn =  [ int(self._netaddr),0x08,0x16,0x51]
             self._ser.write([ int(self._netaddr),0x08,0x16,0x51, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(12)
             A1  = int(rsp[1]<<16) + int(rsp[3]<<8) + int(rsp[2])
             A2  = int(rsp[4]<<16) + int(rsp[6]<<8) + int(rsp[5])
             A3  = int(rsp[7]<<16) + int(rsp[9]<<8) + int(rsp[8])
             print("Angles", A1, A2, A3)
         except Exception as e:
             print ('getAng- ', e)
         return 0.01 * (A1^0xFFFFFF), 0.01 * (A2^0xFFFFFF), 0.01 * (A3^0xFFFFFF)

    #########################################################################                         freq
    def getFreq(self):
         if self.fail: return False
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn = [ int(self._netaddr),0x08,0x16,0x40]
             self._ser.write([ int(self._netaddr),0x08,0x16,0x40, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp= self._ser.read(6)
             self.data['freq']  = (int(rsp[1]<<16) + int(rsp[3]<<8) + int(rsp[2])) / 100.0
             return True
         except Exception as e:
             print ('getFreq- ', e)
             self.fail = True
             pass
         return False

    ########################################################################                 serial number
    def getSN(self):
        if self.fail: return False
        try:
            self._ser.reset_input_buffer()
            self._ser.flush()
            dataIn = [ int(self._netaddr),0x08,0x00]
            self._ser.write([ int(self._netaddr),0x08,0x00, crc16Lo(dataIn), crc16Hi(dataIn) ])
            rsp= self._ser.read(10)

            self.data['SerialNumber'] = '' + str(rsp[1]).zfill(2)
            self.data['SerialNumber'] += str(rsp[2]).zfill(2)
            self.data['SerialNumber'] += str(rsp[3]).zfill(2)
            self.data['SerialNumber'] += str(rsp[4]).zfill(2)
            return True
        except Exception as e:
            self.fail = True
            print ('getSN', e)
        return False

    ########################################################################                 network address
    def getUnitAddr(self):
         try:
             self._ser.reset_input_buffer()
             self._ser.flush()
             dataIn = [ int(self._netaddr),0x08,0x05]
             self._ser.write([ int(self._netaddr),0x08,0x05, crc16Lo(dataIn), crc16Hi(dataIn) ])
             rsp = self._ser.read(5)
             sn = str(rsp[2])
         except Exception as e:
             print ('getUnitAddr', e)
         return sn

    ########################################################################

if __name__ == '__main__':
    # execute only if run as a script
    m230 = M230('/dev/moxa')
    print(json.dumps(m230.data))

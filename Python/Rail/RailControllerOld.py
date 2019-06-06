################################################################################################
# Copyright@ FARO Technology, Tracker Department
# Author: Patrick Zhou
# Modified: Dan Ferrone on 2/19/18
# Date: 08/28/2017
# License: GPL
# Declaration: You agree to use these codes at your own risk and maintenance efforts
################################################################################################

################################################################################################
#  Exlar Motor
#
#  Contains the interface to the Exlar motor controller
#
################################################################################################

import logging
import time
from Rail.PyTrackerException import PyTrackerException
from Rail.ModbusRTU import ModbusRTU

class RailController (object):

    def __init__(self):
        self.__modbus = ModbusRTU()
        self.moveRegisters = [6100,6118,6136,6154,6172,6190,6208,6226,6244,6262,6280,6298,6316,6334,6352,6370]

    def open (self, port):
        return self.__modbus.connect(port)

    def close (self):
        return self.__modbus.disconnect()

    def check (self):
        self.getBaudRate()

    def getBaudRate (self):
        result = self.parseRawResult(self.__modbus.read_reg(5302));
        if (result[0]=='Succeed'):
            return result[1];
        else:
            raise Exception ("Fail to read Baud rate");

    def getPosition (self):
        response = self.__read2Regs(380)
        return self.__convertResponse(response,16,16,False)

    def moveTo(self, position):
        if position < 0 or position > 15:
            raise Exception ("No position " + str(position) + " is valid")

        logging.debug(self.parseRawResult(self.__modbus.write_reg(4317, 0x00)))
        logging.debug(self.parseRawResult(self.__modbus.write_reg(4316, 0x01)))                 # enable momentary
        # logging.debug(prettyResult(csz.read_reg(4318)))
        logging.debug(self.parseRawResult(self.__modbus.write_reg(4319, 0x00)))
        flag = 0x01 << position
        logging.debug(self.parseRawResult(self.__modbus.write_reg(4319, flag)))

    def waitMove(self):
        # exit if too many exceptions???
        except_timie = 7
        while except_timie:
            try:
                if 0x1000 & self.getStatus() > 0:
                    break
                else:
                    time.sleep(1)
            except Exception:
                except_timie -= 1

    def pause (self):
        logging.debug(self.parseRawResult(self.__modbus.write_reg(4317, 0x08)))

    def stop (self):
        logging.debug(self.parseRawResult(self.__modbus.write_reg(4317, 0x04)))

    #################################################################
    #Reference OEG_MOTION_ENUM for more details of the returned value
    #################################################################
    def getStatus(self):
        result = self.parseRawResult(self.__modbus.read_reg(105));
        if (result[0]=='Succeed'):
            return result[1];
        else:
            raise Exception ("Fail to read current Status");


    # logging.debug(prettyResult(csz.read_reg(6136)))                     #Move option
    # logging.debug(prettyResult(csz.read_reg(6137), 9, 7))                   #AMPS limits
    # logging.debug(prettyDResult(csz.read_two_regs(6138), 12,20))        #Acceleration       RPS
    # logging.debug(prettyResult(csz.read_reg(6140)))                     #Swithch Event. 0 for unassigned
    # logging.debug(prettyResult(csz.read_reg(6141)))                     #Next move to automatically. 0 for unassigned
    # logging.debug(prettyResult(csz.read_reg(6142)))                     #Primary option. 0 for Motion_Absolute
    # logging.debug(prettyDResult(csz.read_two_regs(6144), 16,16))        #Position REVS
    # logging.debug(prettyDResult(csz.read_two_regs(6146), 8,24))         #Velocity  RPS
    # logging.debug(prettyResult(csz.read_reg(6148)))                     #Secondary Move Option

    def __getBinaryString(self,n, nBits=8):
        string = ''
        while n > 0:
            n, rem = divmod(n, 2)
            if rem == 0:
                string = '0' + string
            else:
                string = '1' + string
        for i in range(nBits - len(string)):
            string = '0' + string
        return string

    def __binaryToInt(self,binString):
        number = 0
        for i in range(len(binString)):
            number += int(binString[len(binString) - 1 - i]) * (2 ** i)
        return number

    def binaryToFloat(self,binString, intLength, decLength):
        return self.__binaryToInt(binString[:intLength]) + self.__binaryToInt(binString[-decLength:]) / (2 ** decLength)

    def __convertResponse(self,response, intLength, decLength, U=True):
        string = ''
        if len(response) == 4:
            string += self.__getBinaryString(response[2])
            string += self.__getBinaryString(response[3])
            string += self.__getBinaryString(response[0])
            string += self.__getBinaryString(response[1])
        else:
            string += self.__getBinaryString(response[0])
            string += self.__getBinaryString(response[1])
        if U:
            return self.binaryToFloat(string, intLength, decLength)
        else:
            n = self.binaryToFloat(string, intLength, decLength)
            if n > (2 ** (intLength - 1)):
                return n - (2 ** (intLength))
            else:
                return n

    def __read2Regs(self,register):
        return self.__modbus.read_two_regs(register)[1]

    def __readReg(self,register):
        return self.__modbus.read_regs(register, 1)[1]

    def __convertInput(self,input, intLength, decLength, U=True):
        # binary = self.__getBinaryString(int(input),intLength) + self.__getBinaryString((input-int(input))*(2**decLength),decLength)
        # return int(binary[-16:],2) , int(binary[:16],2)
        if U:
            binary = self.__getBinaryString(int(input), intLength) + self.__getBinaryString(
                (input - int(input)) * (2 ** decLength), decLength)
            return int(binary[-16:], 2), int(binary[:16], 2)
        else:
            if input < 0:
                input += (2 ** (intLength))
                binary = self.__getBinaryString(int(input), intLength) + self.__getBinaryString(
                    (input - int(input)) * (2 ** decLength), decLength)
                return int(binary[-16:], 2), int(binary[:16], 2)
            else:
                binary = self.__getBinaryString(int(input), intLength) + self.__getBinaryString(
                    (input - int(input)) * (2 ** decLength), decLength)
                return int(binary[-16:], 2), int(binary[:16], 2)

    def __writeReg(self,register,value):
        self.__modbus.write_reg(register,value)

    def __write2Regs(self,register,intValue,decValue):
        self.__writeReg(register,decValue)
        self.__writeReg(register+1,intValue)

    def moveToPosition(self,position,moveVelocity = 6 , moveAcceleration = 16.0):
        ## velocity was 2.35
        if position > 45 or position < -450:
            raise PyTrackerException('Position must be between -450 and 0')
        else:
            # self.__writeUACC32(self.moveRegisters[15]+2,moveAcceleration)
            # self.__writeUVEL32(self.moveRegisters[15]+10,moveVelocity)
            self.__writePOS32(self.moveRegisters[15]+8,position)
            self.moveTo(15)
            self.waitMove()

    def __writeUACC32(self,register,value):
        decValue , intValue = self.__convertInput(value,12,20)
        self.__write2Regs(register,intValue,decValue)
        response = self.__read2Regs(register)
        # print('Wrote Acceleration to: ',self.__convertResponse(response,12,20))

    def __writeUVEL32(self,register,value):
        decValue , intValue = self.__convertInput(value,8,24)
        self.__write2Regs(register,intValue,decValue)
        response = self.__read2Regs(register)
        # print('Wrote Velocity to ',self.__convertResponse(response,8,24))

    def __writePOS32(self,register,value):
        decValue , intValue = self.__convertInput(value,16,16,False)
        self.__write2Regs(register,intValue,decValue)
        response = self.__read2Regs(register)
        # print('Wrote Position to ',self.__convertResponse(response,16,16,False))

    @staticmethod
    def codeDWord(value, high, low):
        intvalue = value*pow(2,low)
        bs = intvalue.to_bytes(4, byteorder='big')
        return bs[2]+bs[3]+bs[0]+bs[1]

    @staticmethod
    def decodeAWord(word):
        return int.from_bytes(word, byteorder='big')

    @staticmethod
    def parseRawResult(result):
        return 'Succeed' if (result[0] == 0) else result[0], RailController.decodeAWord(result[-1])

    @staticmethod
    def parseAResult (result, high, low):
        return  'Succeed' if(result[0]==0) else result[0], RailController.decodeAWord(result[1]) / pow(2,low)

    @staticmethod
    def decodeDWord(dword, high, low):
        bigDWord = bytearray()
        bigDWord.append(dword[2])
        bigDWord.append(dword[3])
        bigDWord.append(dword[0])
        bigDWord.append(dword[1])
        # pass
        return int.from_bytes(bigDWord, byteorder='big') / pow(2, low)

    @staticmethod
    def parseDResult(result, high, low):
        return 'Succeed' if (result[0] == 0) else result[0], ExlarMotor.decodeDWord(result[1], high, low)


############################################################################################################
# test code
############################################################################################################
if __name__ == '__main__':
    #logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    #logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    railController = RailController();
    railController.open('COM4');
    try:
        distance = 0
        railController.moveToPosition(distance)
    finally:
        railController.close()





import serial
import Rail.CRC16 as CRC16
import struct
import logging
class ModbusRTU(object):

    def __init__(self):
        self.ser = serial.Serial()
        self.ser.port = None
        self.ser.baudrate = 19200
        self.ser.parity = serial.PARITY_EVEN
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.xonxoff = 0
        self.ser.rtscts = 0
        self.ser.dsrdtr = 0
        self.ser.timeout = 1.0      # experiment with this
        self.crc16 = CRC16.CRC16(True)
        self.appdata = None
        self.reply_type = None
        self.__device_id = 1

    @property
    def device_id(self):
        return self.__device_id

    @device_id.setter
    def device_id(self, value):
        self.__device_id = value


    def connect(self, serial_port):
        ret = 0
        self.ser.port = serial_port
        try:
            self.ser.open()
        except (OSError, serial.SerialException):
            ret = -1
            self.ser.port = None
        return ret

    def disconnect(self):
        self.ser.close()

    def _write_stream(self, stream):
        crc = self.crc16.calculate(bytes(stream))
        self._add_crc(crc)
        self.ser.write(stream)
        response = self._read_reply()
        return response

    def _read_stream(self, stream):
        crc = self.crc16.calculate(bytes(self.appdata))
        self._add_crc(crc)
        self.ser.write(self.appdata)
        # response = self.ser.read(500)
        return self._read_reply()

    def _read_reply(self):
        """ returns list containing two entrys:
        entry 0: return code - 0-OK, -1- crc error, -2- exception
        entry 1: application data when OK return code
                 exception value when -2 error code """
        reply = []
        ret_code = 0
        app_data_start = 2
        exception = False
        response = self.ser.read(100)
        response_byte_count = len(response)
        logging.debug(response_byte_count)
        logging.debug(response)

        if response_byte_count < 5:
            reply.append(-1)
            reply.append(response)
        else:
            read_count = 0
            self.reply_type = response[1]
            if response[1] == 0x03:  # read
                read_count = response[2]
                app_data_start += 1
            elif response[1] == 0x06:  # write reg
                read_count = 4
            elif response[1] == 0x10:  # write regs
                read_count = 4
            elif response[1] >= 0x80:  # exception
                read_count = 3
                exception = True
            if self.verify_crc(response, read_count) is False:
                ret_code = -1
            else:
                if exception is True:
                    ret_code = -2
                    app_data_start = 0

            reply.append(ret_code)
            if response[1] == 0x06 or response[1] == 0x10 :
                reply.append(response[app_data_start:app_data_start + 2])
                reply.append(response[app_data_start+2:app_data_start + read_count])
            else:
                reply.append(response[app_data_start:app_data_start+read_count])

        return reply

    def verify_crc(self, response, read_count):
        crc_length = len(response) - 2
        temp = response[0 : crc_length]
        temp1 = response[crc_length:crc_length+2]
        crc = self.crc16.calculate(bytes(temp))
        embedded_crc = struct.unpack('H', bytes(temp1))
        ret = True
        if embedded_crc[0] != crc:
            ret = False
        return ret


    def _add_word(self, value):
        ## Dan was here
        self.appdata.extend(struct.pack('!H', value))

    def _add_crc(self, value):
        self.appdata.extend(struct.pack('H', value))

    def _add_write_prefix(self):
        self.appdata = bytearray(self.__device_id.to_bytes(1, byteorder='big')+b'\x06')

    def _add_write_regs_prefix(self):
        self.appdata = bytearray(self.__device_id.to_bytes(1, byteorder='big')+b'\x10')

    def _add_read_prefix(self):
        self.appdata = bytearray(self.__device_id.to_bytes(1, byteorder='big')+b'\x03')

    def write_reg(self, register, value):
        self._add_write_prefix()
        self._add_word(register)
        self._add_word(value)
        return self._write_stream(self.appdata)

    def write_two_reg(self, register, value):
        self._add_write_prefix()
        self._add_word(register)
        self._add_word(2)
        self.appdata.append(4)
        self.appdata.append(value)
        return self._write_stream(self.appdata)

    def write_regs(self, start_register, number_registers, value_list):
        self._add_write_regs_prefix()
        self._add_word(start_register)
        self._add_word(number_registers)
        data_bytes = number_registers*2
        self.appdata.append(data_bytes)
        for v in value_list:
            self._add_word(v)
        return self._write_stream(self.appdata)

    def read_reg(self, register):
        return self.read_regs(register, 1)

    def read_two_regs (self, register):
        return self.read_regs(register, 2)

    def read_regs(self, start_register, number_registers):
        self._add_read_prefix()
        self._add_word(start_register)
        self._add_word(number_registers)
        reply = self._read_stream(self.appdata)
        return reply
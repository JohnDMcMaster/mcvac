#!/usr/bin/env python3

import serial
import time


class InficonTimeout(Exception):
    pass


class BCG450:
    def __init__(self,
                 port="/dev/ttyUSB0",
                 ser_timeout=0.5,
                 ser=None,
                 verbose=False):
        self.verbose = verbose
        if not ser:
            ser = serial.Serial(
                port,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                rtscts=False,
                dsrdtr=False,
                xonxoff=False,
                timeout=ser_timeout,
                # Blocking writes
                writeTimeout=None)
        self.ser = ser
        self.ser.flushInput()
        self.ser.flushOutput()
        self.mode = None
        # verify plausible comms
        self.sync()

    def sync(self, timeout=0.2):
        tstart = time.time()
        while True:
            if time.time() - tstart >= timeout:
                raise InficonTimeout()
            if self.ser.read() == b"\x07":
                break

    def get_torr_ex(self, timeout=0.2, flush_input=True):
        tstart = time.time()
        while True:
            if time.time() - tstart >= timeout:
                raise InficonTimeout()
            # can really back up
            # get a recent measurement
            if flush_input:
                self.ser.flushInput()
            # Sync
            while True:
                if time.time() - tstart >= timeout:
                    raise InficonTimeout()
                if self.ser.read() == b"\x07":
                    break
            try:
                buf = self.ser.read(8)
                if len(buf) != 8:
                    continue
                page, status_byte, error_byte, meas_hi, meas_lo, _version, _response, checksum_got = buf
                checksum_calc = sum(buf[0:7]) % 0x100
                if checksum_calc != checksum_got:
                    continue
                assert page == 5, page
                # status 1
                # assert status == 0, status
                #if status != 0:
                #    print('status', status)
                assert error_byte == 0, error_byte
                # From manual
                torr = 10**((meas_hi * 256 + meas_lo) / 4000 - 12.5) * 0.750062
                j = {
                    "torr": torr,
                    "page": page,
                    "error_byte": error_byte,
                    "status_byte": status_byte
                }
                status3 = status_byte & 0x3
                j["degas"] = status3 == 3
                if status3 == 0:
                    j["emission"] = "off"
                    j["status_str"] = "off"
                elif status3 == 1:
                    j["status_str"] = "emission 25 uA"
                    j["emission"] = "25 uA"
                elif status3 == 2:
                    j["status_str"] = "emission 5 mA"
                    j["emission"] = "5 mA"
                elif status3 == 3:
                    j["status_str"] = "degas"
                    j["emission"] = "off"
                else:
                    print("bad status byte 0x3", status3)
                    assert 0
                unit_bits = (status_byte >> 4) & 0x3
                assert unit_bits == 1
                return j
            except Exception as e:
                continue

    def get_torr(self, timeout=0.2, flush_input=True):
        j = self.get_torr_ex(timeout=timeout, flush_input=flush_input)
        return j["torr"]

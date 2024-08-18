#!/usr/bin/env python3

import serial
import numpy as np
import matplotlib.pyplot as plt
import time


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
        self.sync()

    def sync(self):
        while self.ser.read() != b"\x07":
            continue

    def get_torr(self):
        while self.ser.read() != b"\x07":
            continue
        page, status, error, meas_hi, meas_lo, _version, _response, _checksum = self.ser.read(
            8)
        assert page == 5, page
        # status 1
        # assert status == 0, status
        #if status != 0:
        #    print('status', status)
        assert error == 0, error
        torr = 10**((meas_hi * 256 + meas_lo) / 4000 - 12.5) * 0.750062
        return torr

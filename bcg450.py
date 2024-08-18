#!/usr/bin/env python3

import serial
import matplotlib.pyplot as plt
import glob
import time
import json
import datetime

from mcvac.util import default_date_dir
from mcvac.bcg450 import BCG450


def main():
    import argparse

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--verbose', action="store_true")
    parser.add_argument('--graph', action="store_true")
    parser.add_argument('--dir', default=None, help='Output dir')
    parser.add_argument('--postfix', default=None, help='')
    parser.add_argument('fn', nargs='?', help='Log file name')
    args = parser.parse_args()

    def log_next(j):
        open(args.fn, "w+").write(json.dumps(j) + "\n")

    outdir = args.dir
    if outdir is None:
        outdir = default_date_dir("log", "bcg450", args.postfix)

    bcg = BCG450()
    tstart = time.time()
    plt.gca().set_yscale('log')
    measi = 0
    while True:
        val = bcg.get_torr()
        if val < 1e-3:
            s = "%0.3f utorr" % (val * 1e6, )
        elif val < 1:
            s = "%0.3f mtorr" % (val * 1e3, )
        else:
            s = "%g torr" % val
        print(s)
        if args.fn:
            j = {
                "time_utc": datetime.utcnow().isoformat(),
                "tim_local": datetime.now().isoformat(),
                "torr": val,
                "str": s,
            }
            log_next(j)
        # slow...
        if args.graph and measi % 40 == 0:
            tnow = time.time() - tstart
            plt.scatter(tnow, val)
            plt.pause(0.0001)
        measi += 1


if __name__ == "__main__":
    print("test")
    main()

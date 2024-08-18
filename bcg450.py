#!/usr/bin/env python3

import serial
import matplotlib.pyplot as plt
import glob
import time
import json
import os
from datetime import datetime

from mcvac.util import default_date_dir
from mcvac.bcg450 import BCG450


def main():
    import argparse

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--verbose', action="store_true")
    parser.add_argument('--graph', action="store_true")
    # parser.add_argument('--graph-log', action="store_true")
    parser.add_argument('--postfix', default=None, help='')
    parser.add_argument('--out-dir', default="log", help='')
    parser.add_argument('--period', type=float, default=None, help='')
    parser.add_argument('fn', nargs='?', help='Log file name')
    args = parser.parse_args()

    def log_next(j):
        if not os.path.exists(args.out_dir):
            os.mkdir(args.out_dir)
        open(out_fn, "w+").write(json.dumps(j) + "\n")

    out_fn = args.fn
    if out_fn is None:
        out_fn = default_date_dir(args.out_dir, "bcg450", args.postfix) + ".jl"
    print(f"Logging to {out_fn}")

    bcg = BCG450()
    tstart = time.time()
    tlast = None
    if True or args.graph_log:
        plt.gca().set_yscale('log')
    measi = 0
    xs = []
    ys = []
    while True:
        if args.period and tlast is not None:
            while time.time() - tlast < args.period:
                time.sleep(0.001)

        jval = bcg.get_torr_ex()
        val = jval["torr"]
        if val < 1e-3:
            s = "%0.3f utorr" % (val * 1e6, )
        elif val < 1:
            s = "%0.3f mtorr" % (val * 1e3, )
        else:
            s = "%g torr" % val
        print(s, jval["status_str"])
        if out_fn:
            j = {
                "time_utc": datetime.utcnow().isoformat(),
                "tim_local": datetime.now().isoformat(),
                "torr": val,
                "str": s,
                "j": jval,
            }
            log_next(j)
        if args.graph:
            tnow = time.time() - tstart
            xs.append(tnow)
            ys.append(val)
            plt.plot(xs, ys)
            # plt.scatter(tnow, val)
            # plt.scatter(val)
            # plt.gca().autoscale_view(scaley=True, scalex=False)
            # plt.draw()
            # plt.gca().autoscale_view(tight=True, scalex=False)
            # plt.gca().autoscale(tight=True, axis="y")
            #plt.gca().relim()
            #plt.gca().autoscale(axis="y")
            # plt.gca().autoscale_view(tight=True, scalex=False)

            plt.pause(0.0001)

            if 0:
                ax = plt.gca()
                ax.relim()
                ax.autoscale_view(None, False, True)
                ax.redraw_in_frame()

        measi += 1
        tlast = time.time()


if __name__ == "__main__":
    main()

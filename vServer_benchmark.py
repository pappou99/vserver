#! /usr/bin/python3

import time, datetime
import os

from vServer_settings import Settings

class Benchmark:
    def __init__(self):
        v_enc_name = Settings.v_enc[0]
        a_enc_name = Settings.a_enc[0]

        day = datetime.date.today()
        t = time.localtime()
        now = str(time.strftime("%H:%M:%S", t))

        path = '/home/administrator/pappou/gstreamwebcam/benchmark/logging/'
        filename = '%s_%s_%s_%s.nmon' % (v_enc_name, a_enc_name, day, now)
        logfile = '%s%s' % (path, filename)
        # mode = 'a' if os.path.exists(logfile) else 'w'
        # with open(logfile, mode) as f:
        #     f.write('')
        os.system("nmon -c 300 -s 1 -T -F %s" % logfile)
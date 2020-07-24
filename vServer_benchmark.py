#! /usr/bin/python3

import time, datetime
import os

from vServer_settings import Settings

class Benchmark:
    """
    Class for external benchmark logging via nmon
    Change the path to a folder where your logging files will be written to.
    """

    def __init__(self):
        v_enc_name = Settings.v_enc[0]
        a_enc_name = Settings.a_enc[0]

        day = datetime.date.today()
        t = time.localtime()
        now = str(time.strftime("%H:%M:%S", t))
        cwd = os.getcwd()

        path = '%s/benchmark/logging/' % cwd # write files to a subfolder of current working directory
        filename = '%s_%s_%sStreams_%s_%s.nmon' % (day, now, Settings.num_streams, v_enc_name, a_enc_name)
        logfile = '%s%s' % (path, filename)
        # mode = 'a' if os.path.exists(logfile) else 'w'
        # with open(logfile, mode) as f:
        #     f.write('')
        os.system("nmon -c 300 -s 1 -T -F %s" % logfile)
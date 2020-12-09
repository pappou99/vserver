#! /usr/bin/python3
#
# Copyright (c) 2020 pappou (Björn Bruch).
#
# This file is part of vServer 
# (see https://github.com/pappou99/vserver).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

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

        path = Settings.benchmark_location
        filename = '%s_%s_%sStreams_%s_%s.nmon' % (day, now, Settings.num_streams, v_enc_name, a_enc_name)
        logfile = '%s/%s' % (path, filename)
        # mode = 'a' if os.path.exists(logfile) else 'w'
        # with open(logfile, mode) as f:
        #     f.write('')
        os.system("nmon -c 300 -s 1 -T -F %s" % logfile)

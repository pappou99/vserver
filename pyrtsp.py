#! /usr/bin/python

# pyrtsp - RTSP test server hack
# Copyright (C) 2013  Robert Swain <robert.swain@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import gi
<<<<<<< HEAD
gi.require_version('Gst','1.0')
=======

gi.require_version('Gst','1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('GstRtspServer','1.0')

>>>>>>> 9c795dd81bbe1e3d9dc1952cd10f64dce927437a
from gi.repository import GObject, Gst, GstVideo, GstRtspServer

Gst.init(None)


mainloop = GObject.MainLoop()
<<<<<<< HEAD

=======
>>>>>>> 9c795dd81bbe1e3d9dc1952cd10f64dce927437a
server = GstRtspServer.RTSPServer()

mounts = server.get_mount_points()

factory = GstRtspServer.RTSPMediaFactory()
<<<<<<< HEAD
factory.set_launch('( videotestsrc is-live=1 ! x264enc speed-preset=ultrafast tune=zerolatency ! rtph264pay name=pay0 pt=96 )')
=======
# factory.set_launch('( videotestsrc is-live=1 ! x264enc speed-preset=ultrafast tune=zerolatency ! rtph264pay name=pay0 pt=96 )')
factory.set_launch('( audiotestsrc is-live=1 do-timestamp=true ! audio/x-raw,channels=8 ! tee name=audio audio. ! queue ! audioconvert ! audioresample ! queue ! jackaudiosink connect=0 client-name=Video1 audio. ! deinterleave name=d interleave channel-positions-from-input=true name=i ! audioconvert ! a_enc. d.src_0 ! i.sink_0 opusenc name=a_enc ! mux. videotestsrc ! videoconvert ! videoscale ! video/x-raw,width=1920,height=1080 ! avenc_mpeg4 ! mpegtsmux alignment=7 name=mux ! rtpmp2tpay ! name=pay0 pt=96 )')
>>>>>>> 9c795dd81bbe1e3d9dc1952cd10f64dce927437a

mounts.add_factory("/test", factory)

server.attach(None)

<<<<<<< HEAD
print "stream ready at rtsp://127.0.0.1:8554/test"
=======
print ("stream ready at rtsp://127.0.0.1:8554/test")
>>>>>>> 9c795dd81bbe1e3d9dc1952cd10f64dce927437a
mainloop.run()

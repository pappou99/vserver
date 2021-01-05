from tkinter.ttk import Widget

import gi

# Needed for set_window_handle():
gi.require_version('GstVideo', '1.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstVideo, GObject


class GstWidget(Widget):
    def __init__(self, gst_launch_string, x, y, width, height, master=None, **kw):
        super(GstWidget, self).__init__(master, 'frame', **kw)

        self.place(x=x, y=y, width=width, height=height)

        self.frame_id = self.winfo_id()

        self.player = Gst.parse_launch(gst_launch_string)
        self.player.set_state(Gst.State.PLAYING)

        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.on_error)
        self.bus.connect('message::state-changed', self.on_status_changed)
        self.bus.connect('message::eos', self.on_eos)
        self.bus.connect('message::info', self.on_info)
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.set_frame_handle)

    def on_status_changed(self, bus, message):
        print('status_changed message -> {}'.format(message))

    def on_eos(self, bus, message):
        print('eos message -> {}'.format(message))

    def on_info(self, bus, message):
        print('info message -> {}'.format(message))

    def on_error(self, bus, message):
        print('error message -> {}'.format(message.parse_error()))

    def play(self):
        print('Current state of my pipeline is {}'.format(self.player.current_state))
        print('setting pipeline state to playing')
        self.player.set_state(Gst.State.PLAYING)

    def close(self):
        self.player.set_state(Gst.State.NULL)

    def is_playing(self):
        print('\t\t{}'.format(self.player.current_state))
        return self.player.current_state is not Gst.State.PLAYING

    def set_frame_handle(self, bus, message):
        if message.get_structure().get_name() == 'prepare-window-handle':
            frame = message.src
            frame.set_property('force-aspect-ratio', True)
            frame.set_window_handle(self.frame_id)
            

def refreshApp():
    app.update()
    return True

GObject.idle_add(refreshApp)
loop = GObject.MainLoop()
loop.run()
    
app=GstWidget()
#! /usr/bin/python3
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GdkX11', '3.0')
from gi.repository import Gtk, GdkX11
from vServer import Settings

Gtk.init(None)

class Ui:

    def __init__(self):
        
        print('Building Ui')
        self.main_window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.main_window.connect(self, "delete-event", self.on_delete_event)
        self.main_hbox = Gtk.HBox.new(False, 0)
        
    def controls_per_stream(self, stream):
        box = Gtk.VBox.new(False, 0)
        stream_info = Gtk.TextView.new()
        stream_info.set_editable(False)
        play = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_PLAY)
        play.connect("clicked", Settings.streams[stream].start())
        stop = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_STOP)
        stop.connect("clicked", self.on_stop, stream)
        box.pack_start(play, False, False, 2)
        box.pack_start(stop, False, False, 2)
        self.main_hbox.add(box)

    def on_run(self, stream):
        print("Stasdf")
        stream.run()

    def on_stop(self, stream):
        pass

        # Gtk.main()
    def show(self):
        self.main_window.add(self.main_hbox)
        self.main_window.set_default_size(640, 480)
        self.main_window.show_all()
        Gtk.main()

    # this function is called when the main window is closed
    def on_delete_event(self, widget, event):
        for stream in range(0, Settings.num_streams, 1):
            Settings.streams[stream].pipeline.set_state(Gst.State.READY)
        Gtk.main_quit()



    #######
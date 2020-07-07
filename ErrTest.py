#! /usr/bin/python3
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GdkX11', '3.0')
from gi.repository import Gtk

Gtk.init(None)

class Settings:
    robots = []

class PossibleInputs:
    pass

class Main:
    def __init__(self):
        choice = int(input("Type in a number between 1 and 12\n"))
        ui = Ui()
        for num in range(0, choice, 1):
            Settings.robots.append(num)
            Settings.robots[num] = Robot(num)
            Settings.robots[num].number = num
            ui.build_ctl_per_robot(Settings.robots[num])
        print("showing ui")
        ui.show()
class Ui(Main):
    def __init__(self):
        print('Building Ui')
        self.main_window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.main_window.connect("delete-event", self.on_delete_event)
        self.main_hbox = Gtk.HBox.new(False, 0)
        
    def build_ctl_per_robot(self, robot):
        print("Building controls for robot")
        box = Gtk.VBox.new(False, 0)
        play = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_PLAY)
        play.connect("clicked", self.on_run, robot)
        stop = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_STOP)
        stop.connect("clicked", self.on_stop, robot)
        box.pack_start(play, False, False, 2)
        box.pack_start(stop, False, False, 2)
        self.main_hbox.add(box)

    def show(self):
        self.main_window.add(self.main_hbox)
        self.main_window.show_all()
        Gtk.main()

    def on_run(self, robot):
        robot.run()

    def on_stop(self, robot):
        pass

    def on_delete_event(self, widget, event):
        Gtk.main_quit()

class Robot:

    def __init__(self, number):
        self.number = number

    def run(self):
        print('Starting robot %s' % self.number)

Main()
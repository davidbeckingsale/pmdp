#!/bin/env python

import gtk
import markdown
import webkit
import sys
import gio
import os
import urllib

class Gui(object):
    def _quit(self, *args):
        gtk.main_quit()

    def __init__(self):
        self.mdfile = None
        self.file_name = None

        # if we pass an argument, load this file, will allow us to run
        # pmpd quickly from the command line.
        if (len(sys.argv) > 1):
            self.mdfile = sys.argv[1]
            self.file_name = self.mdfile.split(".")[0]

            self.text = ""
        # if no argument, set up the welcome page
        else:
            self.text = """
# Welcome to PMDP

This is PMDP, an auto-refreshing [markdown][md] previewer for
Linux.

You can either drop a markdown file here, or launch PMDP with
a markdown file as the argument, e.g. `pmdp test.md`

[md]: http://daringfireball.net/projects/markdown/
"""

        self.htmltext = ""

        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title('PMDP')

        window.connect_after('destroy', self._quit)
        window.maximize()

        self.main_box = gtk.VBox()

        self.wv = webkit.WebView()
        ws = self.wv.get_settings()
        ws.set_property('enable-plugins',False)
        self.wv.set_settings(ws)
        out_scroll = gtk.ScrolledWindow()
        out_scroll.add(self.wv)
        out_scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)


        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_START)
        savebutton = gtk.Button("Save HTML")
        savebutton.connect("clicked", self.write_html)
        bbox.pack_start(savebutton,False,False,0)

        self.main_box.pack_start(bbox,False, False, 0)
        self.main_box.pack_start(out_scroll, True, True, 0)

        window.add(self.main_box)

        window.show_all()

        if self.mdfile != None:
            self.update_from_file(None, None, None, None)
            self.monitor_file()
        else:
            self.render()
            self.update_html()

        self.wv.connect('drag_motion', self.motion_cb)
        self.wv.connect('drag_drop', self.drop_cb)
        self.wv.connect('drag_data_received', self.got_data_cb)

        gtk.main()

    def monitor_file(self):
        """Start monitoring the file"""
        file = gio.File(self.mdfile)
        monitor = file.monitor_file()
        monitor.connect ("changed", self.update_from_file) 

    def read_file(self):
        """Read the file into the text variable """
        with open(self.mdfile) as f:
            self.text = f.read()

    def render(self):
        """Render self.text as markdown, store in html_text"""
        self.htmltext = markdown.markdown(self.text)

    def update_html(self):
        """Update the html in the webview"""
        if self.file_name != None:
            self.wv.load_html_string(self.htmltext, self.file_name+".html")
        else:
            self.wv.load_html_string(self.htmltext, "file:///")

    def update_from_file(self, monitor=None, file=None, unknown=None, event=None):
        """Re-read the file and update the rendered text and the web view."""
        self.read_file()
        self.render()
        self.update_html()

    def write_html(self, widget):
        """Write the rendered html to a file, with the same name as the 
            markdown file."""
        htmlfile = self.file_name+".html"

        with open(htmlfile, 'w') as f:
            f.write(self.htmltext)

    def motion_cb(self, wid, context, x, y, time):
        context.drag_status(gtk.gdk.ACTION_COPY, time)
        # Returning True which means "I accept this data".
        return True

    def drop_cb(self, wid, context, x, y, time):
        # Some data was dropped, get the data
        wid.drag_get_data(context, context.targets[-1], time)
        return True

    def got_data_cb(self, wid, context, x, y, data, info, time):
        # Got data.

        uri = data.data.strip('\r\n\x00')
        uri_splitted = uri.split() # we may have more than one file dropped

        for uri in uri_splitted:
            path = self.get_file_path_from_dnd_dropped_uri(uri)
            if os.path.isfile(path): # is it file?
                self.mdfile = path

        self.monitor_file()
        self.update_from_file()
        context.finish(True, False, time) 

    def get_file_path_from_dnd_dropped_uri(self, uri):
        # get the path to file
        path = ""
        if uri.startswith('file:\\\\\\'): # windows
            path = uri[8:] # 8 is len('file:///')
        elif uri.startswith('file://'): # nautilus, rox
            path = uri[7:] # 7 is len('file://')
        elif uri.startswith('file:'): # xffm
            path = uri[5:] # 5 is len('file:')

        path = urllib.url2pathname(path) # escape special chars
        path = path.strip('\r\n\x00') # remove \r\n and NULL

        return path

if __name__ == '__main__':
    demo = Gui()


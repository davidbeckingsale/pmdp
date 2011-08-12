#!/bin/env python

import gtk
import markdown
import webkit
import sys
import gobject
import gio

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
            file = gio.File(self.mdfile)
            monitor = file.monitor_file()
            monitor.connect ("changed", self.update_from_file) 
        else:
            self.render()
            self.update_html()

        gtk.main()


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

    def update_from_file(self, monitor, file, unknown, event):
        """Re-read the file and update the rendered text and the web view."""
        self.read_file()
        self.render()
        self.update_html()

    def write_html(self, widget):
        htmlfile = self.file_name+".html"

        with open(htmlfile, 'w') as f:
            f.write(self.htmltext)


if __name__ == '__main__':
    demo = Gui()


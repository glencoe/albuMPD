import lib.TcpFileView
import lib.MpdClient
import socket
import lib.Library
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


class Handler:

    def __init__(self, lib, builder):
        self._lib = lib
        self._last_chosen_artist = None
        self._builder = builder

    def artist_list_view_cursor_changed_cb(self, *artist_view):
        artist_view = artist_view[0]
        (model, pathlist) = artist_view.get_selection().get_selected_rows()
        for path in pathlist:
            tree_iter = model.get_iter(path)
            value = model.get_value(tree_iter, 0)
            if value != self._last_chosen_artist:
                self._last_chosen_artist = value
                album_store = self._builder.get_object('album_store')
                album_store.clear()
                for album in lib.search('albumartist', value):
                    album.fetch_cover()
                    album_pic = GdkPixbuf.Pixbuf.new_from_file(album.get_cover_path())
                    album_store.append([album.title(), album_pic])



builder = Gtk.Builder()
tcp_file_view = lib.TcpFileView.TcpFileView(socket)
client = lib.MpdClient.MpdClient(tcp_file_view, logger=sys.stdout)
lib = lib.Library.Library(client, logger=sys.stdout)
client.connect("hal", 6600)
lib.get_artists()
builder.add_from_file("gui.glade")
artist_store = builder.get_object("artist_store")
artist_view = builder.get_object('artist_list_view')
artist_name_col = Gtk.TreeViewColumn("Artist", Gtk.CellRendererText(), text=0)
album_view = builder.get_object('album_view')
album_view.set_pixbuf_column(1)
album_view.set_text_column(0)
artist_view.append_column(artist_name_col)
for artist in lib.artists():
    artist_store.append([artist.name()])

win = builder.get_object("main_window")
builder.connect_signals(Handler(lib, builder))
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

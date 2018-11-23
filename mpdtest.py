import lib.TcpFileView
import lib.MpdClient
import socket
import lib.Library
import sys

tcp_file_view = lib.TcpFileView.TcpFileView(socket)
client = lib.MpdClient.MpdClient(tcp_file_view, logger=sys.stdout)

client.connect("hal", 6600)

lib = lib.Library.Library(client, logger=sys.stdout)

artists = lib.get_artists()
print(artists[0])
print(artists[0].get_albums())
artists[0].get_albums()[0].fetch_cover()

client.shutdown()

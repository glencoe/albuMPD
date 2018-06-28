class Library:

    def __init__(self, client):
        self._client = client
        self._albums = []

    def refresh(self):
        self._albums = [Album(album_dict, self._client)
                       for album_dict in self._client.list("albumartist",
                                                           group_tags=["album",
                                                                       "musicbrainz_albumid"])]

    def search(self, term):
        return [Album(album_dict, self._client)
                for album_dict in self._client.list("albumartist",
                                                    group_tags=[
                                                        "album",
                                                        "musicbrainz_albumid"],
                                                    filter=term)]

    def get(self):
        if len(self._albums) == 0:
            self.refresh()
        return self._albums

    def albums(self):
        return self.get()



class Album:

    def __init__(self, album_dict, client):
        self._album_dict = album_dict
        self._client = client
        self._songs = []

    def album_artist(self):
        return self._album_dict.AlbumArtist

    def id(self):
        return self._album_dict.MUSICBRAINZ_ALBUMID

    def title(self):
        return self._album_dict.Album

    def songs(self):
        song_dicts = self._client.find("musicbrainz_albumid {}".format(self.id()))
        self._songs = [Song(song_dict, self._client) for song_dict in song_dicts]

    def __repr__(self):
        result = "<ALBUM "
        for key in self._album_dict:
            result += "{}: {}; ".format(key, self._album_dict[key])
        result = result.rstrip("; ") + ">"
        return result


class Song:

    def __init__(self, song_dict, client):
        self._song_dict = song_dict
        self._client = client

    def time(self):
        return self._song_dict.Time

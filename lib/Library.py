class Library:

    def __init__(self, client):
        self._client = client

    def get(self):
        return self._client.list("albumartist", group_tags=["album"])


class Album:

    def __init__(self, album_dict, client):
        self._album_dict = album_dict
        self._client = client

    def album_artist(self):
        return self._album_dict.AlbumArtist

    def id(self):
        return self._album_dict.MUSICBRAINZ_ALBUMID

    def title(self):
        return self._album_dict.Album


class Track:

    def __init__(self, track_dict, client):
        self._track_dict = track_dict
        self._client = client
import os.path


class Library:

    def __init__(self, client):
        self._client = client
        self._albums = []
        self._group_tags = ["album", "musicbrainz_albumid",
                            "albumartistsort", "genre"]
        self._primary_list_tag = "albumartist"

    def refresh(self):
        self._albums = [Album(album_dict, self._client)
                        for album_dict in self._client.list(self._primary_list_tag,
                                                            group_tags=self._group_tags)]

    def search(self, field, term):
        return [Album(album_dict, self._client)
                for album_dict in self._client.list(self._primary_list_tag,
                                                    filter=[field, term],
                                                    group_tags=self._group_tags)]

    def get(self):
        if len(self._albums) == 0:
            self.refresh()
        return self._albums

    def albums(self):
        return self.get()


class Album:

    def __init__(self, album_dict, client, cover_dir=""):
        self._album_dict = album_dict
        self._client = client
        self._songs = []
        self._cover_dir = cover_dir

    def album_artist(self):
        return self._album_dict['albumartist']

    def directory(self):
        first_song = self.songs()[0].file()
        album_dir = os.path.dirname(first_song)
        return album_dir

    def id(self):
        return self._album_dict['musicbrainz_albumid']

    def title(self):
        return self._album_dict['album']

    def has_id(self):
        return 'musicbrainz_albumid' in self._album_dict

    def songs(self):
        if len(self._songs) == 0:
            try:
                song_dicts = self._client.find("musicbrainz_albumid", self.id())
            except KeyError:
                song_dicts = self._client.find('album', self.title(), 'albumartist', self.album_artist())
            self._songs = [Song(song_dict, self._client) for song_dict in song_dicts]
        return self._songs

    def __repr__(self):
        result = "<ALBUM "
        for key in self._album_dict:
            result += "{}: {}; ".format(key, self._album_dict[key])
        result = result.rstrip("; ") + ">"
        return result

    def get_cover_path(self):
        return os.path.join(self._cover_dir, self.id() + ".jpg")

    def update_cover(self):
        if self.has_id():
            song_url = self.songs()[0].file()
            data = self._client.album_art(song_url)
            file = open(
                self.get_cover_path(),
                'w+b')
            file.write(data)
            file.close()


class Song:

    def __init__(self, song_dict, client):
        self._song_dict = song_dict
        self._client = client

    def time(self):
        return self._song_dict['time']

    def uri(self):
        return self._song_dict['file']

    def file(self):
        return self.uri()

    def album_id(self):
        return self._song_dict['musicbrainz_albumid']

    def __repr__(self):
        return repr(self._song_dict)

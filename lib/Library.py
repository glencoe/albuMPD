import os.path
import hashlib


class Library:

    def __init__(self, client, logger=None):
        self._client = client
        self._albums = []
        self._group_tags = ["album", "musicbrainz_albumid",
                            "albumartistsort", "genre"]
        self._primary_list_tag = "albumartist"
        self._logger = logger
        self._artists = []

    def get_albums(self):
        self._albums = [Album(album_dict, self._client, logger=self._logger)
                        for album_dict in self._client.list(self._primary_list_tag,
                                                            group_tags=self._group_tags)]

    def search(self, field, term):
        return [Album(album_dict, self._client, logger=self._logger)
                for album_dict in self._client.list(self._primary_list_tag,
                                                    filter=[field, term],
                                                    group_tags=self._group_tags)]

    def get_artists(self):
        """
        Here we get all artists. However the call to client.list
        will return some of them more than once e.g.
        1. albumartist: AC/DC
        2. albumartist: AC/DC
           albumartistsort: AC/DC
        This is due to some files not having the correct albumartistsort tag.
        To merge all of these occurences with the cases where a correct albumartistsort
        tag is present, we fill a dictionary with the albumartist tags as keys and
        Artist objects as values. An entry is updated as soon as a better data set
        for an artist is found. Assuming that we have a better data set, if albumartist
        and albumartistsort tag are different.
        """
        artists = {}
        for artist_dict in self._client.list(self._primary_list_tag,
                                             group_tags=['albumartistsort']):
            artist = Artist(artist_dict, self._client)
            if artist.name() not in artists or artist.name() != artist.sort_name():
                artists[artist.name()] = artist
        artists = [artists[key] for key in artists]
        artists.sort()
        self._artists = artists
        return self._artists

    def artists(self):
        return self._artists

    def albums(self):
        return self._albums

    def _log(self, ob):
        if self._logger is not None:
            self._logger.write(repr(ob))


class Artist:

    def __init__(self, artist_dict, client, hash_obj=hashlib.md5()):
        self._client = client
        self._artist_dict = artist_dict
        self._group_tags = ["album", "musicbrainz_albumid",
                            "albumartistsort", "genre"]
        hash_obj.update(self.name().encode())
        self._hash = hash_obj.digest()

    def name(self):
        return self._artist_dict['albumartist']

    def get_albums(self):
        self._client.list('album',
                          group_tags=self._group_tags,
                          filter=['albumartist', self._name])

    def hash(self):
        return self._hash

    def sort_name(self):
        if 'albumartistsort' not in self._artist_dict \
                or self._artist_dict['albumartistsort'] == '':
            return self._artist_dict['albumartist']
        else:
            return self._artist_dict['albumartistsort']

    def __repr__(self):
        return repr(self._artist_dict)

    def __lt__(self, other):
        return self.sort_name().lower() < other.sort_name().lower()


class Album:

    def __init__(self, album_dict, client, cover_dir="", logger=None, calc_hash=hashlib.md5()):
        self._album_dict = album_dict
        self._client = client
        self._songs = []
        self._cover_dir = cover_dir
        self._logger = logger
        calc_hash.update(self.album_artist().encode() + b"////" + self.title().encode())
        self._hash = calc_hash.digest()

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

    def hash(self):
        return self._hash

    def songs(self):
        if len(self._songs) == 0:
            try:
                song_dicts = self._client.find("musicbrainz_albumid", self.id())
            except KeyError:
                song_dicts = self._client.find('album', self.title(), 'albumartist', self.album_artist())
            self._songs = [Song(song_dict, self._client) for song_dict in song_dicts]
        return self._songs

    def update_cover(self):
        self._log("downloading cover for {} - {} to {}\n".format(self.album_artist(),
                                                               self.title(),
                                                               self.get_cover_path()))
        if self.has_id():
            song_url = self.songs()[0].file()
            data = self._client.album_art(song_url)
            file = open(
                self.get_cover_path(),
                'w+b')
            file.write(data)
            file.close()

    def __repr__(self):
        result = "<ALBUM "
        for key in self._album_dict:
            result += "{}: {}; ".format(key, self._album_dict[key])
        result = result.rstrip("; ") + ">"
        return result

    def get_cover_path(self):
        return os.path.join(self._cover_dir, self.id() + ".jpg")

    def _log(self, string):
        if self._logger is not None:
            self._logger.write(string)

    def __lt__(self, other):
        return self.title().lower() < other.title().lower()


class Song:

    def __init__(self, song_dict, client, hash_obj=hashlib.md5()):
        self._song_dict = song_dict
        self._client = client
        hash_obj.update(self.uri())
        self._hash = hash_obj.digest()

    def time(self):
        return self._song_dict['time']

    def uri(self):
        return self._song_dict['file']

    def hash(self):
        return self._hash

    def file(self):
        return self.uri()

    def album_id(self):
        return self._song_dict['musicbrainz_albumid']

    def __repr__(self):
        return repr(self._song_dict)

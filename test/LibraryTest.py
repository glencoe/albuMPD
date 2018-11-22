import unittest
import hashlib
from unittest.mock import create_autospec, call
from lib.TcpFileView import TcpFileView
from lib.MpdClient import MpdClient, MpdClientError
from lib.Library import Album, Song

class SongTest(unittest.TestCase):

    def setUp(self):
        self._client = create_autospec(MpdClient)
        self._song_dict = {
            'file': '/path/to/file.flac',
            'time': '3:12',
            'musicbrainz_albumid': 'abcde123',
            }
        self._song = Song(self._song_dict, self._client)

    def test_songs_time(self):
        first = Song(self._song_dict, self._client)
        self.assertEqual(self._song_dict['time'], self._song.time())

    def test_songs_uri(self):
        self.assertEqual(self._song_dict['file'], self._song.uri())

    def test_songs_hash(self):
        hash_obj = hashlib.md5()
        hash_obj.update(self._song_dict['file'].encode())
        expected_hash = hash_obj.digest()
        self.assertEqual(expected_hash, self._song.hash())

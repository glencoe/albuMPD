import unittest
from lib.ResponseParser import parse_response


class ResponseParserTest(unittest.TestCase):
    def test_parse_one_line(self):
        response = "Artist: Some Random Artist"
        result = parse_response(response)
        self.assertEqual(
            [{"artist": "Some Random Artist"}],
            result
                         )
        response = "AlbumArtist: New Order"
        result = parse_response(response)
        self.assertEqual(
            [{"albumartist": "New Order"}],
            result
        )

    def test_parse_two_lines(self):
        response = "artist: MyArtist\n" \
                   "album: MyAlbum"
        result = parse_response(response)
        self.assertEqual(
            [{"artist": "MyArtist",
              "album": "MyAlbum"}],
            result
        )

    def test_parse_two_groups(self):
        response = "artist: Prince\n" \
                   "album: Dirty Mind\n" \
                   "artist: David Bowie\n" \
                   "album: Heroes"
        result = parse_response(response)
        self.assertEqual(
            [
                {
                    "artist": "Prince",
                    "album": "Dirty Mind",
                },
                {
                    "artist": "David Bowie",
                    "album": "Heroes",
                },
            ],
            result
        )


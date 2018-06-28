import unittest
from lib.ResponseParser import parse_response


class ResponseParserTest(unittest.TestCase):
    def test_parse_one_line(self):
        response = "Artist: Some Random Artist"
        result = parse_response(response)
        self.assertEqual(
            [{"Artist": "Some Random Artist"}],
            result
                         )
        response = "AlbumArtist: New Order"
        result = parse_response(response)
        self.assertEqual(
            [{"AlbumArtist": "New Order"}],
            result
        )

    def test_parse_two_lines(self):
        response = "Artist: MyArtist\n" \
                   "Album: MyAlbum"
        result = parse_response(response)
        self.assertEqual(
            [{"Artist": "MyArtist",
              "Album": "MyAlbum"}],
            result
        )

    def test_parse_two_groups(self):
        response = "Artist: Prince\n" \
                   "Album: Dirty Mind\n" \
                   "Artist: David Bowie\n" \
                   "Album: Heroes"
        result = parse_response(response)
        self.assertEqual(
            [
                {
                    "Artist": "Prince",
                    "Album": "Dirty Mind",
                },
                {
                    "Artist": "David Bowie",
                    "Album": "Heroes",
                },
            ],
            result
        )


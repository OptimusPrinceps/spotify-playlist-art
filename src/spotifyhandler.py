from datetime import datetime, timedelta
from io import BytesIO
from urllib.parse import urljoin

import requests
from PIL import Image

from secret import client_id, client_secret


class AlbumImage:
    def __init__(self, image_bytes):
        self.image = Image.open(BytesIO(image_bytes))
        self.image_bytes = image_bytes


class SpotifyAlbum:
    def __init__(self, name, artists, genres, album_art_url, tracks):
        self.name = name
        self.artists = artists
        self.genres = genres
        self.tracks = tracks

        self.album_art: AlbumImage = self._get_album_art(album_art_url)

    @classmethod
    def _get_album_art(cls, album_art_url) -> Image:
        image_bytes = requests.get(album_art_url).content
        return AlbumImage(image_bytes)

    @classmethod
    def from_api_response(cls, api_response):
        name = api_response['name']
        artists = [artist['name'] for artist in api_response['artists']]
        genres = api_response['genres']
        album_art_url = api_response['images'][0]['url']
        tracks = api_response['tracks']['items']
        return cls(name, artists, genres, album_art_url, tracks)


class Spotify:
    base_url = 'https://api.spotify.com/v1/'

    def __init__(self):
        self._token = None
        self._refresh_at = None

    def _refresh_token(self):
        url = 'https://accounts.spotify.com/api/token'
        data = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret}
        response = requests.post(url, data=data).json()

        self._token = response['access_token']

        expiry = response['expires_in']
        self._refresh_at = datetime.now() + timedelta(seconds=expiry - 60)

    @property
    def _auth_header(self) -> dict:
        if self._token is None or datetime.now() > self._refresh_at:
            self._refresh_token()
        return {'Authorization': f'Bearer {self._token}'}

    def _make_request(self, route, params=None) -> dict:
        """
        Makes GET requests
        """
        url = urljoin(self.base_url, route)
        response = requests.get(url, headers=self._auth_header, params=params)
        response.raise_for_status()

        return response.json()

    def get_playlists(self, user_id) -> list[dict]:
        playlists = self._make_request(f'users/{user_id}/playlists', params={'limit': 50})
        return playlists['items']

    def get_tracks(self, playlist_id) -> list[dict]:
        all_tracks = []
        next_url = f'playlists/{playlist_id}/tracks'
        while next_url is not None:
            tracks = self._make_request(next_url)
            all_tracks.extend(tracks['items'])
            next_url = tracks['next']

        tracks = [track['track'] for track in all_tracks if track['track']]
        return tracks

    def search(self, query, types: list[str] = None):
        """
        Docs: https://developer.spotify.com/documentation/web-api/reference/search
        """
        if types is None:
            types = ["album", "artist", "playlist", "track"]

        route = 'search'
        params = {
            'q': query,
            'type': types
        }
        results = self._make_request(route, params)
        return results

    def get_album(self, album_href) -> SpotifyAlbum:
        album = self._make_request(album_href)
        return SpotifyAlbum.from_api_response(album)

    def get_lyrics(self, track_id) -> list[str]:
        response = requests.get('https://spotify-lyric-api.herokuapp.com', params={'track_id': track_id})
        content = response.json()
        if 'lines' not in content:
            return []
        lines = content['lines']
        lyrics = [line['words'] for line in lines if line['words']]
        return lyrics


spotify = Spotify()

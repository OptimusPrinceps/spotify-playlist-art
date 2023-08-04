from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests

from secret import client_id, client_secret


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

    def make_request(self, route, params=None) -> dict:
        """
        Makes GET requests
        """
        url = urljoin(self.base_url, route)
        response = requests.get(url, headers=self._auth_header, params=params)
        response.raise_for_status()

        return response.json()

    def get_playlists(self, user_id) -> list[dict]:
        playlists = self.make_request(f'users/{user_id}/playlists', params={'limit': 50})
        return playlists['items']

    def get_track_names(self, playlist_id) -> list[str]:
        all_tracks = []
        next_url = f'playlists/{playlist_id}/tracks'
        while next_url is not None:
            tracks = self.make_request(next_url)
            all_tracks.extend(tracks['items'])
            next_url = tracks['next']

        track_names = [track['track']['name'] for track in all_tracks]
        return track_names

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
        results = self.make_request(route, params)
        return results

    def get_lyrics(self, track_id) -> list[str]:
        response = requests.get('https://spotify-lyric-api.herokuapp.com', params={'track_id': track_id})
        content = response.json()
        lines = content['lines']
        lyrics = [line['words'] for line in lines if line['words']]
        return lyrics


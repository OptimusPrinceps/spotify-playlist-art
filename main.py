from datetime import datetime, timedelta
from random import shuffle
from urllib.parse import urljoin

import openai
import requests
from secret import client_id, client_secret


class OpenAI:
    @classmethod
    def chat_complete(cls, roles_and_messages: list[tuple[str, str]]):
        prompt = [{'role': role, 'content': message} for role, message in roles_and_messages]
        response = openai.ChatCompletion.create(model='gpt-4', messages=prompt, stream=False)
        return response.choices[0].text



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
    def _auth_header(self):
        if self._token is None or datetime.now() > self._refresh_at:
            self._refresh_token()
        return {'Authorization': f'Bearer {self._token}'}

    def _make_request(self, route, params=None):
        url = urljoin(self.base_url, route)
        response = requests.get(url, headers=self._auth_header, params=params)
        response.raise_for_status()

        return response.json()

    def get_playlists(self, user_id) -> list[dict]:
        playlists = self._make_request(f'users/{user_id}/playlists', params={'limit': 50})
        return playlists['items']

    def get_tracks(self, playlist_id):
        all_tracks = []
        next_url = f'playlists/{playlist_id}/tracks'
        while not next_url:
            tracks = self._make_request(next_url)
            all_tracks.extend(tracks['items'])
            next_url = tracks['next']

        return all_tracks


class UserInterface:
    @classmethod
    def get_user_id(cls):
        user_id_or_link = input('Please provide your Spotify user ID or link to your profile: ')
        return user_id_or_link.split('/')[-1]

    @classmethod
    def choose_playlist(cls, playlists):
        print('\nFound the following playlists:\n')
        for i, playlist in enumerate(playlists):
            print(f'{i + 1}. {playlist["name"]}')

        playlist_index = int(input('\n\nPlease enter your choice of playlist: '))
        return playlists[playlist_index - 1]['id']

    @classmethod
    def get_playlist_genre(cls):
        return input('Please provide the genre of the playlist: ')


if __name__ == "__main__":
    spotify = Spotify()
    user_id = UserInterface.get_user_id()
    playlists = spotify.get_playlists(user_id)

    playlist_id = UserInterface.choose_playlist(playlists)

    tracks = spotify.get_tracks(playlist_id)

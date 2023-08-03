from datetime import datetime, timedelta
from random import shuffle
from urllib.parse import urljoin

import openai
import requests
from secret import client_id, client_secret


class OpenAI:
    @classmethod
    def get_txt2img_prompt(cls, playlist_genre, track_names) -> str:
        system_prompt = 'I am trying to generate an image based on song titles.' \
                        ' You generate a prompt to provide a txt2img model.' \
                        ' The prompt should just be a list of comma separated phrases.'

        user_prompt = f'The following is a list of song titles from a {playlist_genre} playlist:\n\n'
        user_prompt += ', '.join(track_names)
        user_prompt += '\n\nPlease provide a prompt to generate an image based on this playlist.' \
                       ' The prompt should capture the essence or vibe of the song titles' \
                       ' and be no longer than 50 words.'

        roles_and_messages = [
            ('system', system_prompt),
            ('user', user_prompt)
        ]

        return cls._chat_complete(roles_and_messages)

    @classmethod
    def _chat_complete(cls, roles_and_messages: list[tuple[str, str]]) -> str:
        prompt = [{'role': role, 'content': message} for role, message in roles_and_messages]
        response = openai.ChatCompletion.create(model='gpt-4', messages=prompt, stream=False)
        return response.choices[0]['message']['content']


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
        url = urljoin(self.base_url, route)
        response = requests.get(url, headers=self._auth_header, params=params)
        response.raise_for_status()

        return response.json()

    def get_playlists(self, user_id) -> list[dict]:
        playlists = self._make_request(f'users/{user_id}/playlists', params={'limit': 50})
        return playlists['items']

    def get_track_names(self, playlist_id) -> list[str]:
        all_tracks = []
        next_url = f'playlists/{playlist_id}/tracks'
        while not next_url:
            tracks = self._make_request(next_url)
            all_tracks.extend(tracks['items'])
            next_url = tracks['next']

        track_names = [track['track']['name'] for track in all_tracks]
        return track_names


class _UserInterface:
    @classmethod
    def get_user_id(cls) -> str:
        user_id_or_link = input('Please provide your Spotify user ID or link to your profile: ')
        user_id_or_link = user_id_or_link.split('/')[-1]
        user_id_or_link = user_id_or_link.split('?')[0]
        return user_id_or_link

    @classmethod
    def choose_playlist(cls, playlists: list[dict]) -> str:
        print('\nFound the following playlists:\n')
        for i, playlist in enumerate(playlists):
            print(f'{i + 1}. {playlist["name"]}')

        print('')
        playlist_index = None
        while playlist_index not in range(1, len(playlists) + 1):
            playlist_index = int(input('Please enter your choice of playlist: '))
        return playlists[playlist_index - 1]['id']

    @classmethod
    def get_playlist_genre(cls) -> str:
        return input('Please provide the genre of the playlist: ')

    @classmethod
    def display_prompt(cls, prompt):
        print('\nHere is your prompt:\n')
        print(prompt)

    @classmethod
    def should_continue(cls) -> bool:
        should_continue = input('\n\nWould you like to continue? (y/n) ').lower() == 'y'
        print('\n-----------------------------------------\n')
        return should_continue


if __name__ == "__main__":
    spotify = Spotify()
    user_id = _UserInterface.get_user_id()
    playlists = spotify.get_playlists(user_id)

    should_continue = True
    while should_continue:
        playlist_id = _UserInterface.choose_playlist(playlists)

        track_names = spotify.get_track_names(playlist_id)

        # Shuffle for random results
        shuffle(track_names[:75])  # Limits to 75 song titles

        playlist_genre = _UserInterface.get_playlist_genre()

        stable_diffusion_prompt = OpenAI.get_txt2img_prompt(playlist_genre, track_names)

        _UserInterface.display_prompt(stable_diffusion_prompt)

        should_continue = _UserInterface.should_continue()

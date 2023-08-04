from random import shuffle

from src.openaihandler import OpenAI
from src.spotifyhandler import Spotify
from src.userinterface import UserInterface


if __name__ == "__main__":
    spotify = Spotify()

    should_continue = True
    while should_continue:
        query = UserInterface.get_query('album')
        search_result = spotify.search(query, types=['album'])

        album_href = search_result['albums']['items'][0]['href']
        album = spotify.make_request(album_href)

        UserInterface.display_album(album)

        song_lyrics = {}
        for track in album['tracks']['items']:
            track_lyrics = spotify.get_lyrics(track['id'])
            song_lyrics[track['name']] = track_lyrics


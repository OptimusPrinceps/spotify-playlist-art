from random import shuffle

from src.openaihandler import OpenAI
from src.spotifyhandler import Spotify
from src.userinterface import UserInterface


if __name__ == "__main__":
    spotify = Spotify()
    user_id = UserInterface.get_user_id()
    playlists = spotify.get_playlists(user_id)

    should_continue = True
    while should_continue:
        playlist_id = UserInterface.choose_playlist(playlists)
        playlist_genre = UserInterface.get_playlist_genre()

        track_names = spotify.get_track_names(playlist_id)
        shuffle(track_names)  # Shuffle for random results
        track_names = track_names[:50]  # Limits to 50 song titles

        stable_diffusion_prompt = OpenAI.get_txt2img_prompt(playlist_genre, track_names)

        UserInterface.display_prompt(stable_diffusion_prompt)

        should_continue = UserInterface.should_continue()

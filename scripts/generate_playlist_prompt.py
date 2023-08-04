from random import shuffle

from src.openaihandler import OpenAI
from src.spotifyhandler import Spotify
from src.stablediffusionhandler import StableDiffusion
from src.userinterface import UserInterface


def _image_gen_loop(all_track_names, playlist_genre):

    should_continue = True
    while should_continue:
        shuffle(all_track_names)  # Shuffle for random results
        track_names = all_track_names[:50]  # Limits to 50 song titles

        stable_diffusion_prompt = OpenAI.get_txt2img_prompt(playlist_genre, track_names)

        UserInterface.display_prompt(stable_diffusion_prompt)

        print('\nGenerating image with Stable Diffusion...')
        image = StableDiffusion.txt2img(stable_diffusion_prompt, negative_prompt='')
        image.show()
        image.save()

        should_continue = UserInterface.should_continue()


def main():
    spotify = Spotify()
    user_id = UserInterface.get_user_id()
    playlists = spotify.get_playlists(user_id)

    playlist_id = UserInterface.choose_playlist(playlists)
    playlist_genre = UserInterface.get_playlist_genre()

    all_track_names = spotify.get_track_names(playlist_id)

    _image_gen_loop(all_track_names, playlist_genre)


if __name__ == "__main__":
    main()

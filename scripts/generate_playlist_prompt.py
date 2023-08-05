import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from itertools import chain
from random import shuffle, sample

from src.openaihandler import OpenAI
from src.spotifyhandler import spotify
from src.stablediffusionhandler import StableDiffusion
from src.userinterface import UserInterface


def _estimate_playlist_genre(all_tracks):
    sample_size = 25
    sample_tracks = sample(all_tracks, sample_size)

    def make_request(track) -> list:
        album_id = track['album']['id']
        if album_id is None:
            return []
        album = spotify.make_request(f'albums/{album_id}')
        genres = album['genres']
        return genres

    with ThreadPoolExecutor(max_workers=sample_size) as executor:
        results = list(executor.map(make_request, sample_tracks))

    all_genres = list(chain(*results))

    if not all_genres:
        playlist_genre = input('Enter playlist genre: ')
    else:
        playlist_genre = OpenAI.summarise_genre(all_genres)
        print(f'Estimated playlist genre: {playlist_genre}')

    return playlist_genre


def _image_gen_loop(all_tracks, playlist_genre):
    playlist_genre_filename = re.sub(r'\W', '', playlist_genre)

    all_track_names = [track['name'] for track in all_tracks]
    shuffle(all_track_names)

    thread_pool = ThreadPoolExecutor(max_workers=1)
    prompt_future = thread_pool.submit(OpenAI.get_txt2img_prompt, playlist_genre, all_track_names[:50])

    should_continue = True
    while should_continue:
        track_names = all_track_names[:50]  # Limits to 50 song titles

        stable_diffusion_prompt = prompt_future.result()
        prompt_future = thread_pool.submit(OpenAI.get_txt2img_prompt, playlist_genre, track_names)

        UserInterface.display_prompt(stable_diffusion_prompt)

        image = StableDiffusion.txt2img(stable_diffusion_prompt, negative_prompt='bad art, unrealistic, ugly')
        image.show()
        image.save(playlist_genre_filename)

        if not show_images:
            should_continue = UserInterface.should_continue()

        shuffle(all_track_names)  # Shuffle for different results


def main():
    user_id = UserInterface.get_user_id()
    playlists = spotify.get_playlists(user_id)

    playlist_id = UserInterface.choose_playlist(playlists)

    all_tracks = spotify.get_tracks(playlist_id)
    playlist_genre = _estimate_playlist_genre(all_tracks)

    _image_gen_loop(all_tracks, playlist_genre)


if __name__ == "__main__":
    show_images = False
    main()

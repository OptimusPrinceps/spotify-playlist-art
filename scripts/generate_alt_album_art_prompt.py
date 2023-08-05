from concurrent.futures import ThreadPoolExecutor

from src.openaihandler import OpenAI
from src.spotifyhandler import spotify, SpotifyAlbum
from src.stablediffusionhandler import StableDiffusion
from src.userinterface import UserInterface


def _get_album() -> SpotifyAlbum:
    query = UserInterface.get_query('album')
    search_result = spotify.search(query, types=['album'])

    album_href = search_result['albums']['items'][0]['href']
    album = spotify.get_album(album_href)

    UserInterface.display_album(album)

    return album


def _get_lyric_summaries(album: SpotifyAlbum) -> dict[str, str or None]:
    print('Getting lyric summaries... ', end='')

    def _make_request(track):
        track_lyrics = spotify.get_lyrics(track['id'])
        lyric_summary = OpenAI.summarise_song_lyrics(track_lyrics) if track_lyrics else None
        return lyric_summary

    with ThreadPoolExecutor(max_workers=10) as executor:
        lyric_summaries = executor.map(_make_request, album.tracks)

    num_songs_with_lyrics = len([lyric_summary for lyric_summary in lyric_summaries])

    print(f'Found lyrics for {num_songs_with_lyrics}/{len(album.tracks)} songs.')
    if num_songs_with_lyrics == 0:
        raise ValueError('No lyrics found for any track')

    track_names = [track['name'] for track in album.tracks]
    lyrics = dict(zip(track_names, lyric_summaries))
    return lyrics


def _run_generation_loop(album: SpotifyAlbum, lyrics: dict[str, str or None], denoising):
    thread_pool = ThreadPoolExecutor(max_workers=1)
    prompt_future = thread_pool.submit(OpenAI.get_img2img_album_prompt, lyrics)

    while True:
        sd_prompt = prompt_future.result()
        UserInterface.display_prompt(sd_prompt)
        prompt_future = thread_pool.submit(OpenAI.get_img2img_album_prompt, lyrics)

        image = StableDiffusion.img2img(album.album_art, sd_prompt,
                                        negative_prompt='bad art, unrealistic, low resolution',
                                        denoising_strength=denoising)
        image.show()
        image.save(album.name)


def main():
    album = _get_album()
    lyrics = _get_lyric_summaries(album)

    denoising = 0.8
    while True:
        try:
            _run_generation_loop(album, lyrics, denoising=denoising)
        except KeyboardInterrupt:
            denoising = input('Adjust denoising strength or press enter to exit: ')
            if not denoising:
                exit()


if __name__ == "__main__":
    main()

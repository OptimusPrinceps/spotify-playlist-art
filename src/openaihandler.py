import openai

from src.spotifyhandler import SpotifyAlbum


class Models:
    GPT_3_5_TURBO = 'gpt-3.5-turbo'
    GPT_4 = 'gpt-4'


class OpenAI:
    @classmethod
    def summarise_genre(cls, genres: list[str]) -> str:
        system_prompt = 'I will provide you with a list of genres describing music on a playlist.' \
                        ' Please summarise the genre and mood of the playlist using just a few terms.'

        roles_and_messages = [
            ('system', system_prompt),
            ('user', '\n'.join(genres))
        ]
        genre_completion = cls._chat_complete(roles_and_messages, model=Models.GPT_3_5_TURBO)
        genre_completion = genre_completion.strip().replace('\n', ' ')
        return genre_completion

    @classmethod
    def get_txt2img_playlist_prompt(cls, playlist_genre, track_names) -> str:
        system_prompt = 'I am trying to generate an image based on song titles.' \
                        ' You generate a prompt to provide a txt2img model.' \
                        ' The prompt should just be a list of comma separated phrases.'

        user_prompt = f'The following is a list of song titles from a playlist.' \
                      f'The playlist is described as: {playlist_genre}.\n\n'
        user_prompt += ', '.join(track_names)
        user_prompt += '\n\nPlease provide a prompt to generate an image based on this playlist.' \
                       ' The prompt must:' \
                       '\n - Describe the mood and vibe of the song titles' \
                       '\n - Describe the mood of the playlist genre' \
                       '\n - Be no longer than 50 words.' \
                       '\n\nUse a mix of concrete and abstract terms to describe the playlist image.' \
                       ' Remember that the image should be coherent, so do not describe too many different things.'

        roles_and_messages = [
            ('system', system_prompt),
            ('user', user_prompt)
        ]

        gpt_response = cls._chat_complete(roles_and_messages)
        return cls._process_response(gpt_response)

    @classmethod
    def get_img2img_album_prompt(cls, album: SpotifyAlbum, song_lyrics: dict[str, str]):
        album_name = album.name
        # TODO

    @classmethod
    def summarise_song_lyrics(cls, lyrics: list[str]) -> str:
        system_prompt = 'I want to create digital art based on a song. I will provide you with the lyrics to the song.' \
                        'You will write a brief description of the imagery and emotions conveyed by the song.'
        roles_and_messages = [
            ('system', system_prompt),
            ('user', '\n'.join(lyrics))
        ]
        return cls._chat_complete(roles_and_messages, model=Models.GPT_3_5_TURBO)

    @classmethod
    def _chat_complete(cls, roles_and_messages: list[tuple[str, str]], model=Models.GPT_4) -> str:
        prompt = [{'role': role, 'content': message} for role, message in roles_and_messages]
        response = openai.ChatCompletion.create(model=model, messages=prompt, stream=False)
        return response.choices[0]['message']['content']

    @classmethod
    def _process_response(cls, gpt_response: str):
        if gpt_response.startswith('"'):
            gpt_response = gpt_response[1:]
        if gpt_response.endswith('"'):
            gpt_response = gpt_response[:-1]

        return gpt_response

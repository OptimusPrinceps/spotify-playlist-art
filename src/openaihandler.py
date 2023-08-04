import openai


class OpenAI:
    @classmethod
    def summarise_genre(cls, genres: list[str]) -> str:
        system_prompt = 'I will provide you with a list of genres describing music on a playlist.' \
                        ' Please summarise the genre and mood of the playlist using just a few terms.'

        roles_and_messages = [
            ('system', system_prompt),
            ('user', '\n'.join(genres))
        ]
        genre_completion = cls._chat_complete(roles_and_messages, model='gpt-3.5-turbo')
        genre_completion = genre_completion.strip().replace('\n', ' ')
        return genre_completion

    @classmethod
    def get_txt2img_prompt(cls, playlist_genre, track_names) -> str:
        system_prompt = 'I am trying to generate an image based on song titles.' \
                        ' You generate a prompt to provide a txt2img model.' \
                        ' The prompt should just be a list of comma separated phrases.'

        user_prompt = f'The following is a list of song titles from a playlist.' \
                      f'The playlist is described as: {playlist_genre}.\n\n'
        user_prompt += ', '.join(track_names)
        user_prompt += '\n\nPlease provide a prompt to generate an image based on this playlist.' \
                       ' The prompt should:' \
                       '\n - Capture the essence and vibe of the song titles' \
                       '\n - Suit the genre/mood of the playlist' \
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
    def summarise_song_lyrics(cls, lyrics: list[str]) -> str:
        system_prompt = 'I want to create digital art based on a song. I will provide you with the lyrics to the song' \
                        ' and you will provide a brief description of some appropriate imagery along with the' \
                        ' emotions conveyed.'
        roles_and_messages = [
            ('system', system_prompt),
            ('user', '\n'.join(lyrics))
        ]
        return cls._chat_complete(roles_and_messages)

    @classmethod
    def _chat_complete(cls, roles_and_messages: list[tuple[str, str]], model='gpt-4') -> str:
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

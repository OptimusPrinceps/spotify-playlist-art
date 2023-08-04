import openai


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
                       ' and be no longer than 50 words.' \
                       ' Remember that the prompt should be used to generate a coherent image.'

        roles_and_messages = [
            ('system', system_prompt),
            ('user', user_prompt)
        ]

        gpt_response = cls._chat_complete(roles_and_messages)
        return cls._process_response(gpt_response)

    @classmethod
    def _chat_complete(cls, roles_and_messages: list[tuple[str, str]]) -> str:
        prompt = [{'role': role, 'content': message} for role, message in roles_and_messages]
        response = openai.ChatCompletion.create(model='gpt-4', messages=prompt, stream=False)
        return response.choices[0]['message']['content']

    @classmethod
    def _process_response(cls, gpt_response: str):
        if gpt_response.startswith('"'):
            gpt_response = gpt_response[1:]
        if gpt_response.endswith('"'):
            gpt_response = gpt_response[:-1]

        return gpt_response

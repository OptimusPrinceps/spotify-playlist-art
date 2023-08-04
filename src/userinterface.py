class UserInterface:
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
        print('\n----------------------------------------------------------------------------------')
        return should_continue

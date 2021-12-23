import hashlib
import json
import random
import re
import string
import urllib

import requests
from spotipy import util, Spotify

CLIENT_ID = "288affe8ede54ae18fdbb4880ebfdccb"
CLIENT_SECRET = '8c70b69bfc1945adb0c5ed3b04cbb2d8'
SCOPES = 'user-library-read user-library-modify playlist-modify-private playlist-modify-public'
REDIRECT_URI = 'https://amayakasa.github.io/vk-to-spotify/'

android_client_headers = {
    'User-Agent': 'VKAndroidApp/4.13.1-1206 (Android 4.4.3; SDK 19; armeabi; ; ru)',
    'Accept': 'image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, */*'
}


def random_device_id():
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))


def params(parse=False, **args):
    if parse:
        return "".join(f'&{key}={urllib.parse.quote_plus(str(args[key]))}' for key in args if (args[key] is not None))
    else:
        return "".join(f'&{key}={args[key]}' for key in args if args[key] is not None)


def dump_to_file(name, audios):
    try:
        with open(f'{name}.json', 'w', encoding='utf-8') as target:
            json.dump([{'artist': it['artist'], 'title': it['title']} for it in audios], target, ensure_ascii=False)

        print(f'All tracks saved to {target.name}!')
    except Exception:
        raise Exception('File not found!')


def grab_dump(name):
    with open(f'{name}.json', 'r', encoding='utf-8') as target:
        return json.load(target)


def grab_token(username, scope, client_id, client_secret, redirect_uri):
    return util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)


class VKClient(object):
    session = requests.Session()
    session.headers = android_client_headers

    def __init__(self, login, password, version=5.95):
        self.version = version
        self.device_id = random_device_id()

        response = self.session.get(
            f'https://oauth.vk.com/token?grant_type=password&scope=nohttps,audio&client_id=2274003&client_secret=hHbZxrka2uZ6jB1inYsH&username={login}&password={password}',
            headers={'User-Agent': 'Mozilla/4.0 (compatible; ICS)'}
        ).json()

        if "error" in response:
            raise PermissionError('Incorrect login or password!')

        self.secret = response['secret']
        self.token = response['access_token']

        self.method('execute.getUserInfo', func_v=9),

        request = f'/method/auth.refreshToken?access_token={self.token}&v={version}&device_id={self.device_id}&lang=ru'

        self.send(request)

        print('Successfully logged in VK...')

    def method(self, method, **args):
        request = f'/method/{method}?v={self.version}&access_token={self.token}&device_id={self.device_id}{params(**args)}'

        return self.send(request, args, method)

    def send(self, url, args=None, method=None, headers=None):
        hashed = hashlib.md5((url + self.secret).encode()).hexdigest()

        if method is not None and args is not None:
            url = f'/method/{method}?v={self.version}&access_token={self.token}&device_id={self.device_id}{params(True, **args)}'
        if headers is None:
            return self.session.get('https://api.vk.com' + url + "&sig=" + hashed).json()
        else:
            return self.session.get('https://api.vk.com' + url + "&sig=" + hashed, headers=headers).json()

    def get_audios(self, count=None, file=None):
        if count is None:
            count = self.method('execute', code='return API.audio.get({count:2});')['response']['count']

        response = self.method('execute', code='return API.audio.get({count:%s});' % count)['response']

        print(f'Grabbed {len(response["items"])} tracks!')

        if file is None:
            return response['items']
        else:
            dump_to_file(file, response['items'])


class SpotifyClient:

    def __init__(self, username, client_id, client_secret, scopes, redirect_uri):
        print(f'Connecting to Spotify, authorizing as "{username}"...')

        self.username = username
        self.token = grab_token(username, scopes, client_id, client_secret, redirect_uri)
        self.client = Spotify(auth=self.token)

    def find_track_uri(self, label):
        try:
            search = self.client.search(label)

            items = search['tracks']['items']

            if len(items) > 0:
                return items[0]['uri']

        except:
            print(f"Error finding track uri for {label}")


    def grab_tracks(self, name):
        songs = grab_dump(name)

        track_uris = list()

        not_found = list()

        failed = 0
        for index, track in enumerate(songs):
            track_name = f'{track["artist"]} — {track["title"]}'

            alternative_name = re.sub("([(\[]).*?([)\]])", "\g<1>\g<2>", track_name)
            alternative_name = re.sub(r'[^\w]', ' ', alternative_name)

            found = self.find_track_uri(track_name)

            if found is None:
                found = self.find_track_uri(alternative_name)

            if found is not None:
                if found in track_uris:
                    continue

                print(f'Found: {track_name}')

                track_uris.append(found)
            else:
                failed = failed + 1
                not_found.append(track_name)

        print(f'{failed} tracks not found!')

        show = True if input('Show them? Yes - y, no - n: ') == 'y' else False

        if show:
            for track in not_found:
                print(track)

        return track_uris

    def create_playlist(self, name, public=True):
        response = self.client.user_playlist_create(self.username, name, public=public)

        if not response or not response['id']:
            return False

        print(f'Creating playlist with name "{name}"...')

        return response['id']

    def playlist_add(self, playlist_id, tracks):
        response = self.client.user_playlist_add_tracks(self.username, playlist_id, tracks[:100])

        if not response['snapshot_id']:
            return False

        # A maximum of 100 tracks can be added per request, so:
        if len(tracks) > 100:
            self.playlist_add(playlist_id, tracks[100:])

        print('Adding tracks to playlist...')


def select_that_what_you_want():
    print('Select that you want: ')
    print('1 — Grab tracks from VK to further importing')
    print('2 — Import already grabbed tracks to Spotify')
    print('Or press any other key to exit')

    try:
        mode = int(input())

        if mode == 1:
            grab_tracks_from_vk()
        elif mode == 2:
            import_tracks_to_spotify()
        else:
            exit(0)

        select_that_what_you_want()
    except Exception:
        exit(0)


def grab_tracks_from_vk():
    print('Okay, then we need to login in VK.')
    try:
        client = VKClient(input('Login: '), input('Password: '))
    except PermissionError:
        print('Oops, looks like you typed wrong login or password')
        print('Let\'s try again!')
        client = VKClient(input('Login: '), input('Password: '))

    if client:
        print('Let\'s grab your tracks, how many tracks do you need to grab?')
        print('If you wanna grab all the tracks, just write "all", if not just specify the number')
        choice = input('Well, your choice: ')
        print('Now, specify the name of the file where the tracks will be saved (ex. my-fav-songs)')
        file = input('Name: ')

        if choice.lower() == "all":
            client.get_audios(file=file)
        else:
            client.get_audios(int(choice), file=file)
    print('Okay, that\'s all!\n')


def import_tracks_to_spotify():
    print('So, you wanna import grabbed tracks to Spotify, okay.')
    username = input('Please, write your Spotify username: ')

    spotify = SpotifyClient(
        username,
        scopes=SCOPES,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI
    )

    print('Well, now specify the name of the file in which the tracks are saved')
    name = input('Name: ')

    try:
        tracks_uris = spotify.grab_tracks(name)
    except Exception:
        print('Oops, file not found, let\'s try specify name again')
        name = input('Name: ')
        tracks_uris = spotify.grab_tracks(name)

    """
    print('\nOkay, let\'s create a playlist to add tracks to')
    playlist_name = input('Type its name: ')

    print('Will its be a public playlist?')
    is_public = True if input('Yes - y, no - n: ') == 'y' else False

    playlist_id = spotify.create_playlist(playlist_name, is_public)
    """
    playlist_id  = input("Let's add these tracks to a playlist. Copy playlist id: ")

    spotify.playlist_add(playlist_id, tracks_uris)

    print('Hooray, this is a victory, enjoy the music!\n')


select_that_what_you_want()

import os
from replit import web
from flask import Flask, session, request, redirect, url_for, render_template
from flask_session import Session
import spotipy
import uuid
import concurrent.futures
from jinja2 import Environment, FileSystemLoader

import scraper

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)



def session_cache_path():
    return caches_folder + session.get('uuid')


@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private',
                                               cache_handler=cache_handler,
                                               show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template('signin.html', auth=auth_url)

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    
    playlists = getPlaylists(spotify)
    
    profile_picture = getProfilePicture(spotify)

    return render_template('results.html', playlists = playlists, display_name = spotify.me()['display_name'],
    profile_picture=profile_picture)


    

@app.route('/signout')
def signOut():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route('/playlists')
def playlists():
    sp = userConnect()
    return sp.current_user_playlists()




@app.route('/current_user')
def current_user():
    sp = userConnect()
    return sp.current_user()
@app.route('/showSongs/<string:playlist_id>')
def showSongs(playlist_id):
    print(playlist_id)
    sp = userConnect()
    
    results = sp.playlist(playlist_id=playlist_id, fields='tracks, next')
    tracks = results['tracks']

    
    songList = getSongs(tracks)

    



    # update dictionary based on song bpm and key
    # may have to make a lists of lists
    # getKeyBPM(songs)
    return render_template('songs.html', songList=songList)

def getSongs(tracks):
    
    songList = []

    
    

    def getSongList(item):
        songList.append(getSongInfo(item))
   
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(getSongList, tracks['items'])
   #for item in tracks['items']:

    
        
    return songList



def getSongInfo(item):

    track = item['track']
    name = track['name']
    artist_name = track['artists'][0]['name']


    #songs[name] = artist_name

    #print(key,bpm)
    key, bpm = scraper.findBPMandKey([artist_name, name])
    
    return [name, artist_name, bpm, key]
    
        
def getProfilePicture(sp):
    sp = userConnect()
    results =sp.me()['images'][0]
    
    return results['url']
    
def getPlaylists(sp):
    sp = userConnect()
    playlists = {}

    while True:
        curGroup = sp.current_user_playlists(limit=50)['items']
        ## Show Playlists names to screen
        ## once playlist is chosen, the playlist id will be saved
        ## cur = sp.playlist_tracks(playlist_id=)
        for item in curGroup:
            name = item['name']
            id = item['id']
            playlists[id]=name
        if len(curGroup) < 50:
            break

    return playlists


def userConnect():
    cache_handler, auth_manager = authorization()
    
    return spotipy.Spotify(auth_manager=auth_manager)

def authorization():

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    return cache_handler, auth_manager


web.run(app, threaded=True, host="0.0.0.0", port="8080")
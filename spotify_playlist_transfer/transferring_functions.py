import spotipy
from spotipy.oauth2 import SpotifyPKCE
import base64
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
import time

# Enter your client ID and redirect URI here. Must be the same as the one used in the Spotify Developer Dashboard.
CLIENT_ID = ""
REDIRECT_URI = "http://localhost:8080/callback/" # Must have callback URL to redirect to after authentication


# Retry decorator to fix Spotify's API rate limit 
@retry(wait=wait_fixed(30), stop=stop_after_attempt(3))
def add_items_to_playlist(sp, playlist_id, track_uris):
# Add tracks to a playlist 
    sp.playlist_add_items(playlist_id, track_uris)

@retry(wait=wait_fixed(30), stop=stop_after_attempt(3))
def download_from_origin():
    print("Login to Origin account")
    origin_spotify = spotipy.Spotify(auth_manager=SpotifyPKCE(client_id=CLIENT_ID, redirect_uri=REDIRECT_URI, scope="user-library-read"))
    print("\n\nOrigin account:", origin_spotify.me()['display_name'])

    # Download playlists
    print("Downloading playlists...")
    result = origin_spotify.current_user_playlists()  # current user's playlists as a dictionary
    playlists = result['items'] # list of playlists
    while result['next']:  # pages after first
        result = origin_spotify.next(result) # get next page
        playlists.extend(result['items']) # add to list of playlists

    for playlist in playlists: # for each playlist 
        result = origin_spotify.playlist_tracks(playlist['id']) # get tracks of playlist
        playlist_tracks = result['items']   # list of tracks
        while result['next']: # pages after first
            result = origin_spotify.next(result) # get next page
            playlist_tracks.extend(result['items']) # add to list of tracks
        track_list = []
        for track in playlist_tracks:
            track_list.append(track['track']['uri'])
        playlist['track_list'] = track_list

    # Download saved tracks
    print("Downloading saved tracks...") 
    result = origin_spotify.current_user_saved_tracks() # desired user playlist tracks saved as a dictionary
    saved_tracks = result['items'] # list of saved tracks
    while result['next']: # pages after first
        result = origin_spotify.next(result) # get next page
        saved_tracks.extend(result['items']) # add to list of saved tracks
    saved_tracks_list = [saved_track['track']['id'] for saved_track in saved_tracks] # list of saved track IDs

    return (playlists, saved_tracks_list)  # return tuple of playlists and saved tracks

@retry(wait=wait_fixed(30), stop=stop_after_attempt(3)) 
# upload to destination account
def upload_to_destination(playlists_dict_and_saved_tracks_list_tuple): # takes tuple of playlists and saved tracks
    playlists_dict = playlists_dict_and_saved_tracks_list_tuple[0] # get playlists
    saved_tracks_list = playlists_dict_and_saved_tracks_list_tuple[1] # get saved tracks

    print("Login to the Spotify account you want to transfer to")
    destination_spotify = spotipy.Spotify(auth_manager=SpotifyPKCE(client_id=CLIENT_ID, redirect_uri=REDIRECT_URI, scope="playlist-modify-public playlist-modify-private ugc-image-upload user-library-modify"))
    print("\n\nDestination account:", destination_spotify.me()['display_name'])

    # Playlists
    print("Uploading playlists...")
    for playlist in playlists_dict:
        if playlist['track_list']:
            # Create playlist
            new_playlist = destination_spotify.user_playlist_create(destination_spotify.me()['id'], playlist['name'], public=playlist['public'], collaborative=playlist['collaborative'], description=playlist['description'])
            print(f"Created new playlist: {playlist['name']} with ID: {new_playlist['id']}")


            # Set thumbnail
            if playlist['images']:
                thumbnail_b64 = base64.b64encode(requests.get(playlist['images'][0]['url']).content)
                try:
                    destination_spotify.playlist_upload_cover_image(new_playlist['id'], thumbnail_b64)
                    print(f"Thumbnail uploaded for playlist: {playlist['name']}")
                except Exception as e:
                    print(f"Error uploading thumbnail of \"{playlist['name']}\" playlist; skipping... ({str(e)})")

            # Set tracks
            list_49 = song_segmentation(playlist['track_list'])  # Split into chunks to respect API limits
            for chunk in list_49:
                print(f"Adding a chunk of {len(chunk)} tracks to playlist: {playlist['name']}")
                add_items_to_playlist(destination_spotify, new_playlist['id'], chunk)
        else:
            print(f"Playlist \"{playlist['name']}\" has no tracks; skipping...")

    # Saved tracks
    print("Uploading saved tracks...")
    list_49 = song_segmentation(saved_tracks_list)
    for chunk in list_49:
        destination_spotify.current_user_saved_tracks_add(chunk)

# Split list into chunks of 49 to respect Spotify API limits
def song_segmentation(list):
    return [list[i:i + 49] for i in range(0, len(list), 49)]
# Tranfer Spotify Playlists Between Two Spotify Users

CURRENT WORKING AS 2024: This program transfers all of a Spotify users playlists and saved tracks to another Spotify users account

REQUIRES DEVELOPER MODE ON SPOTIFY ACCOUNT (AND THE CLIENT ID)

## How to run code

1. Run `pip install spotify_playlist_transfer`
2. Set your client ID as an environment variable in transferring_functions.py: `CLIENT_ID = <your client ID>` 
3. Login into the Spotify account of the playlists you want to transfer.
4. The program will copy the playlists and then log out of the account.
5. Login into the Spotify account which you want to move the playlists to.

## How to get a client id

1. Go to Spotify's Developer Dashboard.
2. Create a new application.
3. Set `redirect_uri` in the application setting on the Spotify portal to `http://localhost:8080/callback/`
4. Set both email accounts associated with the playlist transfer to users.



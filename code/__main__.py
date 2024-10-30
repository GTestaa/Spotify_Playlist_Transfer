import sys
from . import transferring_functions
import webbrowser
import time


def main():
	spotify_logout()
	old_account_dl= transferring_functions.download_from_origin()
	spotify_logout()
	transferring_functions.upload_to_destination(old_account_dl)
	print("Playlist Transfer Completed")

def spotify_logout():
	webbrowser.open('accounts.spotify.com/logout')	# logout from old account
	time.sleep(3)

if __name__ == '__main__':
	sys.exit(main())
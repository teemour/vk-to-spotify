# vk-to-spotify
This is a simple utility that works on Python and is made to transfer music from VK to Spotify.

All features working in CLI, so, just follow the lines and all be okay!

Made at the request of my beloved wife, who started using Spotify after its release in our country. :two_hearts:

## Running
Working on Python 3.6+.
Go to the directory with ``vk-to-spotify`` and just run it. 
```bash
python vk-to-spotify.py
```

## How it works?
### Part I: Grabbing from VK
This thing login into VK under the guise of a mobile client and pulls a selected number of tracks from your audios.<br>
This has to be done for the reason that [``VK has closed methods for working with audio in its API``](https://vk.com/dev/audio_api), this is a kind of hack.<br>
After, saves all tracks to JSON in format like **artist — title**. They are now ready to be imported to Spotify.<br>
### Part II: Importing to Spotify
Okay, now we need to grant access, all actions are performed in the CLI. Just follow the lines.<br>
Type your username, than copy redirect-link (if its your first time) to command line and press Enter.<br>
Just specify name of your secret stash with your lovely tracks from VK, he-he, and watch as the utility tries to find them in Spotify.<br>
After completing this process, you can see which tracks were not found and will not be imported.<br>
Now we need to give a name to the playlist to which all tracks will be added, as well as its type, public or private.<br>
Now, just watch the process as it ends, just check your playlists on Spotify. :yum:

## Why do I need this page?
Just to redirect to it and all that. Thanks for your attention.

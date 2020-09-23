# Youtube TMS Finder

![](http://new.tinygrab.com/7020c0e8b010392da4053fa90ab8e0c8419bded864.png)

## What you need to know

This code makes it possible to search youtube channels for songs without having to manually check the videos. This is done by crawling their youtube channel, downloading a video if it is under 4 minutes long, fingerprinting the audio, and checking it against a database (the database which is included in this program). It was developed for Windows so people don't have to install Virtual machines or WSL subsystems or anything like that, and also because my university administrator doesn't allow changing operating systems.


## Credits to:
The makers of youtube-dl
Itspoma, the creator of the audio fingerprinting and recognition code.

## How to set up 

1. Download the youtube-dl folder from https://drive.google.com/drive/folders/1kw1Wk-YJmki5malOPy1WIxS_dWkRqJeE?usp=sharing (These files could not be uploaded to the github page since they're too big.)
1. Move the just downloaded youtube-dl folder into the YT-TMS-Finder folder.
1. Open a command prompt and install the requirements:
```
> pip install -r requirements.txt
```

![](http://new.tinygrab.com/7020c0e8b0393eec4a18c62170458c029577d378c2.png)

## How to
- Check a youtube channel

  ```
  > python find_stable.py
  ```
- Can I add my own songs to the database?

  Yes, itspoma made this possible. Just upload that mp3 file into the "mp3s" folder. Now do `python collect-fingerprints-of-songs.py`. Any song in the 'mp3s' folder that was previously added already will be skipped. The song is now added into the database and can be recognised. For more info please check out: https://github.com/itspoma/audio-fingerprint-identifying-python
  


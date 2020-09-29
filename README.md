# Youtube TMS Finder

![](http://new.tinygrab.com/7020c0e8b010392da4053fa90ab8e0c8419bded864.png)

## What you need to know

This code was made in an effort to make it easier to find the song that has been dubbed as 'the most mysterious song on the internet' and it makes it possible to search youtube channels for songs without having to manually check the videos. This is done by crawling their youtube channel, downloading a video if it is under 4 minutes long, fingerprinting the audio, and checking it against a database (the database which is included in this program). It was developed for Windows so people don't have to install Virtual machines or WSL subsystems or anything like that, and also because my university administrator doesn't allow changing operating systems.

The necessary code was already available, I just made them work together.

## Credits:
- Credit to the makers of youtube-dl
- Special thanks and credit to Itspoma, the creator of the audio fingerprinting and recognition code.

## How to set up (please read)

1. Make sure you have python 3 installed.
1. Open a command prompt and install the requirements:
```
> pip install -r requirements.txt
```
3. Now run
```
> python find_stable.py
```
4. Check for any matches! This will be displayed and a file called "MATCHES.txt" will be created so you don't have to check the progress constantly.

If the program doesn't work right away you probably don't have ffmpeg installed, so please check the problems section of this README and especially the part about ffmpeg not being installed where I explain how to install it with one simple command.

If the program still doesn't work right away, use this:
5. Download the youtube-dl folder from [this google drive](https://drive.google.com/drive/folders/1kw1Wk-YJmki5malOPy1WIxS_dWkRqJeE?usp=sharing) (These files could not be uploaded to the github page since they're too big.)
6. Move the just downloaded youtube-dl folder into the YT-TMS-Finder folder.

## Note

- In case you do ```> python reset-database.py```, simply do ```python collect-fingerprints-from-songs.py```.

## Updates

### V1.0.1
- Option to ignore previously tried videos. This is useful in case the process unexpectedly ends and you want to continue where you left off.
- Speedmode available in v1.0.2

## Example

```bat
Ben-0-mad> python find_stable.py
Welcome to


$$$$$$$$\ $$\      $$\  $$$$$$\         $$$$$$\  $$\                 $$\
\__$$  __|$$$\    $$$ |$$  __$$\       $$  __$$\ \__|                $$ |
   $$ |   $$$$\  $$$$ |$$ /  \__|      $$ /  \__|$$\ $$$$$$$\   $$$$$$$ | $$$$$$\   $$$$$$\
   $$ |   $$\$$\$$ $$ |\$$$$$$\        $$$$\     $$ |$$  __$$\ $$  __$$ |$$  __$$\ $$  __$$\
   $$ |   $$ \$$$  $$ | \____$$\       $$  _|    $$ |$$ |  $$ |$$ /  $$ |$$$$$$$$ |$$ |  \__|
   $$ |   $$ |\$  /$$ |$$\   $$ |      $$ |      $$ |$$ |  $$ |$$ |  $$ |$$   ____|$$ |
   $$ |   $$ | \_/ $$ |\$$$$$$  |      $$ |      $$ |$$ |  $$ |\$$$$$$$ |\$$$$$$$\ $$ |
   \__|   \__|     \__| \______/       \__|      \__|\__|  \__| \_______| \_______|\__|


example url:  https://www.youtube.com/channel/UCmSynKP6bHIlBqzBDpCeQPA/videos


Please enter the channel url: https://www.youtube.com/channel/UCmSynKP6bHIlBqzBDpCeQPA/videos
sqlite - connection opened

DevTools listening on ws://127.0.0.1:36749/devtools/browser/c974ddad-0534-4ee7-9f82-50c47379fae2

Song with id n2i-22aBC3E is less than 4 minutes! (0:07)
Downloading mp3...
This is Michael HD.mp3 downloaded, now performing fingerprint match scan. Please wait...
mp3 deleted.

Song with id Id75WC1yWXg is less than 4 minutes! (2:57)
Downloading mp3...
Cursed Images with The Most Mysterious Song on the Internet playing.mp3 downloaded, now performing fingerprint match scan. Please wait...
POSSIBLE MATCH FOUND!
mp3 deleted.

[[ output trunacted ]]

Song with id MHuVePv1Pxo is less than 4 minutes! (0:26)
Downloading mp3...
PaRappa's silly fun family friendly adventures of happiness - Episode 1.mp3 downloaded, now performing fingerprint match scan. Please wait...
mp3 deleted.
sqlite - connection has been closed
```

## Any problems might arise due to
1. Python not being recognised as internal command. FIX by adding python interpreter folder to the PATH variable)
1. ffmpeg not being installed. FIX by opening powershell in administrator mode, then in this shell do 
```@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command " [System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin" ``` and then ```choco install -y ffmpeg``` afterwards. You can check that ffmpeg is installed by doing ```choco search ffmpeg```.

1. Sqlite3 is not an installed module in python 3. FIX by opening a command prompt and doing `pip install sqlite3`

## FAQ
- How to check a youtube channel?

  ```
  > python find_stable.py
  ```
- Can I add my own songs to the database?

  Yes, itspoma made this possible. Just upload that mp3 file into the "mp3" folder. Now do `python collect-fingerprints-of-songs.py`. Any song in the 'mp3' folder that was previously added already will be skipped. The song is now added into the database and can be recognised. For more info please check out [itspoma's repo](https://github.com/itspoma/audio-fingerprint-identifying-python)
 
- Is it fast?
  At the moment it ins't. I have an idea in mind of how to fix this but I'm testing it at the moment.
  
- Is it storage efficient?
  After installing the necessary modules, yes, very.

- How does it work in detail?
  First we have to get all the video ID's from a youtube channel. This is not possbile by simply using requests or beautifulsoup. We would have to open the browser ourselves going down all the way to the bottom of the page, but we can also do this with webbot so we don't have to do it. Then it downloads the HTML source. From this HTML file we can obtain all the video ID's and their time length without the need of the YouTube API (which costs money). For every video the following is done:
  1. If the video length is less than 4 minutes, download the audio from the video in mp3 format using youtube-dl.
  2. Fingerprint the song.
  3. Match the fingerprint against the database.
  4. If there are more than 100 hashes that match, print this on the screen and add it to a "MATCHES.txt" file.

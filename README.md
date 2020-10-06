# Youtube TMS Finder

To find unidentified music.

![](https://i.ibb.co/w7zGH3d/intro-image2.png)

## What you need to know

This code was made in an effort to make it easier to find the song that has been dubbed as 'the most mysterious song on the internet' and it makes it possible to search youtube channels for songs without having to manually check the videos. This is done by crawling their youtube channel, downloading a video if it is under 4 minutes long, fingerprinting the audio, and checking it against a database (the database which is included in this program). It was developed for Windows so people don't have to install Virtual machines or WSL subsystems or anything like that, and also because my university administrator doesn't allow changing operating systems. But it should work on linux as well.

The necessary code was already available, I just made them work together.

## Credits:
- Credit to the makers of youtube-dl
- Special thanks and credit to Itspoma, the creator of the audio fingerprinting and recognition code.
- Thanks to nrsyed for helping with code optimisation.

## How to use
usage: ```find_stable.py [-h] [-i] [-s] [-v] [-t THRESHOLD] [-c CHANNEL_URL] [-id ID] [-r RESTORE_FILE]```
1. ```-c``` to supply channel URL from command line, if this is not supplied, it will be asked automatically.
1. ```-i``` ignore videos that were checked in another session already.
1. ```-m``` multithreading, max number of videos to check at the same time, 3 is optimal
1. ```-s``` download only first 30 seconds of video. This speeds up the download and fingerprinting.
1. ```-v``` for verbosity.
1. ```-r``` for restore file (This restore file has to be the html source of a youtube channel)
1. ```-id``` to check only one video ID
1. ```-t``` to set the hash matches threshold (at which you will be notified of a match)
1. ```-h``` for the help message.

## How to set up on Windows

1. Make sure you have python 3 installed.
1. Open a command prompt and install the requirements:
```
> pip install -r requirements.txt
```
3. Do you have problems installing PyAudio? Please skip to the next step.

4. To make the installation easier, we'll use chocolately which is just like brew, pip, or other module utilities. Open up CMD in the administrator mode and do this command:
```@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command " [System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin" ```

![](https://i.ibb.co/dmN3DvV/chocho-install.png)

5. Great now you have Chocolately installed. Next we'll install the chromedriver. If you already have the chromedriver you can skip this step. Close the previous CMD window and open a new CMD in administrator mode, run:
``` choco install chromedriver  ```

6. In order to download audio from YouTube we'll need ffmpeg. We'll download this now. If you already have ffmpeg you can skip this step. In the same CMD window, run:
``` choco install ffmpeg -y```

7. If you had any problems with installing PyAudio, that's a common issue. The solution to downloading PyAudio if the normal ```pip install pyaudio``` fails, is this:
Go to https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio and download the .whl file for your version of python.
Then open up a command prompt (press Windows key and type CMD). Navigate to the folder with the .whl file and do ```pip install PyAudio-0.2.11-cp37-cp37m-win_amd64.whl``` or whatever .whl file suits your version of python. Now you have it installed.

8. Now run
```
> python find_stable.py
```

9. Check for any matches! This will be displayed and a file called "MATCHES.txt" will be created so you don't have to check the progress constantly.


## How to set up on Linux

1. Make sure you have python 3 installed.
1. Open a terminal and install the requirements:
```
$ pip install -r requirements.txt
```
3. Do you have problems installing PyAudio? Please skip to the next step.

4. Installing ffmpeg:
```
sudo apt install software-properties-common
sudo apt update
sudo add-apt-repository ppa:jonathonf/ffmpeg-4
sudo apt install ffmpeg
```

5. In case you have any problems with installing PyAudio, please check out [this](https://stackoverflow.com/questions/20023131/cannot-install-pyaudio-gcc-error)

6. To install the chromedriver on linux: please go see [here](https://makandracards.com/makandra/29465-install-chromedriver-on-linux)

7. ```$ python find_stable.py```


## Note

- In case you do ```> python reset-database.py```, simply do ```python collect-fingerprints-from-songs.py```.
- verbosity update and speedmode update coming soon.

## Updates

### V1.0.4-beta
- Added multithreading

### V1.0.4-alpha.1/2
- Made it easier for the user to get the chromedriver.exe for selenium right
- Added -r option for restore file (html source of a youtube channel)
- Added -id option to check only one video
- Added -t option to select the hash matches threshold yourself, default is 20.
- Colorama RecursionError was fixed.

### V1.0.4-alpha
- Code optimisation

### V1.0.3
- Speedmode: use ```-s``` (it uses only the first 30 seconds of a video to do the audio recognition on)
- Verbosity: use ```-v``` (recommended)
- Now tells you how far the progress is.
- Bug fixes.


### V1.0.2
- Channel url can now also be given as command line argument (supply ```-c CHANNEL_URL```)

### V1.0.1
- Option to ignore previously tried videos. This is useful in case the process unexpectedly ends and you want to continue where you left off.
- Speedmode available in v1.0.3

### V1.0.1-alpha.1
- Bug fix

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

1. Problem with Selenium and chromedriver. For Windows please do step 3 and 4 of the setup!

1. Problem with ffmpeg.

## FAQ
- How to check a youtube channel?

  ```
  > python find_stable.py
  ```
- Can I add my own songs to the database?

  Yes, itspoma made this possible. Just upload that mp3 file into the "mp3" folder. Now do `python collect-fingerprints-of-songs.py`. Any song in the 'mp3' folder that was previously added already will be skipped. The song is now added into the database and can be recognised. For more info please check out [itspoma's repo](https://github.com/itspoma/audio-fingerprint-identifying-python).
  
  Note: ALWAYS MAKE SURE THAT THE AUDIO YOU PUT IN THE mp3 FOLDER ARE DOWNLOADED FROM YOUTUBE. This has to do with how Youtube processes audio. If you download something from youtube and compare it to something downloaded from youtube, you are likely not to miss that there is a match. If the audio you put in the database is not download from youtube, you might see that the bot does not find a match. I know this is very strange but unfortunately I have no idea why this happens.
  
- Is it storage efficient?
  After installing the necessary modules, yes.

- What is the optimal number of threads?
  After doing a couple of quick tests, I got these results:
  
  * \# of threads = 1: 12 videos took 98.53 seconds
  * \# of threads = 2: 12 videos took 57.15 seconds
  * \# of threads = 3: 12 videos took 50.21 seconds
  * \# of threads = 4: 12 videos took 51.58 seconds
  * \# of threads = 5: 12 videos took 55.09 seconds
  
  Therefore it seems like 3 threads is a good option. And after doing some tests with a larger number of videos, I got these results:
  [To be finished]

- How does it work in detail?
  First we have to get all the video ID's from a youtube channel. This is not possbile by simply using requests or beautifulsoup. We would have to open the browser ourselves going down all the way to the bottom of the page, but we can also do this with webbot so we don't have to do it. Then it downloads the HTML source. From this HTML file we can obtain all the video ID's and their time length without the need of the YouTube API (which costs money). For every video the following is done:
  1. If the video length is less than 4 minutes, download the audio from the video in mp3 format using youtube-dl.
  2. Fingerprint the song.
  3. Match the fingerprint against the database.
  4. If there are more than 100 hashes that match, print this on the screen and add it to a "MATCHES.txt" file.

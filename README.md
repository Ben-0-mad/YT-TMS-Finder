# YouTube TMS Finder

To find unidentified music on YouTube.

![](https://i.ibb.co/jWpv8rN/Windows-Terminal-d-TKLealgu-T.png)

## What you need to know

This code was made in an effort to make it easier to find the song that has been dubbed 'The Most Mysterious Song on the Internet' as well as other unknown songs. This tool makes it possible to search YouTube channels for songs without having to manually check the videos. 

This is done by crawling the YouTube channel, downloading a video if it is under 4 minutes long, fingerprinting the audio, and checking it against a database (which is included in this program). It was developed for Windows so people don't have to install virtual machines or WSL subsystems or anything like that, and also because my university administrator doesn't allow changing operating systems. But it should work on Linux as well.

The necessary code was already available, I just made them work together.

## Credits & contributors:
- Credit to the makers of youtube-dl
- Special thanks and credit to Itspoma, the creator of the audio fingerprinting and recognition code.
- Thanks to nrsyed for helping with code optimisation.
- Thanks to Tamago-iku for contributing.

## How to use
Usage: 
```
find_stable.py [-h] [-i] [-s] [-v] [-t THRESHOLD] [-m THREADS] [-c CHANNEL_URL] [-id ID] [-r RESTORE_FILE]
```
1. ```-h``` for the help message.
1. ```-i``` ignore videos that were checked in another session already.
1. ```-s``` download only first 30 seconds of video. This speeds up the download and fingerprinting.
1. ```-v``` for verbosity.
1. ```-t``` to set the hash matches threshold (at which you will be notified of a match)
1. ```-m``` multithreading, max number of videos to check at the same time, 3 is optimal
1. ```-c``` to supply channel URL from command line, if this is not supplied, it will be asked automatically.
1. ```-id``` to check only one video ID
1. ```-r``` for restore file (This restore file has to be the html source of a youtube channel)
1. ```-mnd``` set the min duration of videos that you want to check
1. ```-mxd``` set the max duration of videos that you want to check 

**The restore file is automatically created after the first time you grab the HTML of a YouTube channel.**

Some unidentified music we find is different in BPM/pitch, therefore [this package](https://www.dropbox.com/s/ze3nzu8lecy6ndl/TMS%20subtle%20variants%20on%20tone%20and%20speed.zip?dl=0) with slightly different versions of TMS is available. Just put the files in the "mp3" folder and do ```python collect-fingerprints-of-songs.py```.

## How to set up on Windows

1. Make sure you have Python 3 installed.
1. Open a command prompt and install the requirements:
```
> pip install -r requirements.txt
```
3. If you have problems installing PyAudio, skip to the next step.

4. To make the installation easier, we'll use chocolately which is just like brew, pip, or other module utilities. Open up CMD in the administrator mode and do this command:
```
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command " [System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin" 
```

5. Great! Now you have Chocolately installed. Next we'll install the chromedriver. If you already have the chromedriver you can skip this step. Close the previous CMD window and open a new CMD in administrator mode, then run:
``` 
> choco install chromedriver  
```

6. In order to download audio from YouTube we'll need ffmpeg. We'll download this as well. If you already have ffmpeg you can skip this step. In the same CMD window, run:
``` 
> choco install ffmpeg -y
```

7. If you had any problems with installing PyAudio, that's a common issue. The solution to downloading PyAudio if the normal ```pip install pyaudio``` fails, is this:
- Go to https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio and download the .whl file for your version of python.
Then open up a command prompt (press Windows key and type CMD). Navigate to the folder with the .whl file and do ```pip install PyAudio-0.2.11-cp37-cp37m-win_amd64.whl``` or whatever .whl file suits your version of python. Now you have it installed.

8. Now do: ```python find_stable.py```

9. Check for any matches! This will be displayed and a file called "MATCHES.txt" will be created in the folder so you don't have to check the progress constantly. If any videos get missed, they'll be logged in "misses.txt" as well.


## How to set up on Linux

1. Make sure you have Python 3 installed.
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

6. To install the chromedriver on Linux: please go see [here](https://makandracards.com/makandra/29465-install-chromedriver-on-linux)

7. Then do: ```python find_stable.py```


## Note

- In case you do ```python reset-database.py```, simply do ```python collect-fingerprints-from-songs.py```.
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

## Example output

```
C:\Users\username> python find_stable.py
Welcome to...

__   _______   ________  ___ _____  ______ _           _
\ \ / /_   _| |_   _|  \/  |/  ___| |  ___(_)         | |
 \ V /  | |     | | | .  . |\ `--.  | |_   _ _ __   __| | ___ _ __
  \ /   | |     | | | |\/| | `--. \ |  _| | | '_ \ / _` |/ _ \ '__|
  | |   | |     | | | |  | |/\__/ / | |   | | | | | (_| |  __/ |
  \_/   \_/     \_/ \_|  |_/\____/  \_|   |_|_| |_|\__,_|\___|_|


Enter a channel URL to begin.
Example URL:  https://www.youtube.com/channel/UCmSynKP6bHIlBqzBDpCeQPA/videos

DevTools listening on ws://127.0.0.1:36749/devtools/browser/c974ddad-0534-4ee7-9f82-50c47379fae2

Downloading audio from video with ID lI0kLA-7J5Q...
Audio downloaded! Performing fingerprint match scan...
Confidence of a match: 8.
1.92% done

Downloading audio from video with ID RpnhkS_Stfs...
Audio downloaded! Performing fingerprint match scan...
Confidence of a match: 12.
3.85% done

Downloading audio from video with ID -JRSeiogFbA...
Audio downloaded! Performing fingerprint match scan...
Confidence of a match: 8.
5.77% done
```

## Common problems
1. Python is not being recognised as an internal command. FIX by adding Python interpreter folder to the PATH variable.

1. Problem with Selenium and chromedriver. For Windows please do step 3 and 4 of the setup!

1. Problem with ffmpeg. Install ffmpeg in step 6.

## Contributing

If you'd like to contribute, these are the things that still need to be done:
- Use youtube-dl python module instead of actual youtube-dl.exe file. This allows us to remove the youtube-dl folder in this repo.
- Make script compatible with youtube-data API (and make this option optional), so you don't have to open the channel URL in a browser to grab the HTML and then obtain the videos.
- Include timestamps in MATCHES.txt (DONE)
- Add max_duration argument for the argparser
- Finish FAQ section in this readme
- Create and test setup file for Windows and Linux to make installation quicker.

## FAQ
- **How to check a YouTube channel?**

  ```
  > python find_stable.py -c CHANNEL_ID
  ```
- **Can I add my own songs to the database?**

  Yes, itspoma made this possible. Just upload that mp3 file into the "mp3" folder. Now do `python collect-fingerprints-of-songs.py`. Any song in the 'mp3' folder that was previously added already will be skipped. The song is now added into the database and can be recognised. For more info please check out [itspoma's repo](https://github.com/itspoma/audio-fingerprint-identifying-python).
  
  Note: **Make sure that the audio you're adding to the database was downloaded from YouTube!** This has to do with how YouTube processes audio. If you download something from YouTube and compare it to something downloaded from YouTube, you are likely not to miss a match. If the audio you put in the database is not download from YouTube, you might see that the bot does not find a match. I know this is very strange but unfortunately I have no idea why this happens.
  
- **Is it storage efficient?**
  
  After installing the necessary modules, yes. The bot automatically deletes mp3 files after they have been checked against the database.

- **What is the optimal number of threads?**
  
  After doing a couple of quick tests, I got these results:
  
  * \# of threads = 1: 12 videos took 98.53 seconds
  * \# of threads = 2: 12 videos took 57.15 seconds
  * \# of threads = 3: 12 videos took 50.21 seconds
  * \# of threads = 4: 12 videos took 51.58 seconds
  * \# of threads = 5: 12 videos took 55.09 seconds
  
  Therefore it seems like 3 threads is a good option. And after doing some tests with a larger number of videos, I got these results:
  [To be finished]

- **How does it work in detail?**
  
  First we have to get all the video IDs from a YouTube channel. This is not possbile by simply using requests or beautifulsoup. We would have to open the browser ourselves going down all the way to the bottom of the page, but we can also do this with a webbot so we don't have to do it ourselves. 
  
  Then it downloads the HTML source. From this HTML file we can obtain all the video IDs and their time length without the need of the YouTube API (which costs money). For every video the following is done:
  1. If the video length is less than 4 minutes, download the audio from the video in mp3 format using youtube-dl.
  2. Fingerprint the song.
  3. Match the fingerprint against the database.
  4. If there are more than 100 hashes that match, print this on the screen and add it to a "MATCHES.txt" file.

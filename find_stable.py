import argparse                         #for getting command line arguments
import math
import os                               #for various things
import re
import subprocess                       #calling other script or executables from this file
import sys
from time import sleep                  #to prevent errors

import bs4 as bs                        #for working with html source file
from selenium import webdriver
from termcolor import colored           #for getting colored text

from libs.utils import align_matches
from libs.db_sqlite import SqliteDatabase #for working with the SQL database
from recognize_from_file import run_recognition

class Finder:
    def __init__(self, channel_url, ignore_checked=False):
        # This regex captures all valid forms the channel URL might take
        # and excludes any additional path identifiers/parameters.
        # See https://support.google.com/youtube/answer/6180214?hl=en
        expr = r"^.*(/c(hannel)?/[a-zA-Z0-9-_]+)"
        channel_path_match = re.match(expr, channel_url)

        if not channel_path_match.groups():
            raise ValueError("Malformed URL")

        channel_path = channel_path_match.groups()[0]
        self.channel_url = "https://www.youtube.com" + channel_path + "/videos"

        self.sql = SqliteDatabase()
        self.ignore_checked = ignore_checked
        self.file_recogniser_path = os.path.join(os.getcwd(), "recognize-from-file.py")
    
    def get_song_mp3(self, id_: str) -> None:
        """
        Downloads the audio from a youtube video in mp3 format given a video id.
        """
        #print("Downloading mp3...")
        url = "https://www.youtube.com/watch?v=" + id_
        dir_here = os.path.abspath(os.getcwd())
        dir_youtube_dl_dir = os.path.join(dir_here, "youtube-dl")

        # TODO: This should be a method argument or a class/instance variable.
        if sys.platform == "win32":
            youtube_dl_exec = "youtube-dl.exe"
        else:
            youtube_dl_exec = "youtube-dl"

        path_youtube_dl_exec = os.path.join(dir_youtube_dl_dir, youtube_dl_exec)
        dir_mp3s = os.path.join(dir_here, "downloaded_mp3s")
        
        # '%(title)s.%(ext)s' comes from how youtube-dl.exe outputs files with
        # filename as youtube title
        destination_arg = os.path.join(dir_mp3s, "%(title)s.%(ext)s")

        # TODO: This should be done before this method is called.
        if not os.path.isdir(dir_mp3s):
            os.mkdir(dir_mp3s)

        # Download the mp3 file from youtube
        cmd = [
            f"{path_youtube_dl_exec}", "-x", "--audio-format", "mp3",
            "--no-warnings", "-o", f"{destination_arg}", f"{url}"
        ]
        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # Convert stdout to UTF-8 string from bytes.
        # TODO: test Windows compatibility?
        stdout = proc.stdout.decode("utf-8")
        expr = r"\[ffmpeg\] Destination: (.*\.mp3).*"
        match = re.search(expr, stdout)

        if proc.stderr or not match:
            return None

        song_fpath = match.groups()[0]
        return song_fpath
        
    def delete_mp3s(self):
        """
        Deletes all mp3s in the mp3s folder.
        """
        current_directory = os.getcwd()
        for file in os.listdir("downloaded_mp3s"):
            full_path = os.path.join(current_directory, "downloaded_mp3s", file)
            os.remove(full_path)
    
    def get_channel_source(self):
        driver = webdriver.Chrome()
        driver.get(self.channel_url)
        sleep(2)
        source = driver.page_source

        scroll_by = 5000
        driver.execute_script(f"window.scrollBy(0, {scroll_by});")
        while driver.page_source != source:
            source = driver.page_source
            driver.execute_script(f"window.scrollBy(0, {scroll_by});")
            sleep(0.5)
        driver.quit()
        return source
        
    def check_file(self, fpath, thresh=100):
        matches = run_recognition(fpath)
        song = align_matches(self.sql, matches)
        return song["CONFIDENCE"] >= thresh
            
    def get_videos(self, source):
        """
        Extract video ids and durations from channel video page source.
        """
        # Get video ids.
        watch_expr = r'href="/watch\?v=([a-zA-Z0-9_-]+)"'
        matches = re.finditer(watch_expr, source)

        # Each video id has two matching instances, so skip every other to
        # ensure uniqueness.
        video_ids = [match.groups()[0] for match in matches][::2]
        
        # Get duration of video corresponding to each video id.
        soup = bs.BeautifulSoup(source, "html.parser")
        
        # all time durations are contained within a tag with class
        # "style-scope ytd-thumbnail-overlay-time-status-renderer"
        time_spans = soup.findAll(
            "span",
            {"class": "style-scope ytd-thumbnail-overlay-time-status-renderer"}
        )
        
        #Gets a list with the time durations stripped from any trailing spaces
        raw_durations = [time_span.text.strip() for time_span in time_spans]

        # Construct a list of video durations in seconds.
        durations = []
        for raw_duration in raw_durations:
            time_units = raw_duration.split(":")
            seconds = int(time_units[-1])
            minutes = int(time_units[-2])
            hours = int(time_units[-3]) if len(time_units) > 2 else 0

            # Get total duration in seconds.
            duration = seconds + (minutes * 60) + (hours * 3600)
            durations.append(duration)

        # Construct and return a list of videos, where each video is a dict
        # containing the video id and video duration in seconds.
        videos = []
        for (video_id, duration) in zip(video_ids, durations):
            videos.append(
                {
                    "id": video_id,
                    "duration": duration
                }
            )
        return videos

    def check_channel(self, max_duration=math.inf):
        source = self.get_channel_source()
        videos = self.get_videos(source)

        for video in videos:
            id_ = video["id"]
            if (
                (not self.ignore_checked or not self.sql.in_checked_ids(id_))
                and video["duration"] < max_duration
            ):
                song_fpath = self.get_song_mp3(id_)
                possible_match = self.check_file(song_fpath)
                if possible_match:
                    song_fname = os.path.split(song_fpath)[1]
                    with open("MATCHES.txt", "a") as f:
                        f.write(f"{id_} {song_fname}")
                self.sql.add_checked_id(id_)
        self.delete_mp3s()
        

def get_arguments():
    parser = argparse.ArgumentParser(description="TMS-Finder")
    parser.add_argument("channel_url", type=str, help="Channel URL")
    parser.add_argument(
        "-i", "--ignore", dest="ignore", help="Ignore already checked videos",
        action="store_true"
    )
    parser.add_argument(
        "-s", "--speedmode", dest="speedmode", help="Activate speed mode",
        action="store_true"
    )
    return parser.parse_args()


if __name__ == '__main__':
    header = """
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
    """
    #print(header)
    args = get_arguments()

    if not os.path.isdir("downloaded_mp3s"):
        os.mkdir("downloaded_mp3s")

    # TODO: windows/Linux colors?
    #os.system("color 07")

    finder = Finder(args.channel_url, ignore_checked=args.ignore)
    finder.check_channel()

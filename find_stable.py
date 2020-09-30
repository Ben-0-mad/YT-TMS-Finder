import argparse                         #for getting command line arguments
import os                               #for various things
from selenium import webdriver          #for getting html source of channel
from time import sleep                  #to prevent errors
import re                       
import bs4 as bs                        #for working with html source file
import subprocess                       #calling other script or executables from this file
import sys
from termcolor import *           #for getting colored text
import colorama

from libs.db_sqlite import SqliteDatabase #for working with the SQL database
from recognize_from_file import run_recognition
from libs.utils import align_matches
import math

print("""
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
""")



class Finder:
    def __init__(self, channel_url, ignore_checked):
        ### Check if the channel url is in right format
        expr = r"^.*(/c(hannel)?/[a-zA-Z0-9-_]+)"
        channel_path_match = re.match(expr, channel_url)
        
        if channel_path_match is None:
            raise ValueError("Malformed URL, please give a valid URL.")
            
        channel_path = channel_path_match.groups()[0]
        self.channel_url = "https://www.youtube.com" + channel_path + "/videos"
        
        ### For using sql to interact with db file (the database)
        self.sql = SqliteDatabase()
        self.ignore_checked = ignore_checked
        self.channel_url = channel_url.replace('featured','videos')
        self.file_recogniser_path = os.path.join(os.getcwd(), "recognize-from-file.py")
        
    
    def get_song_mp3(self, id: str) -> None:
        """
        Downloads the audio from a youtube video in mp3 format given a video id.
        """
        
        ### Delete existing mp3 files in downloaded_mp3s directory in case there is one left of a previous run
        self.delete_mp3s()
        print("")
        print("Downloading mp3...")
        url = "https://youtube.com/watch?v=" + id
        
        dir_here = os.path.abspath(os.getcwd())
        dir_youtube_dl_dir = os.path.join(dir_here, "youtube-dl")
        
        ### Set youtube-dl exectuable for windows and linux users
        if sys.platform == "win32":
            youtube_dl_exec = "youtube-dl.exe"
        else:
            youtube_dl_exec = "youtube-dl"
            
        path_youtube_dl_exec = os.path.join(dir_youtube_dl_dir, youtube_dl_exec)
        
        
        dir_downloaded_mp3s = os.path.join(dir_here, "downloaded_mp3s")
    
        ### '%(title)s.%(ext)s' comes from how youtube-dl.exe outputs files with 
        ### filename as youtube title
        destination_arg = os.path.join(dir_downloaded_mp3s, "%(title)s.%(ext)s")
        
        ### Make the mp3 folder which will contain a downloaded mp3
        if not os.path.isdir(dir_downloaded_mp3s):
            os.mkdir(dir_downloaded_mp3s)
        
        cmd = [
            f"{path_youtube_dl_exec}", "-x", "--audio-format", "mp3",
            "--no-warnings", "-o", f"{destination_arg}", f"{url}"
        ]
        try:
            proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            sleep(0.1)
            self.songname = os.listdir("downloaded_mp3s")[0]
            print(f"{os.listdir('downloaded_mp3s')[0]} downloaded, now performing fingerprint match scan. Please wait...")
        except:
            cprint("Youtube audio couldn't be downloaded. Skipping for now.", "red")
        

        # Convert stdout to UTF-8 string from bytes.
        # TODO: test Windows compatibility?
        stdout = proc.stdout.decode("utf-8")
        expr = r"\[ffmpeg\] Destination: (.*\.mp3).*"
        match = re.search(expr, stdout)

        if proc.stderr or not match:
            return None

        song_fpath = match.groups()[0]
        return song_fpath
        
    def get_song_mp3_speedmode(self, id):
        """
        Downloads the audio from a youtube video in mp3 format given a video id.
        """
        self.delete_mp3s()
        print("Downloading mp3...")
        url = "https://youtube.com/watch?v=" + id
        dir_here = os.path.abspath(os.getcwd())
        dir_youtube_dl_dir = os.path.join(dir_here, "youtube-dl")
        path_youtube_dl_exec = os.path.join(dir_youtube_dl_dir, "youtube-dl.exe")
        dir_mp3s = os.path.join(dir_here, "downloaded_mp3s")
        
        
        streams = subprocess.check_output(f"{path_youtube_dl_exec} -g https://www.youtube.com/watch?v={id}").decode()
        try:
            audio_stream = streams.split("\n")[1]
            if not os.path.isdir(dir_mp3s):
                os.mkdir(dir_mp3s)
            _ = subprocess.check_output(f"ffmpeg -hide_banner -loglevel warning -i \"{audio_stream.strip()}\" -t 00:00:30.00 -c copy downloaded_mp3s\out.mp4")
            sleep(0.1)
            _ = subprocess.check_output(f"ffmpeg -hide_banner -loglevel warning -i downloaded_mp3s\out.mp4 downloaded_mp3s\out.mp3")
            sleep(0.1)
            self.songname = os.listdir("downloaded_mp3s")[0]
            os.remove("downloaded_mp3s\out.mp4")
        except IndexError:
            cprint("Video streams could not be obtained. Skipping for now.", "red")
        
    def delete_mp3s(self):
        """
        Deletes all mp3s in the mp3s folder.
        """
        current_directory = os.getcwd()
        for file in os.listdir("downloaded_mp3s"):
            full_path = os.path.join(current_directory, "downloaded_mp3s", file)
            os.remove(full_path)
            print("mp3 deleted.")
    
    def get_channel_source(self):
        ### Open a browser
        driver = webdriver.Chrome()
        driver.get(self.channel_url)
        sleep(2)
        source = driver.page_source
        
        ### Keep scrolling until we hit the end of the page
        scroll_by = 5000
        driver.execute_script(f"window.scrollBy(0, {scroll_by});")
        while driver.page_source != source:
            source = driver.page_source
            driver.execute_script(f"window.scrollBy(0, {scroll_by});")
            sleep(0.1)
        driver.quit()
        
        return source
        
    def check_file(self, fpath, thresh=100):
        '''
        Fingerprint and try to match a song against database
        '''
        
        matches = run_recognition(fpath)
        song = align_matches(self.sql, matches)
        return song["CONFIDENCE"] >= thresh
        
        '''
        output = subprocess.check_output(['python', self.file_recogniser_path, os.path.join(os.getcwd(), "downloaded_mp3s", self.songname )])
        if "POSSIBLE MATCH FOUND" in output.decode():
            print(colored("POSSIBLE MATCH FOUND!", "green", attrs=["dark"]))
            with open("MATCHES.txt", "a") as f:
                f.write(f"{self.songname} with YT ID {self.id} has a match with the database!\n")
        '''
            
    def get_videos(self, source):
        """
        Exract video ids and durations from channel video page source
        """
        
        ### get video ids form page source.
        watch_expr = r'href="/watch\?v=([a-zA-Z0-9_-]+)"'
        matches = re.finditer(watch_expr, source)
        
        ### For each video, the id is put twice in the page source, 
        ### so we have to use [::2] to grab only half of the ids
        video_ids = [match.groups()[0] for match in matches][::2]
        
        ### Get duration of video corresponding to each video id.
        soup = bs.BeautifulSoup(source, "html.parser")
        
        ### all time durations are contained within a tag with class
        ### "style-scope ytd-thumbnail-overlay-time-status-renderer"
        time_spans = soup.findAll(
            "span", 
            {"class": "style-scope ytd-thumbnail-overlay-time-status-renderer"}
        )
        
        raw_durations = [ts.text.strip() for ts in time_spans]
        del time_spans
        
        ### Making video durations list
        durations = []
        for raw_duration in raw_durations:
            time_units = raw_duration.split(":")
            seconds = int(time_units[-1])
            minutes = int(time_units[-2])
            hours = int(time_units[-3]) if len(time_units) > 2 else 0

            ### Get total duration in seconds.
            duration = seconds + (minutes * 60) + (hours * 3600)
            durations.append(duration)
            
        # Construct and return a list of videos, where each video is a dict
        # containing the video id and video duration in seconds.
        videos = []
        for (video_id, duration) in zip(video_ids, durations):
            videos.append(
                {
                    "id" : video_id,
                    "duration" : duration
                }
            )
        return videos
        
        
        '''We may need to add also the video titles if we want to include a speedmode but for now this will do.'''
        
    
    def check_channel(self, max_duration=210):
        #Get the HTML source of the channel's video section
        source = self.get_channel_source()
        videos = self.get_videos(source)
        
        for video in videos:
            id_ = video["id"]
            
            '''
            print("")
            print(video["duration"]<= max_duration)
            print(self.ignore_checked)
            print(self.sql.in_checked_ids(id_))
            print((self.ignore_checked == False and video["duration"] <=max_duration) or (video["duration"]<= max_duration and (self.ignore_checked == True and not self.sql.in_checked_ids(id_))))
            '''
            
            ### this seems like complicated logic but it's exactly what we want please 
            ### fill in "(p^~q) or (p ^ (q^ (~r)))" on the website 
            ### https://web.stanford.edu/class/cs103/tools/truth-table-tool/ to see this
            if ((self.ignore_checked == False and video["duration"] <=max_duration) 
            or 
            (video["duration"]<= max_duration and (self.ignore_checked == True and not self.sql.in_checked_ids(id_)))):
                
                song_fpath = self.get_song_mp3(id_)
                try:
                    possible_match = self.check_file(song_fpath)
                    self.sql.add_checked_id(id_)
                except:
                    cprint("Something went wrong, probably a weird youtube title. Skipping for now.", "red")
                
                if possible_match:
                    cprint("Possible match found", "green")
                    
                    song_fname = os.path.split(song_fpath)[1]
                    
                    with open("MATCHES.txt", "a") as f:
                        f.write(f"{id_} {song_fname}")
            self.delete_mp3s()


def get_arguments():
    parser = argparse.ArgumentParser(description='''TMS-Finder''')
    
    parser.add_argument("-i", "--ignore", dest="ignore", default=False, help="Ignore already checked videos", action='store_true')
    parser.add_argument("-s", "--speedmode", dest="speedmode", help="Activate speed mode", action = "store_true")
    parser.add_argument("-v", "--verbose", dest="verbose", help="Give Feedback", action = "store_true")
    parser.add_argument("-c", "--channel", dest="channel_url", help="help")
    
    return parser.parse_args()


if __name__ == '__main__':
    args = get_arguments()
    
    ### Make sure we have this folder
    if not os.path.isdir("downloaded_mp3s"):
        os.mkdir("downloaded_mp3s")
    
    ### Check channel argument
    if args.channel_url is None:
        channel_url = input("\nPlease enter the channel url: ")   #Example input: www.youtube.com/c/GlitchxCity/featured
    else:
        channel_url = str(args.channel_url)
    
    ### initialise colored text
    colorama.init()
    
    finder = Finder(channel_url, args.ignore)
    finder.check_channel()

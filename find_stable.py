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
    def __init__(self, channel_url, arguments):
        ### setting variables
        self.sql = SqliteDatabase()
        
        self.ignore_checked = arguments.ignore
        self.verbose = arguments.verbose
        self.speedmode = arguments.speedmode
        self.vprint(str(arguments), "yellow")
        
        ### Make sure we have this folder
        if not os.path.isdir("downloaded_mp3s"):
            os.mkdir("downloaded_mp3s")
        
        ### Check if the channel url is in right format
        expr_channel = r"^.*(/c(hannel)?/[a-zA-Z0-9-_]+)"
        expr_user    = r"^.*(/u(ser)?/[a-zA-Z0-9-_]+)"
        channel_path_match = re.match(expr_channel, channel_url)
        user_path_match = re.match(expr_user, channel_url)
        
        if channel_path_match is None and user_path_match is None:
            raise ValueError("Malformed URL, please give a valid URL.")
        elif channel_path_match is not None:
            channel_path = channel_path_match.groups()[0]
            self.channel_url = "https://www.youtube.com" + channel_path + "/videos"
        else:
            channel_path = user_path_match.groups()[0]
            self.channel_url = "https://www.youtube.com" + channel_path + "/videos"
        
    
    def vprint(self, text: str, colour:str = "white"):
        """
        Helpful function for printing when verbose is turned on
        """
        if self.verbose:
            cprint(text, colour)
    
    def get_song_mp3(self, id, speed_mode=False):
        """
        Downloads the audio from a youtube video in mp3 format given a video id.
        """
        
        ### Delete existing mp3 files in downloaded_mp3s directory in case there is one left of a previous run
        self.delete_mp3s()
        self.vprint("\nDownloading mp3...")
        url = "https://youtube.com/watch?v=" + id
        
        dir_here = os.path.abspath(os.getcwd())
        dir_youtube_dl_dir = os.path.join(dir_here, "youtube-dl")
        
        ### Set youtube-dl exectuable for windows and linux users
        if sys.platform == "win32":
            youtube_dl_exec = "youtube-dl.exe"
        else:
            youtube_dl_exec = "youtube-dl"
        path_youtube_dl_exec = os.path.join(dir_youtube_dl_dir, youtube_dl_exec)
        
        ### initialise this variable to make the destination argument for the youtube-dl command
        dir_downloaded_mp3s = os.path.join(dir_here, "downloaded_mp3s")
    
        ### '%(title)s.%(ext)s' comes from how youtube-dl.exe outputs files with 
        ### filename as youtube title
        destination_arg = os.path.join(dir_downloaded_mp3s, "%(title)s.%(ext)s")
        
        ### Make the mp3 folder which will contain a downloaded mp3
        if not os.path.isdir(dir_downloaded_mp3s):
            os.mkdir(dir_downloaded_mp3s)
        
        if speed_mode:
            cmd = [
                f"{path_youtube_dl_exec}", "-x",
                "--postprocessor-args", "\"-ss 00:00:00.00 -t 00:00:30.00\"",
                f"{url}", "--audio-format", "mp3", "-o", f"{destination_arg}"
            ]
        else:
            cmd = [
                f"{path_youtube_dl_exec}", "-x", "--audio-format", "mp3",
                "--no-warnings", "-o", f"{destination_arg}", f"{url}"
            ]

        try:
            proc = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            songname = os.listdir("downloaded_mp3s")[0]
            self.vprint(f"{songname} with id {id} downloaded, now performing fingerprint match scan. Please wait...")
        except KeyboardInterrupt:
            ### completely exit program if this is what user wants
            exit()
        except:
            ### always show error even when verbose is off
            cprint("Youtube audio couldn't be downloaded. Skipping for now.", "red")
            ### when return value is None, we go to the next song to check (see code in line 326)
            return None
        

        # Convert stdout to UTF-8 string from bytes.
        # TODO: test Windows compatibility?
        # Greek letters not supported for commented out part!!
        '''
        stdout = proc.stdout.decode("utf-8")
        expr = r"\[ffmpeg\] Destination: (.*\.mp3).*"
        match = re.search(expr, stdout)

        if proc.stderr or not match:
            return None
        
        song_fpath = match.groups()[0]
        
        
        print(f"\n\n{stdout}\n===\n{expr}\n===\n{match}\n===\n{match.groups()}\n\n")
        exit()
        return song_fpath
        '''
        
        ### This does support greek letters even though it may not be the best way to do it.
        return os.path.abspath(os.path.join("downloaded_mp3s", os.listdir("downloaded_mp3s")[0]))
    
    
    def delete_mp3s(self):
        """
        Deletes all mp3s in the mp3s folder.
        """
        current_directory = os.getcwd()
        for file in os.listdir("downloaded_mp3s"):
            full_path = os.path.join(current_directory, "downloaded_mp3s", file)
            os.remove(full_path)
            self.vprint("mp3 deleted.")
    
    
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
        
    def check_file(self, fpath, thresh=40):
        """
        Fingerprint and try to match a song against database
        """
        
        matches = run_recognition(fpath)
        song = align_matches(self.sql, matches)
        return song["CONFIDENCE"] >= thresh
    
        
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
        
        total_videos = len(videos)
        
        for (video, index) in zip(videos, range(total_videos)):
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
                
                ### download the song
                if not self.speedmode:
                    song_fpath = self.get_song_mp3(id_)
                else:
                    song_fpath = self.get_song_mp3_speedmode(id_)
                
                ### we skip this song if something went wrong with the download
                if song_fpath is None:
                    ### Skip to the next video in the for loop
                    continue 
                
                try:
                    possible_match = self.check_file(song_fpath)
                    self.vprint(f"{100*index/total_videos:.2f}% done")
                    self.sql.add_checked_id(id_)
                except IndexError:
                    cprint("Something went wrong, probably a weird youtube title. Skipping for now.", "red")
                    continue
                except KeyboardInterrupt:
                    exit()
                
                if possible_match:
                    self.vprint("Possible match found", "green")
                    
                    song_fname = os.path.split(song_fpath)[1]
                    
                    with open("MATCHES.txt", "a") as f:
                        f.write(f"{song_fname} with YT ID {id_} has a match with the database! Oh my lawd please check it\n")
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
    
    ### Check channel argument
    if args.channel_url is None:
        channel_url = input("\nPlease enter the channel url: ")   #Example input: www.youtube.com/c/GlitchxCity/featured
    else:
        channel_url = str(args.channel_url)
    
    ### initialise colored text
    colorama.init()
    
    finder = Finder(channel_url, args)
    finder.check_channel()

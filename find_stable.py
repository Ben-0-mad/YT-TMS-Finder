import argparse                         #for getting command line arguments
import os                               #for various things
from selenium import webdriver, common  #for getting html source of channel
from time import sleep                  #to prevent errors
import re                       
import bs4 as bs                        #for working with html source file
import subprocess                       #calling other script or executables from this file
import sys
from termcolor import *           #for getting colored text
import colorama
### initialise colored text
colorama.init()

from libs.db_sqlite import SqliteDatabase #for working with the SQL database
from recognize_from_file import run_recognition
from libs.utils import align_matches
import math
import datetime                         # To include time info in the missed.txt file

import threading
import multiprocessing

### for getting script runtime
import time
start_time = time.time()


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
    def __init__(self):        
        ### Verifying needed folders
        if not os.path.isdir("downloaded_mp3s"):
            os.mkdir("downloaded_mp3s")
        
        ### setting variables
        self.arguments = get_arguments()
        self.sql = SqliteDatabase()
        
        assert 3 - [self.arguments.id, self.arguments.restore_file, self.arguments.channel_url].count(None) <= 1 , "Can't have any of id, channel, restore file as combined arguments."
        
        # if there is no url or id, ask for url
        if (self.arguments.id is None and self.arguments.channel_url is None and self.arguments.restore_file is None):
            self.arguments.channel_url = input("\nPlease enter the channel url: ")   #Example input: www.youtube.com/c/GlitchxCity/featured
        
        # if there is a url, verify if it's a correct URL
        if self.arguments.channel_url is not None:
            self.verify_url(self.arguments.channel_url)
        
        
        self.ignore_checked = self.arguments.ignore
        self.verbose = self.arguments.verbose
        self.speedmode = self.arguments.speedmode
        self.vprint(str(self.arguments), "yellow")
        
        ### Make sure that there are not leftovers from previous runs
        self.delete_mp3s()
        
        
    def verify_url(self, url):
        ### Check if the channel url is in right format
        expr_channel = r"^.*(/c(hannel)?/[a-zA-Z0-9-_]+)"
        expr_user    = r"^.*(/u(ser)?/[a-zA-Z0-9-_]+)"
        channel_path_match = re.match(expr_channel, url)
        user_path_match = re.match(expr_user, url)
        
        if channel_path_match is None and user_path_match is None:
            raise ValueError("Malformed URL, please give a valid URL.")
        elif channel_path_match is not None:
            channel_path = channel_path_match.groups()[0]
            self.channel_url = "https://www.youtube.com" + channel_path + "/videos"
        else:
            channel_path = user_path_match.groups()[0]
            self.channel_url = "https://www.youtube.com" + channel_path + "/videos"
        return True
    
    
    def vprint(self, text: str, colour:str = "white"):
        """
        Helpful function for printing when verbose is turned on
        """
        if self.verbose:
            cprint(text, colour)
    
    
    def get_song_mp3(self, id: str) -> str:
        """
        Downloads the audio from a youtube video in mp3 format given a video id.
        """
        
        ### Delete existing mp3 files in downloaded_mp3s directory in case there is one left of a previous run
        #self.delete_mp3s()
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
        #destination_arg = os.path.join(dir_downloaded_mp3s, "%(title)s.%(ext)s")
        destination_arg = os.path.join(dir_downloaded_mp3s, f"{id}.%(ext)s")
        
        ### Make the mp3 folder which will contain a downloaded mp3
        if not os.path.isdir(dir_downloaded_mp3s):
            os.mkdir(dir_downloaded_mp3s)
        
        ### Setting up the command for the different modes
        if not self.speedmode:
            cmd = [
                f"{path_youtube_dl_exec}", "-x", "--audio-format", "mp3", 
                "--no-warnings", "-o", f"{destination_arg}", f"{url}"
                ]
        else:
            cmd = [f"{path_youtube_dl_exec}", "-x", "--postprocessor-args", "\"-ss 00:00:00.00 -t 00:00:15.00\"", f"{url}", "--audio-format", "mp3", "-o", f"{destination_arg}"]
        
        
        ### Speedmode is not supported on Windows because of this way of calling the command. On Windows it does not wait until all the files for the mp3 are merged. Therefore I still need to use subprocess.run to make this work
        
        try:
            subprocess.check_output(' '.join(cmd))
            sleep(0.1)
            self.vprint(f"Video with id {id} downloaded, now performing fingerprint match scan.")
        except KeyboardInterrupt:
            ### completely exit program if this is what user wants
            self.delete_mp3s()
            exit()
        except:
            ### always show error even when verbose is off
            cprint("Youtube audio couldn't be downloaded. Skipping for now.", "red")
            with open("missed.txt", "a") as f:
                f.write(f"Missed: {id} at {datetime.datetime.now().time()}\n")
            ### when return value is None, we go to the next song to check (see code in line 326)
            return None
        
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
            #self.vprint("mp3 deleted.")
    
    
    def get_channel_source(self):
        ### if a restore file is supplied, use that instead
        if self.arguments.restore_file is not None:
            with open(self.arguments.restore_file) as f:
                source = f.read()
            return source
        
        ### Open a browser and catch chromedriver not found error
        try:
            driver = webdriver.Chrome()
        except common.exceptions.WebDriverException:
            try:
                driver = webdriver.Chrome(executable_path = r"C:\ProgramData\chocolatey\bin\chromedriver.exe")
            except:
                print("If you see this, selenium can't find your chromedriver.")
                print("In order to fix this, search for the chromedriver on your file system (search the whole C: for \"chromedriver.exe\")")
                print("Now copy the file location of a chromedriver.exe and paste it")
                print(r"example input: C:\ProgramData\chocolatey\bin\chromedriver.exe")
                location = input("Paste here:")
                driver = webdriver.Chrome(executable_path = location)
                print("alternatively you can put it in the code yourself so you don't have to constantly fill this in.")
                print("To do that, in the file find_stable.py search for the line \"driver = webdriver.Chrome()\" and in between the brackets put")
                print("executable_path = YOUR_CHROMEDRIVER_LOCATION")
        
        
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
        
        with open("restore_file.html", "w") as f:
            f.write(source.encode('utf-8').decode('ascii','ignore'))
        
        return source
    
    
    def check_file(self, fpath, thresh=20):
        """
        Fingerprint and try to match a song against database
        """
        ### Getting ID from filepath, Might just supply ID as argument
        base = os.path.basename(fpath)
        id_, _ = os.path.splitext(base)
        
        matches = run_recognition(fpath)
        song = align_matches(self.sql, matches)
        confidence = song['CONFIDENCE']
        self.vprint(f"Confidence of a match: {confidence}", "yellow")
        
        ### If there's a match, give feedback to user
        if confidence >= thresh:
            self.vprint(f"POSSIBLE MATCH FOUND FOR ID: {id_}", "green")
            with open("MATCHES.txt", "a") as f:
                f.write(f"Video with YT ID {id_} has a match with the database! Oh my lawd please check it\n")
        
        return confidence >= thresh
    
        
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
    
    
    def check_one_video(self, id_):
        song_fpath = self.get_song_mp3(id_)
        if song_fpath is None:
                return
        
        possible_match = self.check_file(song_fpath, )
        
        if possible_match:
            song_fname = os.path.split(song_fpath)[1]
            with open("MATCHES.txt", "a") as f:
                f.write(f"{song_fname} with YT ID {id_} has a match with the database! Oh my lawd please check it\n")
        else:
            self.vprint("Probably not a match")
    
    
    def check_channel(self, max_duration=210):
        #Get the HTML source of the channel's video section
        source = self.get_channel_source()
        videos = self.get_videos(source)
        
        target_videos = []
        for video in videos:
            if ((self.ignore_checked == False and video["duration"] <=max_duration) 
                or 
                (video["duration"]<= max_duration and (self.ignore_checked == True and not self.sql.in_checked_ids(video["id"])))):
                target_videos.append(video)
        
        total_videos = len(target_videos)
        if total_videos == 0: self.vprint("All videos have been checked or are longer than than the max duration.","green"), exit()
        
        
        _ = 0
        for index in range(round(len(target_videos)/self.arguments.threads)):
            section = target_videos[self.arguments.threads*index : self.arguments.threads*(index+1)]
            
            jobs = []
            for video in section:
                ### this seems like complicated logic but it's exactly what we want, 
                ### please fill in "(p^~q) or (p ^ (q^ (~r)))" on the website 
                ### https://web.stanford.edu/class/cs103/tools/truth-table-tool/ to see for yourself
                
                    id_ = video["id"]
                    try:
                        thread = threading.Thread(target=self.get_song_mp3, args=(id_,))
                    except KeyboardInterrupt:
                        self.delete_mp3s
                        exit()
                    jobs.append(thread)
            
            self.vprint("Downloading mp3s...")
            for job in jobs:
                _+=1
                job.start()
            for job in jobs:
                job.join()
                
                ### we skip this song if something went wrong with the download
                #if song_fpath is None:
                #    ### Skip to the next video in the for loop
                #    continue 
                
            #self.delete_mp3s()
            #continue
            #pass
            #exit()
            # this works now :)
            
            jobs = []
            for file in os.listdir("downloaded_mp3s"):
                p = threading.Thread(target=self.check_file, args=(os.path.join("downloaded_mp3s", file), self.arguments.threshold, ))
                #filename, file_extension = os.path.splitext(file)
                #self.sql.add_checked_id(filename)
                jobs.append(p)
            
            for job in jobs:
                job.start()
            for job in jobs:
                job.join()
                
            self.vprint(f"{100*(_)/total_videos:.2f}% done")
            
            self.delete_mp3s()
            print("")    
        self.delete_mp3s()
    
    
    def main(self):
        if self.arguments.id is not None:
            self.check_one_video(self.arguments.id)
        else:
            self.check_channel()
        
        print(f"runtime: {time.time() - start_time}")
        

def get_arguments():
    parser = argparse.ArgumentParser(description='''TMS-Finder''')
    
    parser.add_argument("-i", "--ignore", dest = "ignore", default=False, help="Ignore already checked videos", action='store_true')
    parser.add_argument("-s", "--speedmode", dest = "speedmode", help="Activate speed mode", action = "store_true")
    parser.add_argument("-v", "--verbose", dest = "verbose", help="Give Feedback, default = True", action = "store_true", default = True)
    parser.add_argument("-t", "--threshold", dest = "threshold", action="store", type = int, help = "Set the threshold for the number of hash matches at which you are notified of a match, default is 20", default = 20)
    parser.add_argument("-m", "--multi-threading", dest="threads", action="store",type=int, help="Amount of videos allowed to concurrently check, default is 1", default=1)
    parser.add_argument("-c", "--channel", dest = "channel_url", help="Parse the channel url as command line argument")
    parser.add_argument("-id" ,"--id", dest = "id", help = "Test a single video instead of a whole YT channel.")
    parser.add_argument("-r", "--restore-file", dest = "restore_file", help="Give a restore file to get the html source of a channel without opening the browser again")
    
    return parser.parse_args()


if __name__ == '__main__':
    finder = Finder()
    try:
        finder.main()
    except:
        print("Why you leaving me :(")
        sys.exit()
        finder.delete_mp3s()
        exit()

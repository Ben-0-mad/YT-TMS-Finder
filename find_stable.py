import os                               #for various things
from webbot import Browser              #for getting html source of channel
from time import sleep                  #to prevent errors
import re                       
import bs4 as bs                        #for working with html source file
import subprocess                       #calling other script or executables from this file
from libs.db_sqlite import SqliteDatabase #for working with the SQL database
import argparse                         #for getting command line arguments
from termcolor import colored           #for getting colored text

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

def get_arguments():
    parser = argparse.ArgumentParser(description="TMS-Finder")
    parser.add_argument("-i", "--ignore", dest="ignore", help="Ignore already checked videos", action='store_true')
    parser.add_argument("-s", "--speedmode", dest="speedmode", help="Activate speed mode", action = "store_true")
    return parser.parse_args()

args = get_arguments()

if not os.path.isdir("downloaded_mp3s"):
    os.mkdir("downloaded_mp3s")
else:
   None

class Finder:
    def __init__(self, channel_url):
        self.args = args
        self.channel_url = channel_url.replace('featured','videos')
        self.sql = SqliteDatabase()
        self.file_recogniser_path = os.path.join(os.getcwd(), "recognize-from-file.py")
    
    def get_song_mp3(self, id: str) -> None:
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
        
        # '%(title)s.%(ext)s' comes from how youtube-dl.exe outputs files with filename as youtube title
        destination_arg = os.path.join(dir_mp3s, "%(title)s.%(ext)s")
        #Make the mp3 folder which will contain a downloaded mp3
        if not os.path.isdir(dir_mp3s):
            os.mkdir(dir_mp3s)
        # Download the mp3 file from youtube
        try:
            os.system(f"{path_youtube_dl_exec} -x --audio-format mp3 -q --no-warnings -o {destination_arg} {url}")
            sleep(0.1)
            self.songname = os.listdir("downloaded_mp3s")[0]
            print(f"{os.listdir('downloaded_mp3s')[0]} downloaded, now performing fingerprint match scan. Please wait...")
        except:
            print(colored("Youtube audio couldn't be downloaded. Skipping for now.", "red", attrs=["dark"]))
        
        
        
    def delete_mp3s(self):
        """
        Deletes all mp3s in the mp3s folder.
        """
        current_directory = os.getcwd()
        for file in os.listdir("downloaded_mp3s"):
            full_path = os.path.join(current_directory, "downloaded_mp3s", file)
            os.remove(full_path)
            print("mp3 deleted.")
    
    def get_channel_ids(self):
        driver = Browser()
        driver.go_to(self.channel_url)
        sleep(3)
        source = driver.get_page_source()
        driver.scrolly(5000)
        while driver.get_page_source() != source:
            source = driver.get_page_source()
            driver.scrolly(5000)
        driver.quit()
        return source
        
    def check_file(self):
        output = subprocess.check_output(['python', self.file_recogniser_path, os.path.join(os.getcwd(), "downloaded_mp3s", self.songname )])
        if "POSSIBLE MATCH FOUND" in output.decode():
            print(colored("POSSIBLE MATCH FOUND!", "green", attrs=["dark"]))
            with open("MATCHES.txt", "a") as f:
                f.write(f"{self.songname} with YT ID {self.id} has a match with the database!\n")
            
    
    def check_channel(self):
        #Get the HTML source of the channel's video section
        source = self.get_channel_ids()
        
        #Wherever "href=\"/watch" is found within the page source, gives a list containing the position of each "href=\"/watch" substring
        starting_chars = [m.start() for m in re.finditer("href=\"/watch", source)]
        
        #now we want to get the video lengths
        soup = bs.BeautifulSoup(source,'lxml')
        
        #all time durations are contained within a span with class "style-scope ytd-thumbnail-overlay-time-status-renderer"
        time_spans = soup.findAll("span", {"class": "style-scope ytd-thumbnail-overlay-time-status-renderer"})
        
        #Gets a list with the time durations stripped from any trailing spaces
        time_spans_plain = [time_span.text.strip() for time_span in time_spans]
        del time_spans
        
        for starting_char, time_span in zip(starting_chars[0::2], time_spans_plain):
            split_time = time_span.split(":")
            if int(split_time[-2]) < 4 and len(split_time) <= 2: #the minutes number is less than 4 and it isn't over an hour long
                self.id = source[starting_char+15:starting_char+26]
                
                if self.args.ignore:
                    if not self.sql.in_checked_ids(self.id):
                        print("")
                        print(f"Song with id {self.id} is less than 4 minutes! ({time_span})")
                        self.get_song_mp3(self.id)
                        self.check_file()
                        self.delete_mp3s()
                        self.sql.add_checked_id(self.id)
                else:
                    print("")
                    print(f"Song with id {self.id} is less than 4 minutes! ({time_span})")
                    self.get_song_mp3(self.id)
                    self.check_file()
                    self.delete_mp3s()
                    self.sql.add_checked_id(self.id)
    


if __name__ == '__main__':
    os.system("color 07")
    channel_url = input("\nPlease enter the channel url: ")   #Example input: www.youtube.com/c/GlitchxCity/featured
    finder = Finder(channel_url)
    finder.check_channel()

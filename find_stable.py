import os
from webbot import Browser
import time
import re
import bs4 as bs
import subprocess
#from fuzzywuzzy import fuzz

print("""
Welcome to 


$$$$$$$$\ $$\      $$\  $$$$$$\         $$$$$$\  $$\                 $$\                     $$\ $$\ 
\__$$  __|$$$\    $$$ |$$  __$$\       $$  __$$\ \__|                $$ |                    $$ |$$ |
   $$ |   $$$$\  $$$$ |$$ /  \__|      $$ /  \__|$$\ $$$$$$$\   $$$$$$$ | $$$$$$\   $$$$$$\  $$ |$$ |
   $$ |   $$\$$\$$ $$ |\$$$$$$\        $$$$\     $$ |$$  __$$\ $$  __$$ |$$  __$$\ $$  __$$\ $$ |$$ |
   $$ |   $$ \$$$  $$ | \____$$\       $$  _|    $$ |$$ |  $$ |$$ /  $$ |$$$$$$$$ |$$ |  \__|\__|\__|
   $$ |   $$ |\$  /$$ |$$\   $$ |      $$ |      $$ |$$ |  $$ |$$ |  $$ |$$   ____|$$ |              
   $$ |   $$ | \_/ $$ |\$$$$$$  |      $$ |      $$ |$$ |  $$ |\$$$$$$$ |\$$$$$$$\ $$ |      $$\ $$\ 
   \__|   \__|     \__| \______/       \__|      \__|\__|  \__| \_______| \_______|\__|      \__|\__|
                                                                                                     

example url:  https://www.youtube.com/channel/UCmSynKP6bHIlBqzBDpCeQPA/videos
""")


class Finder:
    def __init__(self, channel_url):
        self.channel_url = channel_url.replace('featured','videos')
        #self.tms_fp = self.fingerprint_mp3("TMS.mp3")
    
    def get_song_mp3(self, id: str) -> None:
        """
        Downloads the audio from a youtube video in mp3 format given a video id.
        """
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
        os.system(f"{path_youtube_dl_exec} -x --audio-format mp3 -q --no-warnings -o {destination_arg} {url}")
        
    def delete_mp3s(self):
        """
        Deletes all mp3s in the mp3s folder.
        """
        current_directory = os.getcwd()
        for file in os.listdir("downloaded_mp3s"):
            full_path = os.path.join(current_directory, "downloaded_mp3s", file)
            os.remove(full_path)

    def get_channel_vid_ids(self):
        #Get the HTML source of the channel's video section
        driver = Browser()
        driver.go_to(self.channel_url)
        time.sleep(3)
        source = driver.get_page_source()
        driver.scrolly(5000)
        while driver.get_page_source() != source:
            source = driver.get_page_source()
            driver.scrolly(5000)
        driver.quit()
        
        #Wherever "href=\"/watch" is found within the page source, gives a list containing the position of each "href=\"/watch" substring
        starting_chars = [m.start() for m in re.finditer("href=\"/watch", source)]
        
        #now we want to get the video lengths
        soup = bs.BeautifulSoup(source,'lxml')
        
        #all time durations are contained within a span with class "style-scope ytd-thumbnail-overlay-time-status-renderer"
        time_spans = soup.findAll("span", {"class": "style-scope ytd-thumbnail-overlay-time-status-renderer"})
        
        #Gets a list with the time durations stripped from any trailing spaces
        time_spans_plain = [time_span.text.strip() for time_span in time_spans]
        del time_spans
        
        #for a,b in zip(starting_chars[0::2], time_spans_plain):
        #    print(a,b)
        
        #for starting_char, time_span in zip(starting_chars[::2], time_spans_plain):
        for starting_char, time_span in zip(starting_chars[0::2], time_spans_plain):
            if int(time_span.split(":")[-2]) < 3:
                id=source[starting_char+15:starting_char+26]
                print(id, time_span)
                print(f"\nSong with id {id} is less than 3 minutes! ({time_span.split(':')[-2]})")
                print("Downloading mp3...")
                self.get_song_mp3(id)
                print(f"{os.listdir('downloaded_mp3s')[0]} downloaded, now performing fingerprint match scan. Please wait...")
                file_recogniser_path = os.path.join(os.getcwd(), "recognize-from-file.py")
                songname = os.listdir("downloaded_mp3s")[0]
                output = subprocess.check_output(['python', file_recogniser_path, os.path.join(os.getcwd(), "downloaded_mp3s", songname )])
                if "POSSIBLE MATCH FOUND" in output.decode():
                    print("POSSIBLE MATCH FOUND!")
                    with open("MATCHES.txt", "a") as f:
                        f.write(f"{songname} with YT ID {id} has a match with the database!\n")
                self.delete_mp3s()
    


if __name__ == '__main__':
    #os.system("color 02")
    #print("Only 1337 hacekrs may use this python scwipt!")
    
    channel_url = input("\nPlease enter the channel url: ")   #Example input: www.youtube.com/c/GlitchxCity/featured
    finder = Finder(channel_url)
    finder.get_channel_vid_ids()
    #finder.test()
    #finder.delete_mp3() WORKS
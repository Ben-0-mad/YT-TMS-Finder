#!/usr/bin/python3
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from libs.reader_file import FileReader
from libs.db_sqlite import SqliteDatabase
from libs.utils import logmsg, find_matches, align_matches


def run_recognition(filename, print_output=False):
    db = SqliteDatabase()

    abs_filename = os.path.abspath(filename)
    filename = abs_filename.rsplit(os.sep)[-1]

    r = FileReader(abs_filename)
    data = r.parse_audio()

    Fs = data["Fs"]
    channel_amount = len(data["channels"])
    matches = []

    for channeln, channel in enumerate(data["channels"]):
        # TODO: Remove prints or change them into optional logging.
        #if print_output:
            #msg = "   fingerprinting channel %d/%d"
            #print(
            #    logmsg(msg, attrs=["dark"], prefix=filename)
            #    % (channeln + 1, channel_amount)
            #)

        matches.extend(find_matches(db, channel, Fs, filename, print_output))

        #if print_output:
            #msg = "   finished channel %d/%d, got %d hashes"
            #print(
            #    logmsg(msg, attrs=["dark"], prefix=filename)
            #    % (channeln + 1, channel_amount, len(matches))
            #)

    #print_match_results(db, matches, filename)
    return matches


def run_recognition_scan_dir(dirname):
    pathlist = Path(os.path.abspath(dirname)).glob("**/*.mp3")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []

        for path in pathlist:
            futures.append(executor.submit(run_recognition, str(path), False))

        for future in as_completed(futures):
            future.result()


if __name__ == "__main__":
    args = sys.argv[1:]

    filename = None
    scan_dir = False
    if len(args) > 0 and (args[0] == "--dir" or args[0] == "--dirname"):
        scan_dir = True

        if len(args) > 1:
            filename = args[1]
        else:
            print("Must supply a directory name to scan")
            sys.exit(1)
    elif len(args) > 0:
        filename = args[0]
    else:
        print("Must supply a file name to match")
        sys.exit(1)

    if scan_dir is True:
        run_recognition_scan_dir(filename)
    else:
        run_recognition(filename)

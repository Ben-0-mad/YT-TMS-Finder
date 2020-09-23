#!/usr/bin/python3
from termcolor import colored
from libs.db_sqlite import SqliteDatabase
import sys
import os

sys.path.append(os.path.join(sys.path[0], ".."))


if __name__ == "__main__":
    db = SqliteDatabase()

    row = db.executeOne("SELECT 2+3 as x;")

    assert row[0] == 5, "failed simple sql execution"
    print(" * %s" % colored("ok", "green"))

import argparse
import os
import sys
import json
from changes import run_change_report


report_data_loc = "./reports/data/"  # file listings (data backing the reports)
report_text_loc = "./reports/text/"  # reports in JSON
report_index_loc = "./reports/index.json"  # index of all reports
watch_index_loc = "./reports/watch_index.json"  # index of directories being watched


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", help="directory to watch")
args = parser.parse_args()


def find_watch(directory):
    with open(watch_index_loc, 'r') as watch_index:
        index_dict = json.load(watch_index)
    watch_list = index_dict["watches"]
    if directory in watch_list:
        print("being watched")
        watch_settings = watch_list[directory]["ignore_list"]
        print(watch_settings)
        run_change_report(directory, watch_settings, "existing", "cli")
    else:
        print("directory not watched")


def take_input():
    if args.directory:
        if not os.path.exists(args.directory):
            print("Error. No such directory:", args.directory, file=sys.stderr)
            return
        else:
            find_watch(args.directory)
    else:
        print("you must specify a directory")


def main():
    take_input()


if __name__ == "__main__":
    main()

import json
import datetime
import magic
import os
from pathlib import Path
from prompt_toolkit.shortcuts import button_dialog
from shared import get_file_list, error_dialog, file_count_confirmation, print_report_to_screen


report_data_loc = "./reports/data/"  # file listings (data backing the reports)
report_text_loc = "./reports/text/"  # reports in JSON
report_index_loc = "./reports/index.json"  # index of all reports
watch_index_loc = "./reports/watch_index.json"  # index of directories being watched


def diff_file_listing(latest, penultimate, directory_path):
    latest_set = set()
    penultimate_set = set()

    new_files = []
    unchanged_files = []
    deleted_files = []
    modified_files = []
    renamed_files = []

    with open(latest, 'r') as latest_report:
        latest_dict = json.load(latest_report)
        for file in latest_dict["files"]:
            latest_set.add(json.dumps(file))

    if penultimate is None:
        # if this is the first time a change report has run, all files are new
        for item in latest_set:
            file_dict = json.loads(item)
            new_files.append(file_dict["file_path"])
    else:
        with open(penultimate, 'r') as penultimate_report:
            penultimate_dict = json.load(penultimate_report)
            for file in penultimate_dict["files"]:
                penultimate_set.add(json.dumps(file))

        unchanged = latest_set.intersection(penultimate_set)
        for item in unchanged:
            file_dict = json.loads(item)
            unchanged_files.append(file_dict["file_path"])

        latest_unique = latest_set.difference(penultimate_set)
        penultimate_unique = penultimate_set.difference(latest_set)

        latest_by_inode = {}
        for item in latest_unique:
            file_dict = json.loads(item)
            inode_string = str(file_dict["inode"])
            latest_by_inode[inode_string] = file_dict

        penultimate_by_inode = {}
        for item in penultimate_unique:
            file_dict = json.loads(item)
            inode_string = str(file_dict["inode"])
            penultimate_by_inode[inode_string] = file_dict

        inodes_in_both = set()
        for penultimate_key in penultimate_by_inode:
            if penultimate_key in latest_by_inode:
                inodes_in_both.add(penultimate_key)
            else:
                deleted_files.append(penultimate_by_inode[penultimate_key]["file_path"])

        for latest_key in latest_by_inode:
            if latest_key in penultimate_by_inode:
                inodes_in_both.add(latest_key)
            else:
                new_files.append(latest_by_inode[latest_key]["file_path"])

        # check on files where inode is same, something else is not
        for inode in inodes_in_both:
            latest_file = latest_by_inode[inode]
            penultimate_file = penultimate_by_inode[inode]
            if latest_file["size"] != penultimate_file["size"]:
                modified_files.append(latest_file["file_path"])

            if latest_file["file_path"] != penultimate_file["file_path"]:
                renamed_file = {"old": penultimate_file["file_path"], "new": latest_file["file_path"]}
                renamed_files.append(renamed_file)

    # write change report to file
    current_date = datetime.datetime.now()
    current_date_flattened = current_date.strftime('%Y-%m-%d_%H_%M_%S')
    change_report_name = 'change' + directory_path.replace('/', '_') + '_' + current_date_flattened + '.json'
    change_report_path = report_text_loc + change_report_name
    report_dict = {"directory": directory_path, "date": current_date.isoformat(),
                   "changes": {
                       "new": new_files, "deleted": deleted_files, "renamed": renamed_files,
                       "modified": modified_files, "unchanged": unchanged_files}
                   }

    with open(change_report_path, 'w') as contents_file:
        json.dump(report_dict, contents_file)

    # update the report index
    new_report = {"directory": directory_path, "date": current_date.isoformat(), "report_path": change_report_path,
                  "report_type": "change"}
    with open(report_index_loc, 'r') as report_index:
        index_dict = json.load(report_index)
    index_dict["reports"].append(new_report)
    with open(report_index_loc, 'w') as report_index:
        json.dump(index_dict, report_index)

    # finally, show the report to the user
    print_report_to_screen(change_report_path)


def run_change_report(directory_path, ignore_list, origin, mode):
    # logic:
    #   find all files
    #   ignore anything on the ignore list

    # get the list of files
    file_list = []
    file_list_success = get_file_list(directory_path, file_list)
    if file_list_success is False:
        if mode == "interactive":
            error_dialog("no_perms", directory_path)
        elif mode == "cli":
            print("there was a permissions problem")
        return

    file_count = len(file_list)
    proceed = file_count_confirmation(file_count)
    if proceed is False:
        return  # back to main menu

    # write new watch configuration to file, but first check if config already exists
    new_watch_config = {"ignore_list": ignore_list}
    with open(watch_index_loc, 'r') as watch_index:
        watch_index_dict = json.load(watch_index)
    if directory_path not in watch_index_dict["watches"]:
        watch_index_dict["watches"][directory_path] = new_watch_config
    else:
        if origin == "new":
            # if the watch is already on the list, but user entered it as new,
            # check if user wants to re-use existing config
            choice = button_dialog(
                title="Directory already on the watch list",
                text="The selected directory '" + directory_path + "' is already on the watch list. "
                     "Do you want to run a report with new settings?\n\n"
                     "Note: if you've modified the ignore list, those changes will be applied to the "
                     "watch configuration going forward. Choose 'cancel' if you do not wish to change the settings."
                     "\n\nCurrent ignore list:     "
                     + str(watch_index_dict["watches"][directory_path]["ignore_list"])
                     + "\nProposed ignore list:    " + str(new_watch_config["ignore_list"]),
                buttons=[
                    ('Continue', True),
                    ('Cancel', False)]
            ).run()
            if choice is False:
                return
            else:
                watch_index_dict["watches"][directory_path] = new_watch_config
        else:
            watch_index_dict["watches"][directory_path] = new_watch_config
    with open(watch_index_loc, 'w') as watch_index:
        json.dump(watch_index_dict, watch_index)

    # get file details
    file_array = []
    for file in file_list:
        if not os.path.basename(file) in ignore_list:
            stat_dict = {}
            file_stats = Path(file).stat()
            stat_dict["file_path"] = file
            stat_dict["size"] = file_stats.st_size
            stat_dict["inode"] = file_stats.st_ino
            stat_dict["mime_type"] = magic.from_file(file, mime=True)
            file_array.append(stat_dict)

    # save new file listing to the reports data directory
    current_date = datetime.datetime.now()
    current_date_flattened = current_date.strftime('%Y-%m-%d_%H_%M_%S')
    file_report_name = 'files' + directory_path.replace('/', '_') + '_' + current_date_flattened + '.json'
    file_report_path = report_data_loc + file_report_name
    report_dict = {"directory": directory_path, "date": current_date.isoformat(), "files": file_array}
    with open(file_report_path, 'w') as file_listing:
        json.dump(report_dict, file_listing)

    # add new report to the reports index
    new_report = {"directory": directory_path, "date": current_date.isoformat(), "report_path": file_report_path,
                  "report_type": "file_listing"}
    with open(report_index_loc, 'r') as report_index:
        index_dict = json.load(report_index)
    index_dict["reports"].append(new_report)
    with open(report_index_loc, 'w') as report_index:
        json.dump(index_dict, report_index)

    # get existing reports so that we can figure out which are the most recent
    with open(report_index_loc, 'r') as report_index:
        index_dict = json.load(report_index)
    index_list = index_dict["reports"]
    previous_listings = []
    for report in index_list:
        if report["directory"] == directory_path and report["report_type"] == "file_listing":
            previous_listings.append(report)

    # use the new file listing data to determine what has or has not changed in the directory since the last report
    if len(previous_listings) < 2:
        # if this was the first report for the directory, there won't be a penultimate one: all files are new
        diff_file_listing(previous_listings[-1]["report_path"],
                          None,
                          directory_path)
    else:
        diff_file_listing(previous_listings[-1]["report_path"],
                          previous_listings[-2]["report_path"],
                          directory_path)

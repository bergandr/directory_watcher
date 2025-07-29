import os
from pathlib import Path
import datetime
from prompt_toolkit.shortcuts import message_dialog, radiolist_dialog, button_dialog, input_dialog
import magic
import json
from prompt_toolkit import prompt
from prompt_toolkit import print_formatted_text

report_data_loc = "./reports/data/"  # file listings (data backing the reports)
report_text_loc = "./reports/text/"  # reports in JSON
report_index_loc = "./reports/index.json"  # index of all reports
watch_index_loc = "./reports/watch_index.json"  # index of directories being watched


def error_dialog(err_type, input_path):
    if err_type == "no_dir":
        error_text = "Error: directory not found: " + input_path
    elif err_type == "not_dir":
        error_text = "Error: input is not a directory: " + input_path
    elif err_type == "no_perms":
        error_text = "Error: you do not have the required permissions to view the contents of " + input_path
    else:
        error_text = "Error: there was an error trying to read " + input_path

    message_dialog(
        title="Error",
        text=error_text,
    ).run()


def create_report_storage_if_none():
    """
    Create index of reports if none exists - this will create the required files and directories at first launch.
    """
    # create reports index
    if not os.path.exists(report_index_loc):
        blank_index_dict = {"reports": []}
        with open(report_index_loc, 'w') as report_index:
            json.dump(blank_index_dict, report_index)

    # create watch index
    if not os.path.exists(watch_index_loc):
        blank_index_dict = {"watches": {}}
        with open(watch_index_loc, 'w') as watch_index:
            json.dump(blank_index_dict, watch_index)

    # create reports data directory
    if not os.path.exists(report_data_loc):
        os.mkdir(report_data_loc)

    # create reports text directory
    if not os.path.exists(report_text_loc):
        # create reports text directory
        os.mkdir(report_text_loc)


def validate_directory(directory_path):
    # validate directory exists
    if not os.path.exists(directory_path):
        error_dialog("no_dir", directory_path)
        return False
    elif not os.path.isdir(directory_path):
        error_dialog("not_dir", directory_path)
        return False
    else:
        return True


def file_count_confirmation(file_count):
    choice = button_dialog(
        title="Ready to run the report?",
        text="The selected directory contains "
             + str(file_count) +
             " files. Directories with a large number of files may take a long time to process.\n\n"
             "Would you still like to continue?",
        buttons=[
            ('Continue', True),
            ('Cancel', False)]
    ).run()

    return choice


def welcome_screen():
    welcome_text = ("Welcome to Directory Watcher!\n\n"
                    "Keep track of important data by monitoring directories for changes.\n"
                    "Directory Watcher generates reports of new files, deleted files, and files that have changed.")
    welcome_choice = button_dialog(
        title="Directory Watcher!",
        text=welcome_text,
        buttons=[
            ("Enter", "Enter"),
            ("Quit", "Quit"),
        ]
    ).run()

    return welcome_choice


def help_screen():
    help_text = "Some help text." \
        "\n\nWould you like to continue?"

    help_choice = button_dialog(
        title="Welcome!",
        text=help_text,
        buttons=[
            ("Yes", "Enter"),
            ("Quit", "Quit"),
        ]
    ).run()

    return help_choice


def main_menu():
    main_choice = radiolist_dialog(
        title="Main menu",
        text="Choose from the following options:\n",
        values=[
            ("manage_watch", "Manage watched directories\n"),
            ("add_watch", "Add watched directory\n"),
            ("list_reports", "List all reports\n"),
            ("new_contents", "Create new contents report\n    (report of filetypes within a directory)\n"),
            ("help", "Help\n\n"
             "(arrow keys: navigate selections; 'Enter': choose a selection; 'Tab': jump to select/quit")
        ],
        ok_text="Select",
        cancel_text="Quit",
    ).run()

    return main_choice


def print_report_to_screen(report_path):
    with open(report_path, 'r') as report:
        report_dict = json.load(report)
    report_json_pretty = json.dumps(report_dict, indent=4)
    os.system('clear')
    print_formatted_text(report_json_pretty)
    print("\nThis report is located at: ", report_path)
    prompt("\nPress enter to return to the main menu. ")


def list_reports():
    # list all reports and report types
    with open(report_index_loc, 'r') as report_index:
        index_dict = json.load(report_index)
    index_list = index_dict["reports"]
    display_list = []
    for report in index_list:
        # only list 'contents' or 'change' reports, not raw file list data
        if report["report_type"] != "file_listing":
            report_date = report["date"]
            report_type = report["report_type"]
            report_dir = report["directory"]
            value_path = report["report_path"]
            display_text = report_type + ' | ' + report_date + ' | ' + report_dir
            display_list.append((value_path, display_text))

    report_choice = radiolist_dialog(
        title="All reports",
        text="Choose a report from the list, then select 'Open' to view it.",
        values=display_list,
        ok_text="Open",
        cancel_text="Main menu",
    ).run()

    # if the user doesn't select a report
    if report_choice is None:
        return

    # print the selected report to the screen
    print_report_to_screen(report_choice)


def get_file_list(directory, file_list):
    # following example from https://blog.finxter.com/5-best-ways-to-traverse-a-directory-recursively-in-python/
    # recurse through directories, list non-directories as you traverse
    try:
        for listing in os.listdir(directory):
            full_path = os.path.join(directory, listing)
            if os.path.isdir(full_path):
                file_list_success = get_file_list(full_path, file_list)
                if file_list_success is False:
                    return False
            else:
                file_list.append(full_path)
        return True

    except PermissionError:
        error_dialog("no_perms", directory)
        return False

    except OSError:
        error_dialog("OSError", directory)
        return False


def run_contents_report(directory_path):
    file_list = []
    file_list_success = get_file_list(directory_path, file_list)
    if file_list_success is False:
        error_dialog("no_perms", directory_path)
        return

    file_count = len(file_list)
    proceed = file_count_confirmation(file_count)
    if proceed is False:
        return  # back to main menu

    file_array = []
    for file in file_list:
        stat_dict = {}
        file_stats = Path(file).stat()
        stat_dict["file_path"] = file
        stat_dict["size"] = file_stats.st_size
        stat_dict["inode"] = file_stats.st_ino
        stat_dict["mime_type"] = magic.from_file(file, mime=True)
        file_array.append(stat_dict)

    mimetypes_count = {}
    for item in file_array:
        mime = item["mime_type"]
        if mime in mimetypes_count:
            mimetypes_count[mime] += 1
        else:
            mimetypes_count[mime] = 1

    current_date = datetime.datetime.now()
    current_date_flattened = current_date.strftime('%Y-%m-%d_%H_%M_%S')
    contents_report_name = directory_path.replace('/', '_') + '_' + current_date_flattened + '.json'
    contents_report_path = "reports/text/contents" + contents_report_name
    report_dict = {"directory": directory_path, "date": current_date.isoformat(), "mimetypes": mimetypes_count}
    with open(contents_report_path, 'w') as contents_file:
        json.dump(report_dict, contents_file)

    new_report = {"directory": directory_path, "date": current_date.isoformat(), "report_path": contents_report_path,
                  "report_type": "contents"}
    with open(report_index_loc, 'r') as report_index:
        index_dict = json.load(report_index)
    index_dict["reports"].append(new_report)
    with open(report_index_loc, 'w') as report_index:
        json.dump(index_dict, report_index)

    # finally, show the report to the user
    print_report_to_screen(contents_report_path)


def new_contents_report_menu():
    # get directory path
    valid_directory = False
    directory_path = None
    get_directory_text = ("Please enter the absolute path to a directory.\n\n"
                          "Note: to run a report, you must have full "
                          "read permissions to all files in the directory.")

    while not valid_directory:
        directory_path = input_dialog(
            title="Choose a directory",
            text=get_directory_text,
            ok_text="Continue",
        ).run()

        # return to main menu if user cancels
        if directory_path is None:
            return

        valid_directory = validate_directory(directory_path)

    run_contents_report(directory_path)


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


def run_change_report(directory_path, ignore_list):
    # logic:
    #   find all files
    #   ignore anything on the ignore list

    # get the list of files
    file_list = []
    file_list_success = get_file_list(directory_path, file_list)
    if file_list_success is False:
        error_dialog("no_perms", directory_path)
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
        # if the watch is already on the list, check if user wants to re-run it
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


def add_watch_menu():
    # get directory path
    valid_directory = False
    directory_path = None
    get_directory_text = ("Please enter the absolute path to a directory.\n\n"
                          "Note: to run a report, you must have full "
                          "read permissions to all files in the directory.")
    while not valid_directory:
        directory_path = input_dialog(
            title="Choose a directory",
            text=get_directory_text,
            ok_text="Continue",
        ).run()

        # return to main menu if user cancels
        if directory_path is None:
            return

        valid_directory = validate_directory(directory_path)

    # get ignore list
    ignore_dialog_text = ("Please enter a list of filenames to ignore.\n\n"
                          "Note: if you choose to ignore files previously included in the report, those "
                          "files will be listed as 'deleted' in the next report.")

    ignore_string = input_dialog(
        title="Ignore list",
        text=ignore_dialog_text,
        ok_text="Add list",
        cancel_text="Skip"
    ).run()

    # parse the ignore instructions into a list
    if ignore_string is not None and ignore_string != "":
        ignore_list = ignore_string.split('/')
    else:
        ignore_list = []

    run_change_report(directory_path, ignore_list)


def manage_watches():
    # list watched directories
    # look at watch config
    with open(watch_index_loc, 'r') as watch_index:
        index_dict = json.load(watch_index)
    watch_list = index_dict["watches"]

    display_list = []
    for watch in watch_list:
        display_list.append((watch, watch))

    watch_choice = radiolist_dialog(
        title="All watched directories",
        text="Choose a watched directory from the list, then select 'Open' to view settings.",
        values=display_list,
        ok_text="Open",
        cancel_text=" Main menu",
    ).run()

    # if the user chooses to return to the main menu
    if watch_choice is None:
        return

    watch_settings = watch_list[watch_choice]["ignore_list"]
    modify_watch_choice = radiolist_dialog(
        title="Current settings",
        text="Current settings for '" + watch_choice + "':\n" + "Ignore list: " + str(watch_settings),
        values=[
            ("as_is", "Run report with current settings."),
            ("modify", "Modify settings.")
        ],
        ok_text="Select",
        cancel_text="Main menu",
    ).run()

    if modify_watch_choice == "modify":
        # get ignore list
        ignore_dialog_text = ("Please enter a list of filenames to ignore.\n\n"
                              "Note: if you choose to ignore files previously included in the report, those "
                              "files will be listed as 'deleted' in the next report.")

        ignore_string = input_dialog(
            title="Ignore list",
            text=ignore_dialog_text,
            ok_text="Add list",
            cancel_text="Skip"
        ).run()

        # parse the ignore instructions into a list
        if ignore_string is not None and ignore_string != "":
            ignore_list = ignore_string.split('/')
        else:
            ignore_list = []
    elif modify_watch_choice == "as_is":
        ignore_list = watch_settings
    else:
        # if the user cancels
        return

    run_change_report(watch_choice, ignore_list)


def main():
    # run_change_report("/Users/andrewberger/experiments")
    # diff_file_listing("reports/data/_Users_andrewberger_experiments_2025-07-27_17_37_33.json",
    #                   "reports/data/_Users_andrewberger_experiments_2025-07-27_15_44_30.json",
    #                   "/Users/andrewberger/experiments")
    # print("only diffed")
    # return

    launch = welcome_screen()
    if launch == 'Quit':
        return

    # prepare to run and store reports
    create_report_storage_if_none()

    main_menu_choice = ""
    while main_menu_choice is not None:
        main_menu_choice = main_menu()
        if main_menu_choice == "new_contents":
            new_contents_report_menu()
        elif main_menu_choice == "list_reports":
            list_reports()
        elif main_menu_choice == "help":
            help_screen()
        elif main_menu_choice == "add_watch":
            add_watch_menu()
        elif main_menu_choice == "manage_watch":
            manage_watches()


if __name__ == "__main__":
    main()

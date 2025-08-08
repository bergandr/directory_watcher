import os
from prompt_toolkit.shortcuts import message_dialog, radiolist_dialog, button_dialog, input_dialog
import json
from shared import validate_directory, print_report_to_screen
from contents import run_contents_report
from changes import run_change_report


report_data_loc = "./reports/data/"  # file listings (data backing the reports)
report_text_loc = "./reports/text/"  # reports in JSON
report_index_loc = "./reports/index.json"  # index of all reports
watch_index_loc = "./reports/watch_index.json"  # index of directories being watched


def create_report_storage_if_none():
    """
    Create index of reports if none exists - this will create the required files and directories at first launch.
    """
    # create reports directory
    if not os.path.exists('./reports'):
        os.mkdir('./reports')

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


def welcome_screen():
    welcome_text = ("Welcome to Directory Watcher!\n\n"
                    "Keep track of important data by monitoring directories for changes.\n\n"
                    "Directory Watcher generates reports of new files, deleted files, and files that have changed.")
    welcome_choice = button_dialog(
        title="Directory Watcher!",
        text=welcome_text,
        buttons=[
            ("Launch", "Enter"),
            ("Quit", "Quit"),
        ]
    ).run()

    return welcome_choice


def main_menu():
    main_choice = radiolist_dialog(
        title="Main menu",
        text="Choose from the following options:\n",
        values=[
            ("new_contents", "Create new contents report\n    (report of filetypes within a directory)\n"),
            ("add_watch", "Add watched directory\n"),
            ("manage_watch", "Manage watched directories and check for new changes\n"),
            ("list_reports", "List all reports\n\n\n"
             "   [ Arrow keys: navigate selections; 'Enter': choose an option; 'Tab': jump to select/quit ]")
        ],
        ok_text="Select",
        cancel_text="Quit",
    ).run()

    return main_choice


def list_reports():
    # list all reports and report types
    with open(report_index_loc, 'r') as report_index:
        index_dict = json.load(report_index)
    index_list = index_dict["reports"]

    # check for an empty list
    if not index_list:
        message_dialog(
            title="No reports",
            text="No reports found. Reports will appear here once you've added them."
        ).run()
        return

    # get the list of reports to display
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
        text="Choose a report from the list, then select 'Open' to view it.\n\n"
             " Report_type |      Report date           |  Directory analyzed",
        values=display_list,
        ok_text="Open",
        cancel_text=" Main menu",
    ).run()

    # if the user doesn't select a report (this corresponds to the "Main Menu" value)
    if report_choice is None:
        return

    # print the selected report to the screen
    print_report_to_screen(report_choice)


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
    ignore_dialog_text = ("(Optional) Enter a list of filenames to ignore. These files will not be included"
                          "in the report.\n\n"
                          "To enter multiple filenames, separate each filename with a '/' character.")

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

    run_change_report(directory_path, ignore_list, "new", "interactive")


def manage_watches():
    # list watched directories
    # look at watch config
    with open(watch_index_loc, 'r') as watch_index:
        index_dict = json.load(watch_index)
    watch_list = index_dict["watches"]

    if not watch_list:
        message_dialog(
            title="Empty watchlist",
            text="No watched directories found. Watched directories will appear here once you've added them."
        ).run()
        return

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
        text="Current settings for '" + watch_choice + "':\n\n" + "Current ignore list: " + str(watch_settings),
        values=[
            ("as_is", "Run report with current settings."),
            ("modify", "Modify settings.")
        ],
        ok_text="Select",
        cancel_text="Main menu",
    ).run()

    if modify_watch_choice == "modify":
        # get ignore list
        ignore_dialog_text = ("Modify the list of filenames to ignore. Leave blank to stop ignoring files.\n\n"
                              "Note: changing the ignore list on an existing watch will affect the next report.\n"
                              "If you choose to ignore files previously included in the report, those "
                              "files will be listed as 'deleted' in the next report.\n"
                              "If you stop ignoring a previously ignored file, then it will appear as 'new' in"
                              "the next report.\n\n"
                              "Choose 'Skip' to retain the existing list.")

        ignore_string = input_dialog(
            title="Ignore list",
            text=ignore_dialog_text,
            ok_text="Add list",
            cancel_text="Skip"
        ).run()

        # parse the ignore instructions into a list
        if ignore_string is not None and ignore_string != "":
            ignore_list = ignore_string.split('/')
        elif ignore_string == "":
            ignore_list = []
        else:
            ignore_list = watch_settings
    elif modify_watch_choice == "as_is":
        ignore_list = watch_settings
    else:
        # if the user cancels
        return

    run_change_report(watch_choice, ignore_list, "existing", "interactive")


def main():
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
        # elif main_menu_choice == "help":
        #     help_screen()
        elif main_menu_choice == "add_watch":
            add_watch_menu()
        elif main_menu_choice == "manage_watch":
            manage_watches()


if __name__ == "__main__":
    main()

import os
from pathlib import Path
from prompt_toolkit.shortcuts import message_dialog, radiolist_dialog, button_dialog, input_dialog
import magic
# from prompt_toolkit import prompt
# from prompt_toolkit import print_formatted_text
# from prompt_toolkit import PromptSession
# from prompt_toolkit.completion import NestedCompleter, WordCompleter
# from prompt_toolkit.formatted_text import HTML
# from prompt_toolkit.styles import Style


def welcome_screen():
    welcome_text = "Some welcome text." \
        "\n\nWould you like to enter?"

    welcome_choice = button_dialog(
        title="Welcome!",
        text=welcome_text,
        buttons=[
            ("Yes", "Enter"),
            ("Quit", "Quit"),
        ]
    ).run()

    return welcome_choice


def main_menu():
    main_choice = radiolist_dialog(
        title="Main menu",
        text="Choose from the following options",
        values=[
            ("manage_watch", "Manage watched directories\n"),
            ("add_watch", "Add watched directory\n"),
            ("list_reports", "List all reports\n"),
            ("new_contents", "Create new contents report\n"),
            ("help", "Help")
        ],
        ok_text="Select",
        cancel_text="Quit",
    ).run()

    return main_choice


def manage_watch():
    # list watched directories
    # look at directory config
    # modify directory config
    # run new report and get diff
    pass


def add_watch():
    # get directory path
    # validate directory exists and confirm
    # get ignore list
    # validate ignore list
    # run first report
    # get ignore list
    # ignore_list_text = ("Please enter a list of filename patterns to ignore.\n\n"
    #                     "Note: to get an accurate count, you must have full "
    #                     "read permissions to all files in the directory.")
    #
    # ignore_list = input_dialog(
    #     title="Ignore list",
    #     text=ignore_list_text,
    #     ok_text="Continue",
    # ).run()
    pass


def list_reports():
    # list all reports and report types
    pass


def get_file_list(directory, file_list):
    # following example from https://blog.finxter.com/5-best-ways-to-traverse-a-directory-recursively-in-python/
    # recurse through directories, list non-directories as you traverse
    for listing in os.listdir(directory):
        full_path = os.path.join(directory, listing)
        if os.path.isdir(full_path):
            get_file_list(full_path, file_list)
        else:
            file_list.append(full_path)


def run_contents_report(directory_path):
    file_list = []
    get_file_list(directory_path, file_list)

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

    print(mimetypes_count)


def new_contents_report_menu():

    def error_dialog(err_type, input_path):
        if err_type == "no_dir":
            error_text = "Error: directory not found: " + input_path
        elif err_type == "not_dir":
            error_text = "Error: input is not a directory: " + input_path
        else:
            error_text = "Unknown error"

        message_dialog(
            title="Error",
            text=error_text,
        ).run()

    # get directory path
    valid_directory = False
    directory_path = None
    while not valid_directory:
        get_directory_text = ("Please enter the absolute path to a directory.\n\n"
                              "Note: to get an accurate count, you must have full "
                              "read permissions to all files in the directory.")

        directory_path = input_dialog(
            title="Choose a directory",
            text=get_directory_text,
            ok_text="Continue",
        ).run()

        # validate directory exists
        if not os.path.exists(directory_path):
            print("error: directory not found:", directory_path)
            error_dialog("no_dir", directory_path)
            # error dialog
        elif not os.path.isdir(directory_path):
            error_dialog("not_dir", directory_path)
        else:
            valid_directory = True

    run_contents_report(directory_path)
    # confirmation


def main_menu_control():
    pass


def main():
    launch = welcome_screen()
    if launch == 'Quit':
        return

    main_menu_choice = ""
    while main_menu_choice is not None:
        main_menu_choice = main_menu()
        if main_menu_choice == "new_contents":
            new_contents_report_menu()

    # run_contents_report("/Users/andrewberger/storage/r/exclude/")


if __name__ == "__main__":
    main()

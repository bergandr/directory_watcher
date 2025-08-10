import os
import json
from prompt_toolkit.shortcuts import message_dialog, button_dialog
from prompt_toolkit import print_formatted_text, HTML, prompt


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


def print_report_to_screen(report_path):
    with open(report_path, 'r') as report:
        report_dict = json.load(report)
    report_json_pretty = json.dumps(report_dict, indent=4)
    os.system('clear')
    print_formatted_text(report_json_pretty)
    print_formatted_text(HTML("\n<u>This report is located at:</u> "), report_path)
    prompt(HTML("\n<b>Press enter to return to the menu. </b>"))


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

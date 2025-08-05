import json
import magic
from pathlib import Path
from shared import error_dialog, get_file_list, file_count_confirmation, print_report_to_screen
import datetime


report_data_loc = "./reports/data/"  # file listings (data backing the reports)
report_text_loc = "./reports/text/"  # reports in JSON
report_index_loc = "./reports/index.json"  # index of all reports
watch_index_loc = "./reports/watch_index.json"  # index of directories being watched


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

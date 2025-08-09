import os


this_script_path = os.path.realpath(__file__)
this_script_dir = os.path.dirname(this_script_path)
report_data_loc = os.path.join(this_script_dir, "reports/data/")  # file listings (data backing the reports)
report_text_loc = os.path.join(this_script_dir, "reports/text/")  # reports in JSON
report_index_loc = os.path.join(this_script_dir, "reports/index.json")  # index of all reports
watch_index_loc = os.path.join(this_script_dir, "reports/watch_index.json")  # index of directories being watched

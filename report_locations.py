import os


this_script_path = os.path.realpath(__file__)
this_script_dir = os.path.dirname(this_script_path)
report_data_loc = os.path.join(this_script_dir, "reports/data/")  # file listings (data backing the reports)
report_text_loc = os.path.join(this_script_dir, "reports/text/")  # reports in JSON
report_index_loc = os.path.join(this_script_dir, "reports/index.json")  # index of all reports
watch_index_loc = os.path.join(this_script_dir, "reports/watch_index.json")  # index of directories being watched
checksum_dir = os.path.join(this_script_dir, "reports/checksums/")

# shared directories: microservices that generate files will place files in these locations
# data visualizer will save charts within its own directory, which is shared with the main program
chart_dir = "/Users/andrewberger/cs361/microservices/data-visualizer"

# report aggregation service will zip up files in a reports directory that it shares with the main program
zip_dir = os.path.join(this_script_dir, "reports/zips/")

import zmq
import time
import json
import datetime
from report_locations import report_index_loc, checksum_dir


def get_most_recent(directory_path):
    # get existing reports so that we can figure out which are the most recent
    with open(report_index_loc, 'r') as report_index:
        index_dict = json.load(report_index)
    index_list = index_dict["reports"]
    previous_listings = []
    for report in index_list:
        if report["directory"] == directory_path and report["report_type"] == "file_listing":
            previous_listings.append(report)

    most_recent_report = previous_listings[-1]["report_path"]
    return most_recent_report


def send_request(request):
    # this is basically boilerplate request setup code, based on the course-provided zmq documentation
    # establish the context, set up a request socket, and connect to the server
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:1111")

    # loop over the sample data
    print("\nSending", request)
    socket.send_json(request)  # use send_json since all requests will be in JSON format

    # get the reply from the server
    reply = socket.recv_json()
    print("Full reply:", reply)

    time.sleep(5)  # so that we can see each request more clearly on the video demo
    return reply


# def write_checksum_file(checksums):
#     with open('prng-service.txt', 'w') as prng_file:
#         prng_file.write("run")

def get_checksums(directory_path):
    file_list = []
    file_report_path = get_most_recent(directory_path)
    with open(file_report_path, 'r') as latest_report:
        latest_dict = json.load(latest_report)
        for file in latest_dict["files"]:
            file_list.append(file["file_path"])

    request = {"file_list": file_list}
    print(request)
    checksums = send_request(request)
    print(checksums)
    # write change report to file
    current_date = datetime.datetime.now()
    current_date_flattened = current_date.strftime('%Y-%m-%d_%H_%M_%S')
    checksum_report_name = 'checksums' + directory_path.replace('/', '_') + '_' + current_date_flattened + '.txt'
    checksum_report_path = checksum_dir + checksum_report_name

    with open(checksum_report_path, 'w') as checksum_file:
        for file in checksums:
            checksum_line = (checksums[file] + " " + file + '\n')
            checksum_file.write(checksum_line)

import shutil
import zmq
import time
import json
import os
from report_locations import zip_dir, report_index_loc
from prompt_toolkit import print_formatted_text, prompt, HTML


def send_request(request):
    # this is basically boilerplate request setup code, based on the course-provided zmq documentation
    # establish the context, set up a request socket, and connect to the server
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:3333")

    os.system('clear')
    request_pretty = json.dumps(request, indent=4)

    print("\nSending request to zip up reports\n", request_pretty)
    socket.send_json(request)  # use send_json since all requests will be in JSON format

    # get the reply from the server
    reply = socket.recv_json()
    reply_pretty = json.dumps(reply, indent=4)
    print("Received reply:\n", reply_pretty)

    time.sleep(5)  # so that we can see each request more clearly on the video demo
    return reply


def aggregate_reports(directory_path):
    zip_report_dir_name = 'zipped' + directory_path.replace('/', '_')
    zip_report_dir_full_path = os.path.join(zip_dir, zip_report_dir_name)
    os.mkdir(zip_report_dir_full_path)
    with open(report_index_loc, 'r') as report_index:
        index_dict = json.load(report_index)
    index_list = index_dict["reports"]

    for report in index_list:
        report_path = report["report_path"]
        if report["directory"] == directory_path:
            shutil.copy2(report_path, zip_report_dir_full_path)

    request = {"directory": zip_report_dir_full_path, "zip_name": zip_report_dir_name}
    result = send_request(request)

    if result["status"] == "success":
        shutil.rmtree(zip_report_dir_full_path)
        print_formatted_text(HTML("\n<u>The download is located at:</u> "), result["zipped_file"])
        prompt(HTML("\n<b>Press enter to return to the menu. </b>"))


def main():
    aggregate_reports("/Users/andrewberger/cs361-samples")


if __name__ == "__main__":
    main()

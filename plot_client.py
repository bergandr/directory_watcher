import json
import zmq
import time
import os
from report_locations import chart_dir


def get_contents_pie(report):
    rows = []

    with open(report, 'r') as report:
        report_dict = json.load(report)

    for mimetype in report_dict["mimetypes"]:
        rows.append([mimetype, report_dict["mimetypes"][mimetype]])
    data = {
        "chart_type": "pie",
        "data": {
            "headers": ["mimetype", "count"],
            "rows": rows
        }
    }
    return data


def get_changes_bar(report):
    rows = []

    with open(report, 'r') as report:
        report_dict = json.load(report)

    for change in report_dict["changes"]:
        count = len(report_dict["changes"][change])
        rows.append([change, count])

    data = {
        "chart_type": "bar",
        "data": {
            "headers": ["change_type", "count"],
            "rows": rows
        }
    }
    return data


def send_request(request_dict):
    request = json.dumps(request_dict)
    # this is basically boilerplate request setup code, based on the course-provided zmq documentation
    # establish the context, set up a request socket, and connect to the server
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    socket.send_string(request)  # use send_json since all requests will be in JSON format

    # get the reply from the server
    reply = socket.recv()
    reply_list = str(reply).split(':')

    # check for error in creating chart
    result = reply_list[0]
    if result == "Unsupported Chart Type":
        return

    # get path to chart
    chart_path = reply_list[1].strip("'")
    time.sleep(5)  # so that we can see each request more clearly on the video demo
    return chart_path


def route_plot_request(report, report_type):
    if report_type == "contents":
        request = get_contents_pie(report)
    elif report_type == "change":
        request = get_changes_bar(report)
    else:
        print("wrong chart type")
        return

    relative_chart_path = send_request(request)
    full_chart_path = os.path.join(chart_dir, relative_chart_path)
    return full_chart_path

import zmq
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit import prompt, HTML

python_path = "/opt/miniconda3/bin/python"
app_path_cli = "/Users/andrewberger/PycharmProjects/directory_watcher/dirwatch.py"


def send_request(command_dict):
    # this is basically boilerplate request setup code, based on the course-provided zmq documentation
    # establish the context, set up a request socket, and connect to the server
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:7777")

    # send the request
    print("\nSending", command_dict)
    socket.send_json(command_dict)  # use send_json since all requests will be in JSON format

    # get the reply from the server
    reply = socket.recv_json()
    print("Full reply:", reply)


def build_command(directory):
    command_line = python_path + " " + app_path_cli + " -d " + directory
    unit_choice = radiolist_dialog(
        title="Schedule a report",
        text="Choose a schedule for monitoring changes to '" + directory,
        values=[
            ("minute", "Every minute"),
            ("hour", "Hourly"),
            ("day", "Daily"),
        ],
        ok_text="Select",
        cancel_text="Watch menu",
    ).run()

    command_dict = {"command": command_line, "unit": unit_choice, "interval": 1}
    send_request(command_dict)

    prompt(HTML("\n<b>Press enter to return to the menu. </b>"))

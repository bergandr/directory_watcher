import os
from prompt_toolkit import prompt
from prompt_toolkit import print_formatted_text
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter, WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import message_dialog, radiolist_dialog, checkboxlist_dialog, button_dialog, input_dialog
from prompt_toolkit.styles import Style


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
    main_menu_text = '''
    
    Directory Watcher
    
    Main menu
    
    1. Manage watched directories
    
    2. Add watched directory
    
    3. List all reports
    
    4. Create new contents report
    '''

    main_choice = radiolist_dialog(
        title="Main menu",
        text="Choose from the following options",
        values=[
            ("option1", "Manage watched directories"),
            ("option2", "Add watched directory"),
            ("option3", "List all reports"),
            ("option4", "Create new contents report")
        ],
        ok_text="Select",
        cancel_text="Quit",
    ).run()

    return main_choice


def main():
    launch = welcome_screen()
    if launch == 'Quit':
        return

    main_menu_choice = main_menu()
    print(main_menu_choice)


if __name__ == "__main__":
    main()

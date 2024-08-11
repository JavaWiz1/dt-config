from dt_tools.cli.dt_console_helper_demo import demo as console_helper_demo
from dt_tools.cli.dt_console_input_helper_demo import demo as console_input_helper_demo
from dt_tools.cli.dt_msgbox_demo import demo as message_box_demo
from dt_tools.cli.dt_progress_bar_demo import demo as progress_bar_demo
from dt_tools.cli.dt_spinner_demo import demo as spinner_demo
from dt_tools.console.console_helper import ColorFG
from dt_tools.console.console_helper import ConsoleHelper as console
from dt_tools.console.console_helper import ConsoleInputHelper as console_input

if __name__ == '__main__':
    DEMOS = {
        "ConsoleHelper": console_helper_demo,
        "ConsoleInputHelper": console_input_helper_demo,
        "MessageBox": message_box_demo,
        "ProgressBar": progress_bar_demo,
        "Spinner": spinner_demo
    }

    console.clear_screen()
    for name, demo_func in DEMOS.items():
        demo_name = console.cwrap(name, ColorFG.YELLOW)
        resp = console_input.get_input_with_timeout(f'Demo {demo_name} Functions (y/n) > ', 
                                                console_input.YES_NO_RESPONSE, default='n', 
                                                timeout_secs=10).lower()
        if resp == 'y':
            demo_func()
            console.print()

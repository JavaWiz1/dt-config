import time

import dt_tools.console.console_helper as helper
from dt_tools.console.console_helper import (ConsoleControl, ConsoleHelper,
                                             ConsoleInputHelper, CursorShape,
                                             CursorVisibility)


def console_helper_demo():
    console = ConsoleHelper()
    helper.enable_ctrl_c_handler()

    console.clear_screen(cursor_home=True)
    console_size = console.get_console_size()
    row, col = console.cursor_current_position()
    console.set_viewport(1,console_size[0]-1)
    print(f'Console size: {console_size}, cur pos: {row},{col}')
    console.print_line_seperator('Test cursor visibility', 40)
    # print('Test cursor visibility...')
    for setting in CursorVisibility:
        console.cursor_visibility = setting
        console.debug_display_cursor_location()
        console.print_with_wait(f'CURSOR: {setting}', 2, eol=' ')
        print()
    console.clear_screen()

    console.print_line_seperator('Test cursor shape...')
    for shape in CursorShape:
        console.cursor_shape = shape
        console.debug_display_cursor_location()
        console.print_with_wait(f'CURSOR: {shape}', 2, eol = ' ')
        print()
    console.clear_screen()

    console.cursor_shape = CursorShape.STEADY_BLOCK            
    console.display_status('Test Rows...')
    for row in range(1, console_size[0]+1):
        console.print_at(row, 60, f'Row {row}', eol='')
    console.cursor_move(row=1,column=1)
    console.print_with_wait(f'Console size: {console_size} and current position: {row},{col}',3)
    console.cursor_move(5,1)
    print(f'Look at the beautiful {console.cwrap("blue",ConsoleControl.CBLUE)} sky')
    console.debug_display_cursor_location(f'After {console.cwrap("blue",ConsoleControl.CBLUE)} sky')
    time.sleep(3)

    print('Check cursor positioning...')
    console.print_at(10, 5, "Should print at  location 10,5 xxxxxxx", eol='')
    console.debug_display_cursor_location()
    time.sleep(3)
    console.cursor_left(7)

    console.clear_to_EOL()
    console.debug_display_cursor_location(f"Clear to {console.cwrap('EOL',ConsoleControl.CGREEN)}")
    time.sleep(3)

    print('abc', end='')
    console.debug_display_cursor_location()
    time.sleep(3)

    console.clear_to_BOL()
    console.debug_display_cursor_location(f"Clear to {console.cwrap('BOL',ConsoleControl.CGREEN)}")
    time.sleep(3)

    console.clear_to_BOS()
    console.debug_display_cursor_location(f"Clear to {console.cwrap('BOS',ConsoleControl.CGREEN)}")
    time.sleep(3)

    console.cursor_move(12,1)
    console.debug_display_cursor_location( "Moved to 12,1")
    time.sleep(3)

    console.clear_to_EOS()
    console.debug_display_cursor_location(f"Clear to {console.cwrap('EOS',ConsoleControl.CGREEN)}")
    time.sleep(3)

    console.clear_screen()
    print('Check scrolling...')
    for row in range(1, 50):
        print(f'Row {row}')    
        if row % 5 == 0:
            console.debug_display_cursor_location('Scrolling...')
            time.sleep(.5)

    console.set_viewport()
    console.cursor_move(console_size[0],1)
    console.clear_to_EOL()

    console.cursor_move(0,0)
    console._dump_color_palette()

    console.cursor_shape = CursorShape.DEFAULT
    print("End of ConsoleHelper demo.")

def console_input_helper_demo():
    console = ConsoleHelper()
    console_input = ConsoleInputHelper()

    test_name = console.cwrap('Input with Timeout', ConsoleControl.CYELLOW)    
    print(f'{test_name}: default response is y, timeout 3 secs...')
    resp = console_input.get_input_with_timeout('Test prompt (y/n) > ', console_input.YES_NO_RESPONSE, default='y', timeout_secs=3)
    print(f'  returns: {resp}')
    test_name = console.cwrap('Wait with Timeout', ConsoleControl.CYELLOW)
    print(f'\n{test_name}: Wait 5 seconds, or press enter to abort wait')
    console_input.wait_with_bypass(5)

    print("End of ConsoleInputHelper demo.")

def message_box_demo():
    import dt_tools.console.msgbox as msgbox
    import tkinter as tk

    console = ConsoleHelper()

    print('Alert box (no timeout)')
    resp = msgbox.alert('This is an alert box', 'ALERT no timeout')
    print(f'  returns: {console.cwrap(resp, ConsoleControl.CGREEN)}')

    print('Alert box (with timeout, 3 sec)')
    resp = msgbox.alert('This is an alert box', 'ALERT w/Timeout', timeout=3000)
    print(f'  returns: {console.cwrap(resp, ConsoleControl.CGREEN)}')

    txt = ''
    for k,v in tk.__dict__.items():
        if not k.startswith('_') and isinstance(v, int):
            txt += f'{k:20} {v}\n'
    
    print('Alert box (multi-line)')
    msgbox.used_font_family = msgbox.MONOSPACE_FONT_FAMILY
    msgbox.used_font_size = msgbox.MONOSPACE_FONT_SIZE    
    resp = msgbox.alert(txt,"ALERT-MULTILINE (no timeout)")
    print(f'  returns: {console.cwrap(resp, ConsoleControl.CGREEN)}')
    
    msgbox.used_font_family = msgbox.PROPORTIONAL_FONT_FAMILY
    msgbox.used_font_size = msgbox.PROPORTIONAL_FONT_SIZE
    print('Confirmation box (no timeout)')    
    resp = msgbox.confirm('this is a confirm box, no timeout', "CONFIRM")
    print(f'  returns: {console.cwrap(resp, ConsoleControl.CGREEN)}')
    
    print('Confirmation box (3 sec timeout)')    
    resp = msgbox.confirm('this is a confirm box, 3 sec timeout', "CONFIRM", timeout=3000)
    print(f'  returns: {console.cwrap(resp, ConsoleControl.CGREEN)}')
    
    print('Prompt box (no timeout)')    
    resp = msgbox.prompt('This is a prompt box', 'PROMPT', 'default')
    print(f'  returns: {console.cwrap(resp, ConsoleControl.CGREEN)}')
    
    print('Prompt box (3 sec timeout)')    
    resp = msgbox.prompt('This is a prompt box', 'PROMPT (3 sec timeout)', 'default', timeout=3000)
    print(f'  returns: {console.cwrap(resp, ConsoleControl.CGREEN)}')
    
    print('Password box (no timeout)')    
    resp = msgbox.password('This is a password box', 'PASSWORD', 'SuperSecretPassword')
    print(f'  returns: {console.cwrap(resp, ConsoleControl.CGREEN)}')

    print("End of MsgBox demo.")


def progress_bar_demo():
    from dt_tools.console.progress_bar import ProgressBar
    
    print('Progress bar...')
    pbar = ProgressBar("Test bar", bar_length=40, max_increments=50, show_elapsed=False)
    for incr in range(1,51):
        pbar.display_progress(incr, f'incr [{incr}]')
        time.sleep(.15)    

    print('\nProgress bar with elapsed time...')
    pbar = ProgressBar("Test bar", bar_length=40, max_increments=50, show_elapsed=True)
    for incr in range(1,51):
        pbar.display_progress(incr, f'incr [{incr}]')
        time.sleep(.15)
    print("End of ProgressBar demo.")


def spinner_demo():
    from dt_tools.console.spinner import Spinner, SpinnerType
    for spinner_type in SpinnerType:
        spinner = Spinner(caption=spinner_type, spinner=spinner_type, show_elapsed=True)
        spinner.start_spinner()
        for cnt in range(1,20):
            time.sleep(.25)
        spinner.stop_spinner()
    print("End of Spinner demo.")


if __name__ == '__main__':
    DEMOS = {
        "ConsoleHelper": console_helper_demo,
        "ConsoleInputHelper": console_input_helper_demo,
        "MessageBox": message_box_demo,
        "ProgressBar": progress_bar_demo,
        "Spinner": spinner_demo
    }

    console = ConsoleHelper()
    console_input = ConsoleInputHelper()
    for name, demo_func in DEMOS.items():
        demo_name = console.cwrap(name, ConsoleControl.CYELLOW)
        resp = console_input.get_input_with_timeout(f'Demo {demo_name} Functions (y/n) > ', 
                                                console_input.YES_NO_RESPONSE, default='n', 
                                                timeout_secs=10).lower()
        if resp == 'y':
            demo_func()
            print()

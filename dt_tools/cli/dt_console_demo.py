import time

import dt_tools.console.console_helper as helper
from dt_tools.console.console_helper import (
    ColorBG,
    ColorFG,
    ColorStyle,
    ConsoleHelper,
    ConsoleInputHelper,
    CursorShape,
    _CursorAttribute,
)


def console_helper_demo():
    console = ConsoleHelper()
    cih = ConsoleInputHelper()

    helper.enable_ctrl_c_handler()

    wait_seconds = 2

    console.clear_screen(cursor_home=True)
    console_size = console.get_console_size()
    row, col = console.cursor_current_position()
    console.set_viewport(1,console_size[0]-1)
    console.print_with_wait(f'Console size: {console_size}, cur pos: {row},{col}', wait_seconds, eol='\n\n')
    console.cursor_save_position()

    console.print_line_seperator('Test color attributes', 40)
    color_code = ConsoleHelper().color_code(ColorStyle.ITALIC, ColorFG.RED, ColorBG.WHITEBG)
    token = ConsoleHelper().cwrap('string', color_code)
    print(f'This {token} is Red Italic on White BG')
    print(f'This {ConsoleHelper().cwrap("string", ColorFG.GREEN)} is Green')
    print(f'This {ConsoleHelper().cwrap("string", ColorFG.RED)} is Red')
    print(f'This {ConsoleHelper().cwrap("string", ColorFG.RED, None, ColorStyle.ITALIC)} is Italic Red')
    print(f'This {ConsoleHelper().cwrap("string", ColorFG.RED, None, ColorStyle.BOLD)} is Bold Red\n')
    cih.get_input_with_timeout('Press ENTER to continue', timeout_secs=10)
    
    console.cursor_restore_position()
    console.clear_to_EOS()

    console.print_line_seperator('Test cursor attributes', 40)
    for attr in _CursorAttribute:
        console.cursor_attribute = attr
        console.debug_display_cursor_location()
        console.print_with_wait(f'CURSOR: {attr} ', wait_seconds, eol='')
        print()
    print()
    cih.get_input_with_timeout('Press ENTER to continue', timeout_secs=10)
    console.cursor_restore_position()
    console.clear_to_EOS()

    console.print_line_seperator('Test cursor shape...', 40)
    for shape in CursorShape:
        console.cursor_shape = shape
        console.debug_display_cursor_location()
        console.print_with_wait(f'CURSOR: {shape}', wait_seconds, eol = ' ')
        print()
    cih.get_input_with_timeout('Press ENTER to continue', timeout_secs=10)
    console.clear_screen()

    console.cursor_shape = CursorShape.STEADY_BLOCK            
    console.display_status('Test Rows...')
    for row in range(1, console_size[0]+1):
        console.print_at(row, 60, f'Row {row}', eol='')
    console.cursor_move(row=1,column=1)
    console.print_with_wait(f'Console size: {console_size} and current position: {row},{col}', wait_seconds)
    console.cursor_move(5,1)
    print(f'Look at the beautiful {console.cwrap("blue",ColorFG.BLUE)} sky')
    console.debug_display_cursor_location(f'After {console.cwrap("blue",ColorFG.BLUE)} sky')
    time.sleep(wait_seconds)

    print('Check cursor positioning...')
    console.print_at(10, 5, "Should print at  location 10,5 xxxxxxx", eol='')
    console.debug_display_cursor_location()
    time.sleep(wait_seconds)
    console.cursor_left(7)

    console.clear_to_EOL()
    console.debug_display_cursor_location(f"Clear to {console.cwrap('EOL',ColorFG.GREEN)}")
    time.sleep(wait_seconds)

    print('abc', end='')
    console.debug_display_cursor_location()
    time.sleep(wait_seconds)

    console.clear_to_BOL()
    console.debug_display_cursor_location(f"Clear to {console.cwrap('BOL',ColorFG.GREEN)}")
    time.sleep(wait_seconds)

    console.clear_to_BOS()
    console.debug_display_cursor_location(f"Clear to {console.cwrap('BOS',ColorFG.GREEN)}")
    time.sleep(wait_seconds)

    console.cursor_move(12,1)
    console.debug_display_cursor_location( "Moved to 12,1")
    time.sleep(wait_seconds)

    console.clear_to_EOS()
    console.debug_display_cursor_location(f"Clear to {console.cwrap('EOS',ColorFG.GREEN)}")
    time.sleep(wait_seconds)

    console.print_with_wait(f'Console size: {console_size}, cur pos: {row},{col}', wait_seconds, eol='\n\n')
    console.set_viewport(2,console_size[0]-1)

    console.clear_screen()
    console.print_line_seperator('Check scrolling...', 40)
    for row in range(1, 50):
        print(f'Row {row}')    
        if row % 5 == 0:
            console.debug_display_cursor_location('Scrolling...')
            time.sleep(.5)
    cih.get_input_with_timeout('Press ENTER to continue', timeout_secs=10)

    console.set_viewport()
    console.clear_screen()
    console.print_line_seperator('Display color palette, codes are [style,fg,bg]...', 40)
    print('')
    time.sleep(wait_seconds)
    console._display_color_palette()

    console.cursor_shape = CursorShape.DEFAULT
    print(f"End of {console.cwrap('ConsoleHelper', ColorFG.YELLOW)} demo.")

def console_input_helper_demo():    
    console = ConsoleHelper()
    console_input = ConsoleInputHelper()
    print()
    test_name = console.cwrap('Input with Timeout', ColorStyle.ITALIC)    
    print(f'{test_name}: default response is y, timeout 3 secs...')
    resp = console_input.get_input_with_timeout('Test prompt (y/n) > ', console_input.YES_NO_RESPONSE, default='y', timeout_secs=3)
    print(f'  returns: {resp}')
    test_name = console.cwrap('Wait with Timeout', ColorStyle.ITALIC)
    print(f'\n{test_name}: Wait 5 seconds, or press enter to abort wait')
    console_input.wait_with_bypass(5)
    
    print(f"End of {console.cwrap('ConsoleInputHelper', ColorFG.YELLOW)} demo.")

def message_box_demo():
    import tkinter as tk

    import dt_tools.console.msgbox as msgbox

    console = ConsoleHelper()

    print('Alert box (no timeout)')
    resp = msgbox.alert('This is an alert box', 'ALERT no timeout')
    print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')

    print('Alert box (with timeout, 3 sec)')
    resp = msgbox.alert('This is an alert box', 'ALERT w/Timeout', timeout=3000)
    print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')

    txt = ''
    for k,v in tk.__dict__.items():
        if not k.startswith('_') and isinstance(v, int):
            txt += f'{k:20} {v}\n'
    
    print('Alert box (multi-line)')
    msgbox._used_font_family = msgbox.MB_FontFamily.MONOSPACE
    msgbox._used_font_size = msgbox.MB_FontSize.MONOSPACE
    resp = msgbox.alert(txt,"ALERT-MULTILINE (no timeout)")
    print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    msgbox._used_font_family = msgbox.MB_FontFamily.PROPORTIONAL
    msgbox._used_font_size = msgbox.MB_FontSize.PROPORTIONAL
    print('Confirmation box (no timeout)')    
    resp = msgbox.confirm('this is a confirm box, no timeout', "CONFIRM")
    print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    print('Confirmation box (3 sec timeout)')    
    resp = msgbox.confirm('this is a confirm box, 3 sec timeout', "CONFIRM", timeout=3000)
    print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    print('Prompt box (no timeout)')    
    resp = msgbox.prompt('This is a prompt box', 'PROMPT', 'default')
    print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    print('Prompt box (3 sec timeout)')    
    resp = msgbox.prompt('This is a prompt box', 'PROMPT (3 sec timeout)', 'default', timeout=3000)
    print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    print('Password box (no timeout)')    
    resp = msgbox.password('This is a password box', 'PASSWORD', 'SuperSecretPassword')
    print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')

    print(f"End of {console.cwrap('MessageBox', ColorFG.YELLOW)} demo.")


def progress_bar_demo():
    from dt_tools.console.progress_bar import ProgressBar
    
    sleep_time = .15
    print('Progress bar...')
    pbar = ProgressBar("Test bar", bar_length=40, max_increments=50, show_elapsed=False)
    for incr in range(1,51):
        pbar.display_progress(incr, f'incr [{incr}]')
        time.sleep(sleep_time)    

    print('\nProgress bar with elapsed time...')
    pbar = ProgressBar("Test bar", bar_length=40, max_increments=50, show_elapsed=True)
    for incr in range(1,51):
        pbar.display_progress(incr, f'incr [{incr}]')
        time.sleep(sleep_time)
    print(f"End of {console.cwrap('ProgressBar', ColorFG.YELLOW)} demo.")


def spinner_demo():
    from dt_tools.console.spinner import Spinner, SpinnerType

    sleep_time = .25
    for spinner_type in SpinnerType:
        spinner = Spinner(caption=spinner_type, spinner=spinner_type, show_elapsed=True)
        spinner.start_spinner()
        for cnt in range(1,20):
            time.sleep(sleep_time)
        spinner.stop_spinner()
    print(f"End of {console.cwrap('Spinner',ColorFG.YELLOW)} demo.")


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
    console.clear_screen()
    for name, demo_func in DEMOS.items():
        demo_name = console.cwrap(name, ColorFG.YELLOW)
        resp = console_input.get_input_with_timeout(f'Demo {demo_name} Functions (y/n) > ', 
                                                console_input.YES_NO_RESPONSE, default='n', 
                                                timeout_secs=10).lower()
        if resp == 'y':
            demo_func()
            print()

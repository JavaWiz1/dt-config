from dt_tools.console.console_helper import ColorFG
from dt_tools.console.console_helper import ConsoleHelper as console
from dt_tools.os.os_helper import OSHelper

import tkinter as tk

import dt_tools.console.msgbox as msgbox

def demo():
    OSHelper.enable_ctrl_c_handler()

    console.print('')
    console.print_line_seperator('Alert box (no timeout)', 40)

    resp = msgbox.alert('This is an alert box', 'ALERT no timeout')
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')

    console.print('')
    console.print_line_seperator('Alert box (w/timeout, 3 sec)', 40)
    resp = msgbox.alert('This is an alert box', 'ALERT w/Timeout', timeout=3000)
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')

    txt = ''
    for k,v in tk.__dict__.items():
        if not k.startswith('_') and isinstance(v, int):
            txt += f'{k:20} {v}\n'
    
    console.print('')
    console.print_line_seperator('Alert box (multi-line)', 40)
    msgbox._used_font_family = msgbox.MB_FontFamily.MONOSPACE
    msgbox._used_font_size = msgbox.MB_FontSize.MONOSPACE
    resp = msgbox.alert(txt,"ALERT-MULTILINE (no timeout)")
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    console.print('')
    console.print_line_seperator('Confirmation box (no timeout)', 40)
    msgbox._used_font_family = msgbox.MB_FontFamily.PROPORTIONAL
    msgbox._used_font_size = msgbox.MB_FontSize.PROPORTIONAL
    resp = msgbox.confirm('this is a confirm box, no timeout', "CONFIRM")
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    console.print('')
    console.print_line_seperator('Confirmation box (3 sec timeout)', 40)
    resp = msgbox.confirm('this is a confirm box, 3 sec timeout', "CONFIRM", timeout=3000)
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    console.print('')
    console.print_line_seperator('Prompt box (no timeout)', 40)
    resp = msgbox.prompt('This is a prompt box', 'PROMPT', 'default')
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    console.print('')
    console.print_line_seperator('Prompt box (3 sec timeout)', 40)
    resp = msgbox.prompt('This is a prompt box', 'PROMPT (3 sec timeout)', 'default', timeout=3000)
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    console.print('')
    console.print_line_seperator('Password box (no timeout)', 40)
    resp = msgbox.password('This is a password box', 'PASSWORD', 'SuperSecretPassword')
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')

    console.print('')
    console.print(f"End of {console.cwrap('MessageBox', ColorFG.YELLOW)} demo.")


if __name__ == '__main__':
    demo()
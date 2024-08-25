from dt_tools.console.console_helper import ColorFG, TextStyle
from dt_tools.console.console_helper import ConsoleHelper as console
from dt_tools.console.console_helper import ConsoleInputHelper as console_input
from dt_tools.os.os_helper import OSHelper
def demo():    
    OSHelper.enable_ctrl_c_handler()
    timeout = 10
    console.print('')
    console.print_line_seperator('ConsoleInputHelper Demo', 40)
    console.print('')
    test_name = console.cwrap('Input with Timeout', TextStyle.ITALIC)    
    console.print(f'{test_name}: default response is y, timeout {timeout} secs...')
    resp = console_input.get_input_with_timeout('Test prompt (y/n) > ', console_input.YES_NO_RESPONSE, default='y', timeout_secs=timeout)
    console.print(f'  returns: {resp}')

    test_name = console.cwrap('Wait with Timeout', TextStyle.ITALIC)
    console.print(f'\n{test_name}: Wait {timeout} seconds, or press ENTER to abort wait', eol='')
    if console_input.wait_with_bypass(timeout):
        console.print('  Prompt timed out.')
    else:
        console.print('  User aborted wait')
    console.print('')
    console.print(f"End of {console.cwrap('ConsoleInputHelper', ColorFG.YELLOW)} demo.")

if __name__ == '__main__':
    demo()
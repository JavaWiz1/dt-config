import os
import signal
import sys
import time
from enum import Enum
from typing import List, Tuple, Union

from loguru import logger as LOGGER

if sys.platform == "win32":
    import msvcrt
    from ctypes import byref, windll, wintypes  # noqa: F401

# TODO:
#   update _output_to_terminal to allow for printing to stderr OR stdout (default)

class ConsoleControl:
    ESC='\u001b'
    BELL='\a'

    # Console Colors to be used with cwrap()
    CEND      = f'{ESC}[0m'
    CBOLD     = f'{ESC}[1m'
    CITALIC   = f'{ESC}[3m'
    CURL      = f'{ESC}[4m'
    CBLINK    = f'{ESC}[5m'
    CBLINK2   = f'{ESC}[6m'
    CSELECTED = f'{ESC}[7m'

    CBLACK  = f'{ESC}[30m'
    CRED    = f'{ESC}[31m'
    CGREEN  = f'{ESC}[32m'
    CYELLOW = f'{ESC}[33m'
    CBLUE   = f'{ESC}[34m'
    CVIOLET = f'{ESC}[35m'
    CBEIGE  = f'{ESC}[36m'
    CWHITE  = f'{ESC}[37m'

    CBLACKBG  = f'{ESC}[40m'
    CREDBG    = f'{ESC}[41m'
    CGREENBG  = f'{ESC}[42m'
    CYELLOWBG = f'{ESC}[43m'
    CBLUEBG   = f'{ESC}[44m'
    CVIOLETBG = f'{ESC}[45m'
    CBEIGEBG  = f'{ESC}[46m'
    CWHITEBG  = f'{ESC}[47m'

    CGREY    = f'{ESC}[90m'
    CRED2    = f'{ESC}[91m'
    CGREEN2  = f'{ESC}[92m'
    CYELLOW2 = f'{ESC}[93m'
    CBLUE2   = f'{ESC}[94m'
    CVIOLET2 = f'{ESC}[95m'
    CBEIGE2  = f'{ESC}[96m'
    CWHITE2  = f'{ESC}[97m'

    CGREYBG    = f'{ESC}[100m'
    CREDBG2    = f'{ESC}[101m'
    CGREENBG2  = f'{ESC}[102m'
    CYELLOWBG2 = f'{ESC}[103m'
    CBLUEBG2   = f'{ESC}[104m'
    CVIOLETBG2 = f'{ESC}[105m'
    CBEIGEBG2  = f'{ESC}[106m'
    CWHITEBG2  = f'{ESC}[107m'

    # Cursor Control
    CURSOR_HIDE = f'{ESC}[?25l'
    CURSOR_SHOW = f'{ESC}[?25h'
    CURSOR_CLEAR_EOS = f'{ESC}[0J'
    CURSOR_CLEAR_BOS = f'{ESC}[1J'
    CURSOR_CLEAR_LINE = f'{ESC}[2K'
    CURSOR_CLEAR_EOL = f'{ESC}[0K'
    CURSOR_CLEAR_BOL = f'{ESC}[1K'
    CURSOR_CLEAR_SCREEN = f'{ESC}[2J'

    # Window Control
    WINDOW_HIDE = f'{ESC}[2t'
    WINDOW_SHOW = f'{ESC}[1t'
    WINDOW_TITLE = f'{ESC}]2;%title%\a'

class CursorVisibility(Enum):
    NON_BLINKING = f'{ConsoleControl.ESC}[?12l'
    BLINKING = f'{ConsoleControl.ESC}[?12h'
    HIDE = f'{ConsoleControl.ESC}[?25l'
    SHOW = f'{ConsoleControl.ESC}[?25h'

class CursorShape(Enum):
    DEFAULT = f'{ConsoleControl.ESC}[0 q'
    BLINKING_BLOCK = f'{ConsoleControl.ESC}[1 q'
    STEADY_BLOCK = f'{ConsoleControl.ESC}[2 q'
    BLINKING_UNDERLINE = f'{ConsoleControl.ESC}[3 q'
    STEADY_UNDERLINE = f'{ConsoleControl.ESC}[4 q'
    BLINKING_BAR = f'{ConsoleControl.ESC}[5 q'
    STEADY_BAR = f'{ConsoleControl.ESC}[6 q'

class Format:
    end = f'{ConsoleControl.ESC}[0m'
    underline = f'{ConsoleControl.ESC}[4m'
    bold = f'{ConsoleControl.ESC}[1m'
    spacer = ' ͏'

# https://docs.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences
# https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
# https://invisible-island.net/xterm/ctlseqs/ctlseqs.html

# ==========================================================================================================
class ConsoleHelper():
    """
    Class to assist with console output.  Methods to:
    - Set cursor shape and visibility
    - Set console window title
    - Clear functions
    - Cursor control (up, down, left, right, move to location,...)
    """
    LAST_CONSOLE_STR: str = None
    CC: ConsoleControl

    def _output_to_terminal(cls, token: str, eol:str=''):
        print(token, end=eol, flush=True)
        cls.LAST_CONSOLE_STR = token

    def cursor_visibility(cls, token: CursorVisibility):
        cls._output_to_terminal(token.value)
    cursor_visibility = property(None, cursor_visibility)

    def cursor_shape(cls, token: CursorShape):
        cls._output_to_terminal(token.value)
    cursor_shape = property(None, cursor_shape)
    
    def console_hide(cls):
        """Minimize console/terminal window"""
        cls._output_to_terminal(ConsoleControl.WINDOW_HIDE)
    
    def console_show(cls):
        """Restore console/terminal window"""
        cls._output_to_terminal(ConsoleControl.WINDOW_SHOW)
        
    def console_title(cls, title: str):
        title_cmd = ConsoleControl.WINDOW_TITLE.replace("%title%", title)
        print(title_cmd)
        cls._output_to_terminal(title_cmd)

    def cursor_off(cls):
        """Turn console cursor off"""
        cls._output_to_terminal(ConsoleControl.CURSOR_HIDE)

    def cursor_on(cls):
        """Turn console cursor on"""
        cls._output_to_terminal(ConsoleControl.CURSOR_SHOW)

    def clear_to_EOS(cls):
        """Clear from cursor to end of screen"""
        cls._output_to_terminal(ConsoleControl.CURSOR_CLEAR_EOS)

    def clear_to_BOS(cls):
        """Clear from cursor to beginning of screen"""
        cls._output_to_terminal(ConsoleControl.CURSOR_CLEAR_BOS)

    def clear_line(cls):
        """Clear current line"""
        cls._output_to_terminal(ConsoleControl.CURSOR_CLEAR_LINE)

    def clear_to_EOL(cls):
        """Clear from cursor to end of line"""
        cls._output_to_terminal(ConsoleControl.CURSOR_CLEAR_EOL)
    
    def clear_to_BOL(cls):
        """Clear from cursor to beginning of line"""
        cls._output_to_terminal(ConsoleControl.CURSOR_CLEAR_BOL)

    def clear_screen(cls, cursor_home: bool = True):
        """
        Clear screen and home cursor
        optionally leave cursor where it is - cursor_home = False
        """
        cls._output_to_terminal(ConsoleControl.CURSOR_CLEAR_SCREEN)
        if cursor_home:
            cls.cursor_move(1, 1)

    def cursor_up(cls, steps: int = 1):
        """Move cursor up (steps) rows"""
        cls._output_to_terminal(f'{ConsoleControl.ESC}[{steps}A')

    def cursor_down(cls, steps: int = 1):
        """Move cursor down (steps) rows"""
        cls._output_to_terminal(f'{ConsoleControl.ESC}[{steps}B')

    def cursor_right(cls, steps: int = 1):
        """Move cursor right (steps) columns"""
        cls._output_to_terminal(f'{ConsoleControl.ESC}[{steps}C')

    def cursor_left(cls, steps: int = 1):
        """Move cursor left (steps) columns"""
        cls._output_to_terminal(f'{ConsoleControl.ESC}[{steps}D')

    def cursor_scroll_up(cls, steps: int = 1):
        """Scroll screen contents up (steps) rows"""
        cls._output_to_terminal(f'{ConsoleControl.ESC}[{steps}S')

    def cursor_scroll_down(cls, steps: int = 1):
        """Scroll screen contents down (steps) rows"""
        cls._output_to_terminal(f'{ConsoleControl.ESC}[{steps}T')


    def cursor_move(cls, row:int = -1, column:int = -1) -> bool:
        """Move console cursor to position row, column"""
        cur_row, cur_col = cls.cursor_current_position()
        if  row <= 0:
            row = int(cur_row)
        if column <= 0:
            column = int(cur_col)
        max_rows, max_columns = cls.get_console_size()
        if row <= 0 or column <= 0:
            LOGGER.error('cursor_move - row/column must be > 0')
            return False
        if column > max_columns or row > max_rows:
            LOGGER.error((f'cursor_move - row > {max_rows} or col > {max_columns}'))
            return False
        
        cls._output_to_terminal(f"{ConsoleControl.ESC}[%d;%dH" % (row, column))    
        return True

    def print_at(cls, row: int, col: int, msg: str, eol='') -> bool:
        """
        Write string at position row/column, optionally set end of line
        """
        if cls.cursor_move(row, col):
            cls._output_to_terminal(msg, eol)
            return True
        return False
        
    def cursor_current_position(cls) -> Tuple[int, int]:
        """Return console cursor Row and Column position"""
        if sys.platform == "win32":
            sys.stdout.write("\x1b[6n")
            sys.stdout.flush()
            buffer = bytes()
            while msvcrt.kbhit():
                buffer += msvcrt.getch()
            hex_loc = buffer.decode().replace('\x1b[','').replace('R','')
            # print(hex_loc)
            token = hex_loc.split(';')
            row = token[0]
            col = token[1]
        else:
            row, col = os.popen('stty size', 'r').read().split()
        
        return int(row), int(col)

    def cursor_save_position(cls):
        '''Save cursor position, can be restored with restore_position() call'''
        cls._output_to_terminal(f'{ConsoleControl.ESC}[s')

    def cursor_restore_position(cls):
        '''Restore cursor position, saved with the save_position() call'''
        cls._output_to_terminal(f'{ConsoleControl.ESC}[u')

    def get_console_size(cls) -> Tuple[int, int]:
        """Return console size in rows and columns"""
        rows = int(os.getenv('LINES', -1))
        columns = int(os.getenv('COLUMNS', -1))
        if rows <= 0 or columns <= 0:
            size = os.get_terminal_size()
            rows = int(size.lines)
            columns = int(size.columns)

        return rows, columns

    def set_viewport(cls, start_row: int = None, end_row: int = None):
        """Set console writable area to start_row / end_row.  Default is whole screen."""
        max_row, max_col = cls.get_console_size()
        if start_row is None:
            start_row = 1
        if end_row is None:
            end_row = int(max_row)
        if start_row < 1 or start_row > end_row or start_row > max_row:
            raise ValueError(f"set_viewport(): Invalid start row: {start_row}")
        if end_row > max_row:
            raise ValueError(f'set_viewport(): Invalid end row: {end_row}')

        cls._output_to_terminal(f'{ConsoleControl.ESC}[{start_row};{end_row}r')

    def display_status(cls, msg, wait: int = 0):
        """Display status message on last row of screen"""
        max_row, max_col = cls.get_console_size()

        save_row, save_col = cls.cursor_current_position()
        cls.print_at(max_row, 1, f'{msg}', eol='')     
        cls.clear_to_EOL()
        cls.cursor_move(save_row, save_col)   
        if wait > 0:
            time.sleep(wait)

    def sprint_line_seperator(cls, text: str = '', length: int = -1) -> str:
        """
        Return string underline (seperator) with optional text

        Parameters:
          text:   string to display (default empty string)
          length: length of underline (default console width)
        """
        if length < 0:
            row, col = cls.cursor_current_position()
            max_rows, max_cols = cls.get_console_size()
            length = max_cols - col
        fill_len = length - len(text)
        line_out = f'{Format.underline}{text}{" "*(fill_len-1)}{Format.spacer}{Format.end}'
        return line_out

    def print_line_seperator(cls, title: str = '', length: int = -1):
        """
        Print underline (seperator) with optional text

        Parameters:
          text:   string to display (default empty string)
          length: length of underline (default console width)
        """
        print(cls.sprint_line_seperator(title, length))

    def debug_display_cursor_location(cls, msg:str = ""):
        cls.display_status(f'Cursor: {str(ConsoleHelper().cursor_current_position())}  {msg}')

    def print_with_wait(cls, msg: str, wait: float = 0.0, end='\n'):
        print(msg, end=end, flush=True)
        if wait > 0:
            time.sleep(wait)

    def cwrap(cls, in_str: str, color: str) -> str:
        """Wrap string with color codes for output to console"""
        return f'{color}{in_str}{ConsoleControl.CEND}'

    def _dump_color_palette(cls):
        x = 0
        for i in range(24):
            colors = ""
            for j in range(5):
                code = str(x+j)
                # colors = colors + f"{ConsoleControl.ESC}[" + code + f"m\{ConsoleControl.ESC}[" + code + f"m{ConsoleControl.ESC}[0m "
                colors += f'{ConsoleControl.ESC}[{code}m\\{ConsoleControl.ESC}[{code}m{ConsoleControl.ESC}[0m '
            print(colors)
            x = x + 5    

# ==========================================================================================================
class ConsoleInputHelper():
    """
    Helper for getting input from the console
    """

    YES_NO_RESPONSE = ['Y','y', 'N', 'n']

    def get_input_with_timeout(cls, prompt: str, valid_responses: list = [],  
                               default: str = None, timeout_secs: int = -1, 
                               parms_ok: bool = False) -> Union[str, Tuple[str, list]]:
        """
        Prompt for input with a timer

        parameters:

          prompt          : text to display
          valid_responses : string or list of valid responses (default None)
          timeout_secs    : seconds before prompt times out (default -1 = no timeout)
          default         : default value returned (default None)
          parms_ok        : allow parameters in response when checking valid responses (default False)

        parms_ok means if valid responses are y|n, user could respond y 123 or y abc and it would still be valid.
        """
        response: str = ''
        chk_response = ''
        response_params: List = None
        valid_input = False
        while not valid_input:
            if timeout_secs < 0:
                response = input(prompt)
            else:
                try:
                    if sys.platform == "win32":
                        response = cls._input_with_timeout_win(prompt, timeout_secs, default)
                    else:
                        response = cls._input_with_timeout_nix(prompt, timeout_secs, default)
                except TimeoutError:
                    response = default
                    valid_input = True
            
            if not parms_ok:
                chk_response = response
                response_params = None
            else:
                token = response.split()
                if len(token) > 0:
                    chk_response = token[0]
                    response_params = token[1:]
                else:
                    chk_response = response
                    response_params = None

            if not valid_responses:
                LOGGER.trace('no valid responses to check')
                valid_input = True
            elif chk_response in valid_responses:
                    valid_input = True

        if parms_ok:
            return chk_response, response_params
        
        return chk_response

    def wait_with_bypass(cls, secs: int):
        """Timed wait.  Wait for number of seconds and Continue"""
        cls.get_input_with_timeout("", timeout_secs=secs)
        return

    def _input_with_timeout_win(cls, prompt: str, timeout_secs: int,  default: str= None) -> str:
        LOGGER.trace("_input_with_timeout_win()")
        sys.stdout.write(prompt)
        sys.stdout.flush()
        timer = time.monotonic
        endtime = timer() + timeout_secs
        result = []
        while timer() < endtime:
            if msvcrt.kbhit():
                result.append(msvcrt.getwche()) #XXX can it block on multibyte characters?
                endtime = timer() + timeout_secs  # Reset timer each time a key is pressed.
                if result[-1] == '\r':   #XXX check what Windows returns here
                    print()
                    return ''.join(result[:-1])
            time.sleep(0.04) # just to yield to other processes/threads
        if result:
            print()
            return ''.join(result)
        elif default:
            print(default)
        raise TimeoutError('Time Expired.')

    def _alarm_handler(signum, frame):
        raise TimeoutError('time expired.')

    def _input_with_timeout_nix(prompt: str, timeout_secs: int, default: str) -> str:
        # set signal handler for *nix systems
        LOGGER.trace("_input_with_timeout_nix()")
        signal.signal(signal.SIGALRM, ConsoleInputHelper._alarm_handler)
        signal.alarm(timeout_secs) # produce SIGALRM in `timeout` seconds

        response = default
        try:
            response = input(prompt)
        finally:
            signal.alarm(0) # cancel alarm
            return response

# -------------------------------------------------------------------------------------------
# Miscellaneous Routines
# -------------------------------------------------------------------------------------------
def pad_r(in_str: str, length: int, pad_char: str = ' '):
    """Pad input string (to the end) to specified length with spaces."""
    if len(pad_char) > 1:
        raise ValueError('Padding character should only be 1 character in length')
    
    pad_len = length - len(in_str)
    if pad_len > 0:
        return f'{in_str}{pad_char*pad_len}'
    return in_str    

def pad_l(in_str: str, length: int, pad_char: str = ' '):
    """Pad input string (from the beginning) to specified length with spaces."""
    if len(pad_char) > 1:
        raise ValueError('Padding character should only be 1 character in length')
    
    pad_len = length - len(in_str)
    if pad_len > 0:
        return f'{pad_char*pad_len}{in_str}'
    return in_str    

# def cwrap(in_str: str, color: str) -> str:
#   """Wrap string with color codes for output to console"""
#   return f'{color}{in_str}{ConsoleControl.CEND}'

def disable_ctrl_c_handler() -> bool:
    """
    Disable handler for Ctrl-C checking.
    """
    success = True
    try:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
    except:  # noqa: E722
        success = False
    return success

def enable_ctrl_c_handler() -> bool:
    """
    Enable handler for Ctrl-C checking.
    If Ctrl-C occurs, user is prompted to continue or exit.
    Defaults to exit after 10 seconds.
    """
    success = True
    try:
        signal.signal(signal.SIGINT, _interrupt_handler)
    except:  # noqa: E722
        success = False
    return success

def _interrupt_handler(signum, frame):
    resp = ConsoleInputHelper().get_input_with_timeout('\nCtrl-C, Continue or Exit (c,e)? ',['C','c','E','e'], 'e', 10)
    if resp.lower() == 'e':
        os._exit(1)

# def dump_color_palette():
#     x = 0
#     for i in range(24):
#         colors = ""
#         for j in range(5):
#             code = str(x+j)
#             # colors = colors + f"{ConsoleControl.ESC}[" + code + f"m\{ConsoleControl.ESC}[" + code + f"m{ConsoleControl.ESC}[0m "
#             colors += f'{ConsoleControl.ESC}[{code}m\\{ConsoleControl.ESC}[{code}m{ConsoleControl.ESC}[0m '
#         print(colors)
#         x = x + 5    

# def debug_display_cursor_location(msg:str = ""):
#     ConsoleHelper().display_status(f'Cursor: {str(ConsoleHelper().cursor_current_position())}  {msg}')

# def print_with_wait(msg: str, wait: float = 0.0, end='\n'):
#     print(msg, end=end, flush=True)
#     if wait > 0:
#         time.sleep(wait)

if __name__ == "__main__":
    console = ConsoleHelper()
    in_help = ConsoleInputHelper()
    enable_ctrl_c_handler()
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
        console.print_with_wait(f'CURSOR: {setting}', 2, end=' ')
        print()
    console.clear_screen()

    console.print_line_seperator('Test cursor shape...')
    for shape in CursorShape:
        console.cursor_shape = shape
        console.debug_display_cursor_location()
        console.print_with_wait(f'CURSOR: {shape}', 2, end = ' ')
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
    print("That's all folks!")
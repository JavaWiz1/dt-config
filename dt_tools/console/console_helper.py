"""
Console utilities for controlling terminal screen.


Package contains two main classes for working with console windows and text.

- **ConsoleHelper**: Class to aid in console window control and text output including
    - writing to specific locations.
    - clearing portions of the screen
    - colorized output

- **ConsoleInputHelper**: Class providing input prompt with:
    - Input field editing (i.e. controlling valid input)
    - Wait time, timeout before default response is returned


Additionally, helper classes/namespaces provided:

- **ConsoleColor**: Color codes for ansi output 
    (see :func:`~dt_tools.console.console_helper.ConsoleHelper.cwrap()` function).
- **CursorShape**: Ansi codes for controlling cursor shape.

"""


import os
import signal
import sys
import time
from enum import Enum
from typing import Final, List, Tuple, Union

from loguru import logger as LOGGER

if sys.platform == "win32":
    import msvcrt
    from ctypes import byref, windll, wintypes  # noqa: F401

# TODO:
#   update _output_to_terminal to allow for printing to stderr OR stdout (default)

class _ConsoleControl:
    """Console control characters."""
    ESC: Final  = '\u001b'
    BELL: Final = '\a'
    CEND: Final = f'{ESC}[0m'

class ColorStyle:
    """Console Color styles"""
    BOLD: Final     = f'{_ConsoleControl.ESC}[1m'
    ITALIC: Final   = f'{_ConsoleControl.ESC}[3m'
    URL: Final      = f'{_ConsoleControl.ESC}[4m'
    BLINK: Final    = f'{_ConsoleControl.ESC}[5m'
    BLINK2: Final   = f'{_ConsoleControl.ESC}[6m'
    SELECTED: Final = f'{_ConsoleControl.ESC}[7m'

class ColorFG:
    """ Console font colors to be used with :func:`~dt_tools.console.console_helper.ConsoleHelper.cwrap()`."""
    BLACK: Final  = f'{_ConsoleControl.ESC}[30m'
    RED: Final    = f'{_ConsoleControl.ESC}[31m'
    GREEN: Final  = f'{_ConsoleControl.ESC}[32m'
    YELLOW: Final = f'{_ConsoleControl.ESC}[33m'
    BLUE: Final   = f'{_ConsoleControl.ESC}[34m'
    VIOLET: Final = f'{_ConsoleControl.ESC}[35m'
    BEIGE: Final  = f'{_ConsoleControl.ESC}[36m'
    WHITE: Final = f'{_ConsoleControl.ESC}[37m'

    GREY: Final    = f'{_ConsoleControl.ESC}[90m'
    RED2: Final    = f'{_ConsoleControl.ESC}[91m'
    GREEN2: Final  = f'{_ConsoleControl.ESC}[92m'
    YELLOW2: Final = f'{_ConsoleControl.ESC}[93m'
    BLUE2: Final   = f'{_ConsoleControl.ESC}[94m'
    VIOLET2: Final = f'{_ConsoleControl.ESC}[95m'
    BEIGE2: Final  = f'{_ConsoleControl.ESC}[96m'
    WHITE2: Final  = f'{_ConsoleControl.ESC}[97m'

class ColorBG:
    """Console background font colors to be used with :func:`~dt_tools.console.console_helper.ConsoleHelper.cwrap()`."""
    BLACKBG: Final  = f'{_ConsoleControl.ESC}[40m'
    REDBG: Final    = f'{_ConsoleControl.ESC}[41m'
    GREENBG: Final  = f'{_ConsoleControl.ESC}[42m'
    YELLOWBG: Final = f'{_ConsoleControl.ESC}[43m'
    BLUEBG: Final   = f'{_ConsoleControl.ESC}[44m'
    VIOLETBG: Final = f'{_ConsoleControl.ESC}[45m'
    BEIGEBG: Final  = f'{_ConsoleControl.ESC}[46m'
    WHITEBG: Final  = f'{_ConsoleControl.ESC}[47m'

    GREYBG: Final    = f'{_ConsoleControl.ESC}[100m'
    REDBG2: Final    = f'{_ConsoleControl.ESC}[101m'
    GREENBG2: Final  = f'{_ConsoleControl.ESC}[102m'
    YELLOWBG2: Final = f'{_ConsoleControl.ESC}[103m'
    BLUEBG2: Final   = f'{_ConsoleControl.ESC}[104m'
    VIOLETBG2: Final = f'{_ConsoleControl.ESC}[105m'
    BEIGEBG2: Final  = f'{_ConsoleControl.ESC}[106m'
    WHITEBG2: Final  = f'{_ConsoleControl.ESC}[107m'

class CursorShape(Enum):
    """Constants defining available cursor shapes."""
    DEFAULT = f'{_ConsoleControl.ESC}[0 q'
    BLINKING_BLOCK = f'{_ConsoleControl.ESC}[1 q'
    STEADY_BLOCK = f'{_ConsoleControl.ESC}[2 q'
    BLINKING_UNDERLINE = f'{_ConsoleControl.ESC}[3 q'
    STEADY_UNDERLINE = f'{_ConsoleControl.ESC}[4 q'
    BLINKING_BAR = f'{_ConsoleControl.ESC}[5 q'
    STEADY_BAR = f'{_ConsoleControl.ESC}[6 q'

class _FormatControls:
    """Constants for formatting strings."""
    end: Final = f'{_ConsoleControl.ESC}[0m'
    underline: Final = f'{_ConsoleControl.ESC}[4m'
    bold: Final = f'{_ConsoleControl.ESC}[1m'
    spacer: Final = ' ͏'

class _CursorAttribute(Enum):
    """Cursor control characters (Visability, Blink?)."""
    HIDE = f'{_ConsoleControl.ESC}[?25l'
    SHOW = f'{_ConsoleControl.ESC}[?25h'
    SOLID = f'{_ConsoleControl.ESC}[?12l'
    """Solid (non-blinking) Cursor"""
    BLINKING = f'{_ConsoleControl.ESC}[?12h' # Does not work (sometimes)?
    """Blinking Cursor"""

class _CursorClear:
    EOS: Final = f'{_ConsoleControl.ESC}[0J'
    """Clear to End-Of-Screen."""
    BOS: Final = f'{_ConsoleControl.ESC}[1J'
    """Clear to Beginning-Of-Screen."""
    LINE: Final = f'{_ConsoleControl.ESC}[2K'
    """Clear current line."""
    EOL: Final = f'{_ConsoleControl.ESC}[0K'
    """Clear from current position to End-Of-Line."""
    BOL: Final = f'{_ConsoleControl.ESC}[1K'
    """Clear from current position to Beginning-Of-Line."""
    SCREEN: Final = f'{_ConsoleControl.ESC}[2J'
    """Clear entire screen."""

class WindowControl:
    """Window control characters (Hide/Show, Title)."""
    WINDOW_HIDE: Final  = f'{_ConsoleControl.ESC}[2t'
    WINDOW_SHOW: Final  = f'{_ConsoleControl.ESC}[1t'
    WINDOW_TITLE: Final = f'{_ConsoleControl.ESC}]2;%title%\a'


# https://docs.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences
# https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
# https://invisible-island.net/xterm/ctlseqs/ctlseqs.html

# ==========================================================================================================
class ConsoleHelper():
    """
    Class to assist with console output.  
    
    Methods to:

        - Set cursor shape and visibility.
        - Set console window title.
        - Clear functions.
        - Cursor control (up, down, left, right, move to location,...).

    Example::
        from dt_tools.console.console_helper import ConsoleHelper, ConsoleColors

        con = ConsoleHelper()
        con.clear_screen(cursor_home=True)

        console_size = con.get_console_size()
        row, col = con.cursor_current_position()
        con.print_at(5,5, f'Console size: {console_size}, cur pos: {row},{col}', eol='\\n')
        
        token = f'Test {con.cwrap("Yellow", ConsoleColors.CYELLOW)} string')
        con.print_at(5, 10, token)
        
    """
    LAST_CONSOLE_STR: str = None

    def _cursor_attribute(cls, token: _CursorAttribute):
        cls._output_to_terminal(token.value)
    cursor_attribute = property(None, _cursor_attribute)

    def _cursor_shape(cls, token: CursorShape):
        cls._output_to_terminal(token.value)
    cursor_shape = property(None, _cursor_shape)
    
    def console_hide(cls):
        """Minimize console/terminal window"""
        cls._output_to_terminal(WindowControl.WINDOW_HIDE)
    
    def console_show(cls):
        """Restore console/terminal window"""
        cls._output_to_terminal(WindowControl.WINDOW_SHOW)
        
    def console_title(cls, title: str):
        """
        Set the console/window title.

        Arguments:
            title: String to be displayed on the title bar.
        """
        title_cmd = WindowControl.WINDOW_TITLE.replace("%title%", title)
        print(title_cmd)
        cls._output_to_terminal(title_cmd)

    def cursor_off(cls):
        cls._output_to_terminal(_CursorAttribute.HIDE.value)

    def cursor_on(cls):
        """Turn console cursor on"""
        cls._output_to_terminal(_CursorAttribute.SHOW.value)

    def clear_to_EOS(cls):
        """Clear from cursor to end of screen"""
        cls._output_to_terminal(_CursorClear.EOS)

    def clear_to_BOS(cls):
        """Clear from cursor to beginning of screen"""
        cls._output_to_terminal(_CursorClear.BOS)

    def clear_line(cls):
        """Clear current line"""
        cls._output_to_terminal(_CursorClear.LINE)

    def clear_to_EOL(cls):
        """Clear from cursor to end of line"""
        cls._output_to_terminal(_CursorClear.EOL)
    
    def clear_to_BOL(cls):
        """Clear from cursor to beginning of line"""
        cls._output_to_terminal(_CursorClear.BOL)

    def clear_screen(cls, cursor_home: bool = True):
        """
        Clear screen and home cursor.

        Keyword Arguments:
            cursor_home: If true home cursor else leave at current position (default: {True}).
        """
        cls._output_to_terminal(_CursorClear.SCREEN)
        if cursor_home:
            cls.cursor_move(1, 1)

    def cursor_up(cls, steps: int = 1):
        """
        Move cursor up.

        Keyword Arguments:
            steps: Number of rows to move up (default: {1}).
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{steps}A')

    def cursor_down(cls, steps: int = 1):
        """
        Move cursor down.

        Keyword Arguments:
            steps: Number of rows to move down (default: {1}).
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{steps}B')

    def cursor_right(cls, steps: int = 1):
        """
        Move cursor right.

        Keyword Arguments:
            steps: Number of columns to move right (default: {1}).
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{steps}C')

    def cursor_left(cls, steps: int = 1):
        """
        Move cursor left.

        Keyword Arguments:
            steps: Number of columns to move left (default: {1}).
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{steps}D')

    def cursor_scroll_up(cls, steps: int = 1):
        """
        Scroll screen contents up.

        Keyword Arguments:
            steps: Number of row to scroll up (default: {1}).
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{steps}S')

    def cursor_scroll_down(cls, steps: int = 1):
        """
        Scroll screen contents down.

        Keyword Arguments:
            steps: Number of row to scroll down (default: {1}).
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{steps}T')


    def cursor_move(cls, row:int = -1, column:int = -1) -> bool:
        """
        Move cursor to spefic location on console.

        If row or column is not set, current position (row or column) will be used.

        Keyword Arguments:
            row: Row to move cursor (default: {-1}).
            column: Column to move cursor (default: {-1}).

        Returns:
            True if successful, False if location not valid.
        """

        cur_row, cur_col = cls.cursor_current_position()
        if  row <= 0:
            row = int(cur_row)
        if column <= 0:
            column = int(cur_col)
        max_rows, max_columns = cls.get_console_size()
        if row <= 0 or column <= 0:
            LOGGER.debug('cursor_move - row/column must be > 0')
            return False
        if column > max_columns or row > max_rows:
            LOGGER.debug((f'cursor_move - row > {max_rows} or col > {max_columns}'))
            return False
        
        cls._output_to_terminal(f"{_ConsoleControl.ESC}[%d;%dH" % (row, column))    
        return True

    def print_at(cls, row: int, col: int, text: str, eol='') -> bool:
        """
        Print text at specific location on console.

        No new-line will occur unless eol parameter is specifed as '\\n'.

        Arguments:
            row: Target row.
            col: Target column.
            text: String to write to console.

        Keyword Arguments:
            eol: _description_ (default: {''}).

        Returns:
            True if print to console successful, False if invalid location.
        """

        if cls.cursor_move(row, col):
            cls._output_to_terminal(text, eol)
            return True
        return False
        
    def cursor_current_position(cls) -> Tuple[int, int]:
        """
        Current cursor location.

        Returns:
            Cusor location: (row, col).
        """
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
        
        return (int(row), int(col))

    def cursor_save_position(cls):
        """
        Save cursor position, can be restored with restore_position() call.
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[s')

    def cursor_restore_position(cls):
        """
        Restore cursor position, saved with the save_position() call.
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[u')

    def get_console_size(cls) -> Tuple[int, int]:
        """
        Return console size in rows and columns.

        Returns:
            Size as (rows, columns).
        """
        rows = int(os.getenv('LINES', -1))
        columns = int(os.getenv('COLUMNS', -1))
        if rows <= 0 or columns <= 0:
            size = os.get_terminal_size()
            rows = int(size.lines)
            columns = int(size.columns)

        return (rows, columns)

    def set_viewport(cls, start_row: int = None, end_row: int = None):
        """
        Set console scrollable area to start_row / end_row.  Default is whole screen.

        The viewport defines area (rows) text scrolls within.  If no
        arguments provided, viewport is defaulted to whole screen.

        Keyword Arguments:
            start_row: Staring row of viewport (default: {None}).
            end_row: Ending row of viewport (default: {None}).

        Raises:
            ValueError: Invalid start|end row.
        """

        max_row, max_col = cls.get_console_size()
        starting_row = 1 if start_row is None else start_row
        ending_row = int(max_row) if end_row is None else end_row
        if starting_row < 1 or starting_row > ending_row or starting_row > max_row:
            raise ValueError(f"set_viewport(): Invalid start row: {start_row}")
        if ending_row > max_row:
            raise ValueError(f'set_viewport(): Invalid end row: {end_row}')

        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{starting_row};{ending_row}r')

    def display_status(cls, text, wait: int = 0):
        """
        Display status message on last row of screen.

        Arguments:
            text: Status message to be displayed.

        Keyword Arguments:
            wait: Number of seconds to wait/pause (default: {0}).
        """
        max_row, max_col = cls.get_console_size()

        save_row, save_col = cls.cursor_current_position()
        cls.print_at(max_row, 1, f'{text}', eol='')     
        cls.clear_to_EOL()
        cls.cursor_move(save_row, save_col)   
        if wait > 0:
            time.sleep(wait)

    def sprint_line_separator(cls, text: str = '', length: int = -1) -> str:
        """
        Return string underline (seperator) with optional text.

        Keyword Arguments:
            text: Text to be displayed within the separator line (default: {''}).
            length: Length of the separator line  (default: {-1}).
            if < 0, use console width.

        Returns:
            Separator line string.
        """
        if length < 0:
            row, col = cls.cursor_current_position()
            max_rows, max_cols = cls.get_console_size()
            length = max_cols - col
        fill_len = length - len(text)
        line_out = f'{_FormatControls.underline}{text}{" "*(fill_len-1)}{_FormatControls.spacer}{_FormatControls.end}'
        return line_out

    def print_line_seperator(cls, text: str = '', length: int = -1):
        """
        Print line separator at current cursor position.

        Keyword Arguments:
            text: Text to be displayed within the separator line (default: {''}).
            length: Lenght of the separator line  (default: {-1}).
            if < 0, use console width.
        """
        print(cls.sprint_line_separator(text, length))

    def debug_display_cursor_location(cls, msg:str = ""):
        """
        Display current location (row, col) in status area.

        Keyword Arguments:
            msg: Message text to append after current location (default: {""}).
        """
        cls.display_status(f'Cursor: {str(ConsoleHelper().cursor_current_position())}  {msg}')

    def print_with_wait(cls, text: str, wait: float = 0.0, eol='\n'):
        """
        Print text at current location and wait specified number of seconds.

        Arguments:
            text: Text to be printed.

        Keyword Arguments:
            wait: Number of seconds to wait (default: {0.0}).
            eol: EndOfLine character (default: {'\\n'}).

        """
        print(text, end=eol, flush=True)
        if wait > 0:
            time.sleep(wait)

    def cwrap(cls, text: str, color: Union[ColorFG, str], colorBG: ColorBG = None, style: ColorStyle = None) -> str:
        """
        Wrap text with color codes for console display.
        
        See ConsoleFG, ConsoleBG and ConsoleStyle for control codes

        Arguments:
            **text**: req - String containing text to be colorized.
            **color**: req -  The FG color OR color string (see console_color())
            **colorBG**: opt - The BG color (see ColorBG)
            **style**: opt - The style to be applied (see ColorStyle)

        Returns:
            Updated string.
        """
        
        color_code = color if isinstance(color, ColorFG) else cls.color_code(color, colorBG, style)

        return f'{color_code}{text}{_ConsoleControl.CEND}'

    def color_code(cls, style: ColorStyle = None, fg: ColorFG = None, bg: ColorBG= None) -> str:
        """
        Create ANSI color code for style, fg color and bg color

        If any parameter (style, fg or bg) is None, current value will be used.

        Args:
            
            **style**: (:class:`~ColorStyle`, optional): Font style (ie. bold, italic,...).  
            **fg**: (:class:`~ColorFG`, optional): Foreground text color.  
            **bg**: (:class:`~ColorBG`, optional): Background color.  

        Returns:
            str: The ANSI code representing the desired ANSI atributes.
            
        """
        codes = [str(style), str(fg), str(bg)]
        format = ''.join([x for x in codes if x != 'None'])
        code = f'{_ConsoleControl.ESC}[{format}'
        return code

    # == Private Function =================================================================================    
    def _output_to_terminal(cls, token: str, eol:str=''):
        print(token, end=eol, flush=True)
        cls.LAST_CONSOLE_STR = token

    def _display_color_palette(cls):
        """
        prints table of formatted text format options
        """
        for style in range(8):
            for fg in range(30, 38):
                s1 = ''
                for bg in range(40, 48):
                    format = ';'.join([str(style), str(fg), str(bg)])
                    s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
                print(s1)
            print('\n')

# ==========================================================================================================
class ConsoleInputHelper():
    """
    Helper for getting input from the console.

    Example::

        from dt_tools.console.console_helper import ConsoleInputHelper

        ih = ConsoleInputHelper()
        resp = ih.get_input_with_timeout(prompt='Pick a color > ', 
            valid_responses=['Red', 'Blue', 'Green'], 
            default='Blue', 
            timeout_secs=5)
        print(f'You selected: {resp}')    

    """

    YES_NO_RESPONSE: Final[List[str]] = ['Y','y', 'N', 'n']
    """Yes/No valid_argument list constant"""

    def get_input_with_timeout(cls, prompt: str, valid_responses: list = [],  
                               default: str = None, timeout_secs: int = -1, 
                               parms_ok: bool = False) -> Union[str, Tuple[str, list]]:
        """
        Display a prompt for use input.  
        
        If valid_responses is supplied:
            - input will be validated.  User will be re-prompted on bad input. 
            - default response will be returned after timeout (if specified).

        Arguments:
            **prompt**: Text to be displayed as prompt.
            **valid_responses**: A list of valid responses (default: {[]}).
              User input must match one of the values. 
              If list is empty, all input will be accepted.
            **default**: Default value to be return on timeout (default: {None}).
            **timeout_secs**: Number of seconds to wait for response (default: {-1}).  
              If <0, no timeout, wait until user presses enter.
            **parms_ok**: Allow extra parameter input (default: {False}).
              If True, allows user to provide additional text after the valid response.

        Returns:
            User input or default value (if timeout).

        Example::

            from dt_tools.console.console_helper input ConsoleInputHelper

            ih = ConsoleInputHelper()
            resp = ih.get_input_with_timeout(prompt='Pick a color > ', 
                valid_responses=['Red', 'Blue', 'Green'], 
                default='Blue', 
                timeout_secs=5)
            print(f'You selected: {resp}')

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
        """
        Pause execution for specified number of seconds.
        
        User may press enter to resume prior to timeout seconds.

        Arguments:
            secs: Number of seconds to wait.
        """
        cls.get_input_with_timeout("", timeout_secs=secs)

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
def pad_r(text: str, length: int, pad_char: str = ' ') -> str:
    """
    Pad input text with pad character, return left justified string of specified length.

    Example::
    
        text = pad_r('abc', 10, pad_char='X')
        print(text) 
        'abcXXXXXXXX'

    Arguments:
        text: Input string to pad.
        length: Length of resulting string.

    Keyword Arguments:
        pad_char: String padding character (default: {' '}).

    Raises:
        ValueError: Pad character MUST be of length 1.

    Returns:
        Left justified padded string.
    """
    if len(pad_char) > 1:
        raise ValueError('Padding character should only be 1 character in length')
    
    pad_len = length - len(text)
    if pad_len > 0:
        return f'{text}{pad_char*pad_len}'
    return text    

def pad_l(text: str, length: int, pad_char: str = ' ') -> str:
    """
    Pad input text with pad character, return right-justified string of specified length.

        Example::
    
            text = pad_l('abc', 10, pad_char='X')
            print(text) 
            'XXXXXXXXabc'

    Arguments:
        text: Input string to pad.
        length: Length of resulting string.

    Keyword Arguments:
        pad_char: String padding character [default: {' '}].

    Raises:
        ValueError: Pad character MUST be of length 1.

    Returns:
        Right justified padded string.
    """
    if len(pad_char) > 1:
        raise ValueError('Padding character should only be 1 character in length')
    
    pad_len = length - len(text)
    if pad_len > 0:
        return f'{pad_char*pad_len}{text}'
    return text    

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
    
    Prompt will timeout after 10 seconds and exit.
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


if __name__ == "__main__":
    from dt_tools.cli.dt_console_demo import console_helper_demo as demo
    demo()

    print("That's all folks!")
from dt_tools.console.console_helper import ColorFG
from dt_tools.console.console_helper import ConsoleHelper as console
from dt_tools.console.spinner import Spinner, SpinnerType
import time

def demo():    
    console.print('')
    console.print_line_seperator('Spinner Demo', 40)
    console.print('')
    
    sleep_time = .25
    for spinner_type in SpinnerType:
        spinner = Spinner(caption=spinner_type, spinner=spinner_type, show_elapsed=True)
        spinner.start_spinner()
        for cnt in range(1,21):
            if cnt % 5 == 0:
                spinner.caption_suffix(f'working... {cnt} of 20')
            time.sleep(sleep_time)
        spinner.stop_spinner()
    
    console.print('')
    console.print(f"End of {console.cwrap('Spinner',ColorFG.YELLOW)} demo.")

if __name__ == '__main__':
    demo()
from dt_tools.console.console_helper import ColorFG
from dt_tools.console.console_helper import ConsoleHelper as console
from dt_tools.console.progress_bar import ProgressBar
import time

def demo():    
    console.print('')
    console.print_line_seperator('ProgressBar Demo', 40)
    console.print('')
    
    sleep_time = .15
    pbar = ProgressBar("Demo Progress bar", bar_length=40, max_increments=50, show_elapsed=False)
    for incr in range(1,51):
        pbar.display_progress(incr, f'incr [{incr}]')
        time.sleep(sleep_time)    

    console.print('\nProgress bar with elapsed time...')
    pbar = ProgressBar("Demo Progress bar", bar_length=40, max_increments=50, show_elapsed=True)
    for incr in range(1,51):
        pbar.display_progress(incr, f'incr [{incr}]')
        time.sleep(sleep_time)
    
    console.print('')
    console.print(f"End of {console.cwrap('ProgressBar', ColorFG.YELLOW)} demo.")



if __name__ == '__main__':
    demo()
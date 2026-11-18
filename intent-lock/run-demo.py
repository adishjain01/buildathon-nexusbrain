"""Interactive Windows launcher for the local Intent Lock server."""
import msvcrt
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

def start_server():
    print('\nStarting server. Open the address printed below in your browser.', flush=True)
    print('Press R to restart the server, or Q to quit this launcher.', flush=True)
    return subprocess.Popen([sys.executable, str(HERE / 'server.py'), *sys.argv[1:]], cwd=HERE)

def stop_server(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

def main():
    process = start_server()
    reported = False
    try:
        while True:
            if process.poll() is not None and not reported:
                print(f'\nServer stopped (exit {process.returncode}). Press R to retry or Q to quit.', flush=True)
                reported = True
            if msvcrt.kbhit():
                key = msvcrt.getwch().lower()
                if key == 'r':
                    stop_server(process)
                    print('\nRestarting Intent Lock...', flush=True)
                    process = start_server()
                    reported = False
                elif key == 'q':
                    break
                elif key in ('\x00', '\xe0') and msvcrt.kbhit():
                    msvcrt.getwch()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        stop_server(process)
        print('\nIntent Lock stopped.', flush=True)

if __name__ == '__main__':
    main()

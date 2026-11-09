"""keep_awake - keep Windows from sleeping while long background work runs.

Uses one documented Windows API call, SetThreadExecutionState, through
Python's built-in ctypes. No power settings are changed, nothing is
installed, nothing runs after this script exits.

Usage:
    python keep_awake.py              # stay awake for 2 hours
    python keep_awake.py -t 8         # stay awake for 8 hours
    python keep_awake.py -t 0.5 -d    # 30 minutes, keep the display on too
"""
import argparse
import ctypes
import sys
import time
from datetime import datetime, timedelta

# Flags for SetThreadExecutionState
# https://learn.microsoft.com/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate
ES_CONTINUOUS = 0x80000000        # keep the request until it is changed again
ES_SYSTEM_REQUIRED = 0x00000001   # the system must not go to sleep
ES_DISPLAY_REQUIRED = 0x00000002  # the display must stay on as well


def set_state(flags):
    """Calls SetThreadExecutionState. Returns False if Windows refused."""
    kernel32 = ctypes.windll.kernel32
    kernel32.SetThreadExecutionState.restype = ctypes.c_uint32
    kernel32.SetThreadExecutionState.argtypes = [ctypes.c_uint32]
    return kernel32.SetThreadExecutionState(flags) != 0


def prevent_sleep(keep_display_on):
    flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    if keep_display_on:
        flags |= ES_DISPLAY_REQUIRED
        print("Preventing sleep, display stays on...")
    else:
        print("Preventing sleep (display can still turn off)...")
    return set_state(flags)


def allow_sleep():
    print("Allowing Windows to go to sleep again...")
    set_state(ES_CONTINUOUS)  # clear our request


def main():
    parser = argparse.ArgumentParser(description="Prevent Windows from sleeping for a while.")
    parser.add_argument("-t", "--timeout", type=float, default=2.0,
                        help="how long to stay awake, in hours (default: 2)")
    parser.add_argument("-d", "--display", action="store_true",
                        help="also keep the display on")
    args = parser.parse_args()

    if sys.platform != "win32":
        print("Error: keep_awake only works on Windows.")
        sys.exit(1)
    if args.timeout <= 0:
        print("Error: --timeout must be greater than 0.")
        sys.exit(2)

    if not prevent_sleep(args.display):
        print("Error: Windows rejected the request (SetThreadExecutionState failed).")
        sys.exit(1)

    end = datetime.now() + timedelta(hours=args.timeout)
    print(f"Your PC will stay awake for {args.timeout:g} hours, until {end:%H:%M} ({end:%d.%m.%Y}).")
    print("Press Ctrl+C to stop early and allow sleep again.")

    try:
        # Sleep in 1 second steps so Ctrl+C is handled right away.
        while datetime.now() < end:
            time.sleep(1)
        print(f"{args.timeout:g} hours have passed.")
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        allow_sleep()
        print("Exiting.")


if __name__ == "__main__":
    main()

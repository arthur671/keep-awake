# keep-awake

**Keep Windows awake while long background work runs, without touching any settings. One short Python file you can read in a few minutes.**

Downloads, renders, backups, AI agents, long builds: Windows goes to sleep and the work stops. The usual fixes are changing your power plan (and forgetting to change it back) or installing a tool you have to take on trust. keep-awake is neither.

```text
> python keep_awake.py -t 3
Preventing sleep (display can still turn off)...
Your PC will stay awake for 3 hours, until 14:12 (09.11.2026).
Press Ctrl+C to stop early and allow sleep again.
```

## Why this one: full transparency

- **Under 90 lines of plain Python, comments included.** No compiled binary, no installer, no background service, no tray app. What you read is exactly what runs.
- **One documented Windows API call.** It calls [`SetThreadExecutionState`](https://learn.microsoft.com/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate), the same mechanism video players and installers use, through Python's built-in `ctypes`.
- **No dependencies.** Only the Python standard library. Nothing to `pip install`.
- **No settings changed.** Your power plan, sleep timers and registry stay exactly as they are. Nothing is written to disk.
- **Cannot get stuck.** The request belongs to the running process. When the time is up, you press Ctrl+C, or the window is closed or the process is killed, Windows drops the request automatically and normal sleep resumes.
- **No network, no admin rights.**

Tools like PowerToys Awake do the same job well. They come as part of a large app suite with a prebuilt executable, though. If you want something whose whole behaviour you can verify yourself in a few minutes, this is it.

## Usage

Requires Windows and Python 3.7 or newer.

```bash
python keep_awake.py              # stay awake for 2 hours (default)
python keep_awake.py -t 8         # stay awake for 8 hours
python keep_awake.py -t 0.5       # 30 minutes
python keep_awake.py -t 4 -d      # 4 hours, and keep the display on too
```

| Option | Meaning |
|---|---|
| `-t HOURS`, `--timeout HOURS` | How long to stay awake, in hours. Decimals allowed. Default: `2` |
| `-d`, `--display` | Also keep the display on. Without it, the screen can still turn off and lock as usual while the PC keeps working |
| `-h`, `--help` | Show help |

Stop early at any time with **Ctrl+C** or by closing the window.

Keep the window open while your work runs: the PC stays awake only as long as keep-awake is running.

## What it does, exactly

1. On start it calls `SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)`, plus `ES_DISPLAY_REQUIRED` with `-d`. That tells Windows "this program needs the system awake".
2. It waits, checking once per second so Ctrl+C reacts immediately.
3. On exit, for any reason, it calls `SetThreadExecutionState(ES_CONTINUOUS)` to withdraw the request. Even if that line never runs (process killed), Windows withdraws it when the process ends.

That is the whole program.

## Verify it yourself

In an **administrator** command prompt, while keep-awake is running:

```bash
powercfg /requests
```

`python.exe` is listed under `SYSTEM:` (and under `DISPLAY:` with `-d`). After keep-awake exits, it is gone.

## What it does not do

- It does not stop **you** from sleeping the PC: Start → Sleep, closing a laptop lid (depending on your lid setting) or pressing the power button still work.
- It does not stop a screen saver or screen lock. `-d` only keeps the display from switching off.
- It does not move the mouse or press keys, so your status in chat apps is unaffected.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Finished normally or stopped with Ctrl+C |
| `1` | Not on Windows, or Windows rejected the request |
| `2` | Invalid arguments (e.g. `-t 0`) |

## Support

If this tool saved you some time, you can [buy me a coffee on Ko-fi](https://ko-fi.com/arthur9366) ☕

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/arthur9366)

## License

[MIT](LICENSE)

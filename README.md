# ackman-alert

<img width="1480" height="833" alt="ackman_alert_overlay" src="https://github.com/user-attachments/assets/7cf27e07-f703-4e58-b127-c1cce7520f0e" />

Ackman Alert in particular uses `snscrape`, which occasionally drags if X changes markup; the script is resilient and keeps trying.

In this instance I do duplicate handle checks or make `HANDLES = ["BillAckman", "another"]` and loop. It is worth noting the loop then iterates over each handle in sequence, scraping the most recent post for each one and comparing it against a saved state file.

This design choice by me (Michael Mendy) provides flexibility for extending the system beyond Ackman alone, useful if you want to follow a set of influential voices simultaneously. Furthermore, the state persistence mechanism `(~/.ackman_alert_state.json`) by default) can be easily extended to store per-handle last `IDs`, ensuring no cross-account conflicts. The script handles all the usual hiccups you'd expect—network timeouts, wonky responses, and when X just decides to take a break—then picks up right where it left off once everything's back to normal.

Whilst making the script, I wanted to balances simplicity (no API tokens required) with durability, making it a practical solution for real-time push notifications on macOS—even in the face of occasional upstream changes for when Bill Ackman posted to X. 

<img width="3840" height="2979" alt="Untitled diagram _ Mermaid Chart-2025-08-20-115157" src="https://github.com/user-attachments/assets/23cb8f41-dd1b-4b27-9787-66ebfe37e309" />

It's worth to note, if you simply reused the original script I wrote with multiple names hard-coded, you’d run into state collisions. That’s because the script stored just one “last seen post ID” in a single JSON file `(~/.ackman_alert_state.json)`. If account A updated the file, then account B would overwrite it, and the script would lose track of which tweets it had already notified you about.

## Quick Setup

# 1) Create a `venv` (optional but recommended)
```bash
python3 -m venv ~/.venvs/ackman-alert
source ~/.venvs/ackman-alert/bin/activate
```

# 2) Install `snscrape`
```bsah
pip install --upgrade pip
pip install snscrape
```

# 3) Test it (one-shot, no notification on first run)
```bash
python ackman_alert.py --once
```

# 4) Run in a `loop` (foreground)
```bash
python ackman_alert.py --notify-on-first
```

## Notes & Options 

If you prefer clickable notifications that open the post automatically, install `terminal-notifier` and `swap` notify() for a `subprocess.run(["terminal-notifier", "-title", "...", "-subtitle", "...", "-message", "...", "-open", latest['url']]) `. Please install `terminal-notifier`.

```bash
brew install terminal-notifier
```

Below is a mitigations table I've made to let you know what can break `ackman-alert` and what likely isn't going to break it:

| Category                     | What Could Go Wrong                         | Mitigation                                                                              |
| ---------------------------- | ------------------------------------------- | --------------------------------------------------------------------------------------- |
| **Scraper-Level (snscrape)** | X changes markup → scraper fails            | Catch exceptions, log warnings, retry next loop; keep `snscrape` updated                |
|                              | Rate limiting or blocking by X              | Add per-handle delay or backoff; reduce polling interval                                |
|                              | Network failures (timeout, DNS)             | Wrap fetch in try/except; retry on next loop                                            |
|                              | Library bugs / environment drift            | Pin dependency versions in `requirements.txt`; test regularly                           |
| **Notifications**            | AppleScript fails silently                  | Fallback to `terminal-notifier` if installed                                            |
|                              | `terminal-notifier` missing                 | Default to AppleScript-only; document install step (`brew install terminal-notifier`)   |
|                              | macOS Focus/Do Not Disturb hides banners    | User awareness: check Notification Center; optionally add logging of notifications sent |
|                              | Notification collapse (multiple posts)      | Send one per post with unique IDs; consider batching only for high-volume handles       |
| **State File**               | Corruption due to crash                     | Atomic write (temp file + replace) to prevent partial JSON                              |
|                              | Disk full / permission error                | Store state in `~/.x_multi_alert_state.json`; add error logging if writes fail          |
|                              | Manual edits break JSON                     | Validate state file on load; fallback to empty dict if invalid                          |
| **Logic Edge Cases**         | Tweets without text (image/video/poll only) | Fallback to “\[Media Post]” in notification body                                        |
|                              | Retweets or pinned tweets repeat            | Filter for `isRetweet == False`; ignore pinned items                                    |
|                              | Timezone/clock drift                        | Compare post IDs, not timestamps                                                        |
| **Environment / Runtime**    | Launchd not starting script                 | Test with `launchctl list`; document setup in README                                    |
|                              | Virtualenv breaks after Python update       | Pin Python version; rebuild venv after upgrades                                         |
|                              | PATH issues (osascript not found)           | Use absolute paths in `launchd` plist                                                   |
|                              | Mac sleeps during interval                  | Accept gap (catch up next run); or run on always-on machine                             |
|                              | Multiple copies running                     | Use lockfile (`.pid`) to ensure only one instance                                       |
| **Scaling / Multi-Handle**   | Private/suspended/renamed account           | Catch 404 errors, log once, skip handle                                                 |
|                              | Too many handles slows loop                 | Limit handle count; stagger checks                                                      |
|                              | Handle renamed by user                      | Update `--handles` list manually                                                        |
|                              | Deleted accounts                            | Script logs warning and continues                                                       |
| **User Experience**          | Notification fatigue (spam)                 | Increase interval or limit monitored accounts                                           |
|                              | Duplicate alerts                            | Track per-handle last ID; skip repeats                                                  |
|                              | Truncated text in banner                    | Limit to `\~180` chars; append link                                                     |
|                              | Out-of-order banners                        | Accept macOS queueing; consider batching alerts                                         |

Now that we know what the mitigations are, let's get this to run on every macOS booot:

## Make it run on boot (macOS)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.michael.ackman-alert</string>

  <key>ProgramArguments</key>
  <array>
    <string>/Users/USERNAME/.venvs/ackman-alert/bin/python</string>
    <string>/Users/USERNAME/path/to/ackman_alert.py</string>
    <string>--notify-on-first</string>
  </array>

  <key>StartInterval</key>
  <integer>300</integer>

  <key>RunAtLoad</key>
  <true/>

  <key>StandardOutPath</key>
  <string>/tmp/ackman-alert.out</string>
  <key>StandardErrorPath</key>
  <string>/tmp/ackman-alert.err</string>
</dict>
</plist>
```
Then you need to load it:

```bash
launchctl unload ~/Library/LaunchAgents/com.michael.ackman-alert.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.michael.ackman-alert.plist
launchctl start com.michael.ackman-alert
```
Worked for me perfectly. 

## Get push notifications to your iPhone

First, get an API key from `Pushbullet`, add this snippet into `ackman-alert.py`:

```python3
import requests, os

PUSHBULLET_TOKEN = os.getenv("PUSHBULLET_TOKEN")

def pushbullet_notify(title, body):
    if not PUSHBULLET_TOKEN:
        return
    requests.post("https://api.pushbullet.com/v2/pushes",
                  headers={"Access-Token": PUSHBULLET_TOKEN,
                           "Content-Type": "application/json"},
                  json={"type": "note", "title": title, "body": body})
```

Now you have the ability to get `ackman-alerts` on your iPhone and not just on your MacBook or iMac. This is how it should look when you get it on your iPhone 15 (or newer):

![IMG_8793](https://github.com/user-attachments/assets/1d6941c2-2832-4cf6-8843-f4e533be5420)

If you’re on macOS, you can piggyback on `Messages.app` to send yourself an iMessage. The example I'm going to show is something I did in AppleScript:

```applescript
import subprocess

def imessage_notify(phone, text):
    script = f'tell application "Messages" to send "{text}" to buddy "{phone}" of service "E:iMessage"'
    subprocess.run(["osascript", "-e", script])
```

## Make the script executable

Put your script in `~/bin/ackman-alert.py` (or any directory you like) and make it executable:

```bash
chmod +x ~/bin/ackman-alert.py
```
Then run:

```python3
python3 ackman-alert.py
```
Enjoy the updates from Bill Ackman himself.

## Author

Michael Mendy (c) 2025.

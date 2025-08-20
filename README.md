# ackman-alert

<img width="1480" height="833" alt="ackman_alert_overlay" src="https://github.com/user-attachments/assets/7cf27e07-f703-4e58-b127-c1cce7520f0e" />

Ackman Alert in particular uses `snscrape`, which occasionally hiccups if X changes markup; the script is resilient and keeps trying.

In this instance I do duplicate handle checks or make `HANDLES = ["BillAckman", "another"]` and loop. It is worth noting the loop then iterates over each handle in sequence, scraping the most recent post for each one and comparing it against a saved state file.

This design choice by me (Michael Mendy) provides flexibility for extending the system beyond Ackman alone, useful if you want to follow a set of influential voices simultaneously. Furthermore, the state persistence mechanism `(~/.ackman_alert_state.json`) by default) can be easily extended to store per-handle last `IDs`, ensuring no cross-account conflicts.

Whilst making the script, I wanted to balances simplicity (no API tokens required) with durability, making it a practical solution for real-time push notifications on macOS—even in the face of occasional upstream changes for when Bill Ackman posted to X. 

It's worth to note, if you simply reused the original script I wrote with multiple names hard-coded, you’d run into state collisions. That’s because the script stored just one “last seen post ID” in a single JSON file `(~/.ackman_alert_state.json)`. If account A updated the file, then account B would overwrite it, and the script would lose track of which tweets it had already notified you about.

## Quick Setup

# 1) Create a venv (optional but recommended)
```bash
python3 -m venv ~/.venvs/ackman-alert
source ~/.venvs/ackman-alert/bin/activate
```

# 2) Install snscrape
```bsah
pip install --upgrade pip
pip install snscrape
```

# 3) Test it (one-shot, no notification on first run)
```bash
python ackman_alert.py --once
```

# 4) Run in a loop (foreground)
```bash
python ackman_alert.py --notify-on-first
```

## Notes & Options 

If you prefer clickable notifications that open the post automatically, install `terminal-notifier` and `swap` notify() for a `subprocess.run(["terminal-notifier", "-title", "...", "-subtitle", "...", "-message", "...", "-open", latest['url']]) `. Please install `terminal-notifier`.

```bash
brew install terminal-notifier
```

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

## Author

Michael Mendy (c) 2025.

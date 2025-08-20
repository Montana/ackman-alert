# ackman-alert

<img width="1480" height="833" alt="ackman_alert_overlay" src="https://github.com/user-attachments/assets/7cf27e07-f703-4e58-b127-c1cce7520f0e" />

Ackman Alert in particular uses `snscrape`, which occasionally hiccups if X changes markup; the script is resilient and keeps trying.

In this instance I do duplicate handle checks or make `HANDLES = ["BillAckman", "another"]` and loop.

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

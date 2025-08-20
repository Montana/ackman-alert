#!/usr/bin/env python3
import json, os, sys, subprocess, time
from pathlib import Path

HANDLE = "BillAckman"   
STATE_FILE = Path.home() / ".ackman_alert_state.json"
CHECK_INTERVAL_SEC = 60  # only used in --loop mode - michael 

def notify(title, subtitle, message):
    script = f'display notification {json.dumps(message)} with title {json.dumps(title)} subtitle {json.dumps(subtitle)}'
    subprocess.run(["osascript", "-e", script], check=False)

def load_last_id():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text()).get("last_id")
        except Exception:
            return None
    return None

def save_last_id(tweet_id):
    STATE_FILE.write_text(json.dumps({"last_id": tweet_id}))

def get_latest_tweet(): # no need for X API
    try:
        import snscrape.modules.twitter as sntwitter
    except ImportError:
        print("snscrape not installed. Run: pip install snscrape", file=sys.stderr)
        sys.exit(1)

    scraper = sntwitter.TwitterUserScraper(HANDLE)
    for i, tweet in enumerate(scraper.get_items()):
        if i == 0:
            return {
                "id": tweet.id,
                "date": getattr(tweet, "date", None),
                "content": getattr(tweet, "rawContent", getattr(tweet, "content", "")),
                "url": getattr(tweet, "url", f"https://x.com/{HANDLE}/status/{tweet.id}")
            }
    return None

def check_once(notify_on_first=False):
    latest = get_latest_tweet()
    if not latest:
        return False

    last_id = load_last_id()
    if last_id is None:
        save_last_id(latest["id"])
        if notify_on_first:
            notify("Ackman Alert", "@BillAckman", f"Latest: {latest['content']}\n{latest['url']}")
        return True

    if latest["id"] != last_id:
        save_last_id(latest["id"])
        snippet = latest["content"][:180].replace("\n", " ")
        notify("Ackman posted on X", "@BillAckman", f"{snippet}\n{latest['url']}")
        return True

    return False

def main():
    if "--once" in sys.argv:
        notify_on_first = "--notify-on-first" in sys.argv
        changed = check_once(notify_on_first=notify_on_first)
        sys.exit(0 if changed else 0)

    # default: loop mode
    notify_on_first = "--notify-on-first" in sys.argv
    while True:
        try:
            check_once(notify_on_first=notify_on_first)
        except Exception as e:
            print(f"[warn] {e}", file=sys.stderr)
        time.sleep(CHECK_INTERVAL_SEC)
        notify_on_first = False

if __name__ == "__main__":
    main()

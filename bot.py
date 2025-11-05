import os, json, re, time
import feedparser
import tweepy

API_KEY = os.getenv("X_API_KEY")
API_SECRET = os.getenv("X_API_SECRET")
ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def clean_text(s):
    return re.sub(r'\s+', ' ', s).strip()

def make_tweet(title, link, tags, max_len=270):
    base = f"{title} {tags} {link}"
    if len(base) <= max_len:
        return base
    room = max_len - len(tags) - len(link) - 2
    short_title = (title[:room-1] + "…") if room > 10 else title[:room]
    return f"{short_title} {tags} {link}"

def main():
    with open("feeds.json", "r") as f:
        feeds = json.load(f)
    state = load_state()
    changed = False

    for feed in feeds:
        name = feed["name"]
        url = feed["feed"]
        tags = feed["hashtags"]

        parsed = feedparser.parse(url)
        if not parsed.entries:
            continue

        entry = parsed.entries[0]
        uid = getattr(entry, "id", entry.link)
        title = clean_text(entry.title)
        link = entry.link

        if state.get(name) == uid:
            continue

        tweet = make_tweet(title, link, tags)
        try:
            api.update_status(status=tweet)
            print(f"✅ Tweeted: {tweet}")
            state[name] = uid
            changed = True
            time.sleep(3)
        except Exception as e:
            print(f"❌ Error tweeting {name}: {e}")

    if changed:
        save_state(state)

if __name__ == "__main__":
    main()

import asyncio
import aiohttp
import random
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

PREFIXES = ["ninja", "dev", "gaben", "jky", "slonik0v", ""] # add more prefixes as needed and change them
CHARS = "abcdefghijklmnopqrstuvwxyz0123456789"
MIN_LEN = 0
MAX_LEN = 2
DELAY = 1.5

LOG_FILE = "log.txt"
OUT_FILE = "available_usernames.txt" # file to save available usernames github and steam in your directory

checked = set()
stats = {
    "total": 0,
    "github_taken": 0,
    "github_free": 0,
    "steam_taken": 0,
    "steam_free": 0,
    "errors": 0
}

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

async def check_github(session, username):
    url = f"https://github.com/{username}"
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                stats["github_taken"] += 1
                return False
            elif resp.status == 404:
                stats["github_free"] += 1
                return True
            else:
                log(f"GitHub unknown status {resp.status} for {username}")
    except Exception as e:
        stats["errors"] += 1
        log(f"GitHub error for {username}: {e}")
    return None

async def check_steam(session, username):
    url = f"https://steamcommunity.com/id/{username}"
    try:
        async with session.get(url) as resp:
            text = await resp.text()

            if "The specified profile could not be found." in text:
                stats["steam_free"] += 1
                return True
            elif resp.status == 200:
                stats["steam_taken"] += 1
                return False
            else:
                log(f"Steam unknown status {resp.status} for {username}")
    except Exception as e:
        stats["errors"] += 1
        log(f"Steam error for {username}: {e}")
    return None



def gen_username():
    prefix = random.choice(PREFIXES)
    suffix = ''.join(random.choices(CHARS, k=random.randint(MIN_LEN, MAX_LEN)))
    return prefix + suffix

def show_stats():
    print(
        Fore.BLUE +
        f"\n[STATS] Checked: {stats['total']} | "
        f"GitHub ✓ {stats['github_free']} ✗ {stats['github_taken']} | "
        f"Steam ✓ {stats['steam_free']} ✗ {stats['steam_taken']} | "
        f"Errors: {stats['errors']}"
    )

async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            name = gen_username()
            if name in checked:
                continue
            checked.add(name)
            stats["total"] += 1

            print(Fore.CYAN + f"[{stats['total']}] Checking: {name}")

            gh = await check_github(session, name)
            st = await check_steam(session, name)

            if gh or st:
                print(Fore.GREEN + f"[AVAILABLE] {name} » GitHub: {'✓' if gh else '✗'} | Steam: {'✓' if st else '✗'}")
                with open(OUT_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{name} » GitHub: {'✓' if gh else '✗'} | Steam: {'✓' if st else '✗'}\n")
            else:
                print(Fore.RED + f"[TAKEN]     {name} » GitHub: {'✓' if gh else '✗'} | Steam: {'✓' if st else '✗'}")

            show_stats()
            await asyncio.sleep(DELAY)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[EXIT] Остановлено пользователем.")
        show_stats()


# https://github.com/slonik0v - please star this repo if you like it thanks!
import os
import json
import re
import random

def match_sessions_to_proxies():
    sessions_dir = 'sessions'
    proxies_file = 'bot/config/proxies/proxies.txt'
    session_files = [f for f in os.listdir(sessions_dir) if f.endswith('.session')]

    with open(proxies_file, 'r') as f:
        proxies = f.read().splitlines()

    session_proxy_map = {}
    number_pattern = re.compile(r'^(\d+)')

    for session_file in session_files:
        session_name = os.path.splitext(session_file)[0]
        match = number_pattern.match(session_name)

        if match:
            account_number = int(match.group(1))
            if 1 <= account_number <= len(proxies):
                session_proxy_map[session_name] = proxies[account_number - 1]
            else:
                session_proxy_map[session_name] = random.choice(proxies)
        else:
            session_proxy_map[session_name] = random.choice(proxies)

    with open('bot/config/proxies/session_proxy.json', 'w') as f:
        json.dump(session_proxy_map, f, indent=4)

    print(f"Matched {len(session_proxy_map)} sessions with proxies.")

if __name__ == "__main__":
    match_sessions_to_proxies()

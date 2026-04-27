import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime

# ---------------- SETTINGS ----------------

CHECK_INTERVAL_SECONDS = 60  # 1800 seconds = 30 minutes = twice per hour

# ---------------- FLAG COUNTER CONFIG ----------------

url = "https://flagcounter.me/php/ajax_traffic.php"

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,bn;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://flagcounter.me",
    "pragma": "no-cache",
    "referer": "https://flagcounter.me/details/code_id_here/live-traffic",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}

form_data = {
    "code_id": "code_id_here"
}

# ---------------- TELEGRAM CONFIG ----------------

TELEGRAM_BOT_TOKEN = "telegram_bot_token_here"


# ---------------- TELEGRAM FUNCTIONS ----------------

def get_all_users():
    try:
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        response = requests.get(telegram_url, timeout=10)
        data = response.json()

        users = set()

        for update in data.get("result", []):
            if "message" in update:
                users.add(update["message"]["chat"]["id"])
            elif "edited_message" in update:
                users.add(update["edited_message"]["chat"]["id"])
            elif "callback_query" in update:
                users.add(update["callback_query"]["from"]["id"])

        return list(users)

    except Exception as e:
        print("Telegram get users error:", e)
        return []


def send_telegram_message(title, message):
    users = get_all_users()

    if not users:
        print("No Telegram users found. Send /start to your bot first.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    telegram_message = (
        f"🚩 {title}\n\n"
        f"{message}\n\n"
        f"Checked Time: {timestamp}"
    )

    for chat_id in users:
        try:
            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

            payload = {
                "chat_id": chat_id,
                "text": telegram_message
            }

            response = requests.post(telegram_url, data=payload, timeout=10)

            if response.status_code == 200:
                print(f"Telegram message sent to {chat_id}")
            else:
                print(f"Failed to send Telegram message to {chat_id}: {response.text}")

        except Exception as e:
            print(f"Telegram send error for {chat_id}:", e)


# ---------------- FLAG COUNTER FUNCTIONS ----------------

def get_current_rows():
    response = requests.post(
        url,
        headers=headers,
        data=form_data,
        timeout=10
    )

    soup = BeautifulSoup(response.text, "html.parser")

    rows = []

    for tr in soup.select("tbody tr"):
        cols = tr.find_all("td")

        if len(cols) >= 5:
            country = cols[1].get_text(" ", strip=True)
            browser = cols[2].get_text(" ", strip=True)
            platform = cols[3].get_text(" ", strip=True)

            row_data = {
                "country": country,
                "browser": browser,
                "platform": platform
            }

            rows.append(row_data)

    return rows


def find_new_rows(old_rows, current_rows):
    for shift in range(1, len(current_rows) + 1):
        if current_rows[shift:] == old_rows[:len(current_rows) - shift]:
            return current_rows[:shift]

    return []


def format_visitor_rows(rows):
    text = ""

    for index, row in enumerate(rows, start=1):
        text += (
            f"Visitor #{index}\n"
            f"Country: {row['country']}\n"
            f"Browser: {row['browser']}\n"
            f"Device/Platform: {row['platform']}\n\n"
        )

    return text.strip()


# ---------------- MAIN SCRIPT ----------------

print("Starting first check...")

saved_rows = get_current_rows()

print(f"Saved {len(saved_rows)} rows for first time.")

send_telegram_message(
    title="Visitor Tracker Started",
    message=f"Initial visitor list saved successfully.\nTotal rows saved: {len(saved_rows)}"
)

print("Initial saved rows:")

for i, row in enumerate(saved_rows, start=1):
    print(f"{i}. {row}")

print(f"\nChecking every {CHECK_INTERVAL_SECONDS} seconds...\n")

while True:
    time.sleep(CHECK_INTERVAL_SECONDS)

    try:
        current_rows = get_current_rows()

        if current_rows == saved_rows:
            print("No new visitor")

            # send_telegram_message(
            #     title="Visitor Check Completed",
            #     message=(
            #         "No new visitor detected.\n\n"
            #         f"Total current rows: {len(current_rows)}"
            #     )
            # )

        else:
            print("\nNEW VISITOR ACTIVITY FOUND!")

            new_rows = find_new_rows(saved_rows, current_rows)

            if new_rows:
                print("New visitor/visitors found:")

                for row in new_rows:
                    print("-------------------------")
                    print("Country :", row["country"])
                    print("Browser :", row["browser"])
                    print("Platform:", row["platform"])

                alert_message = (
                    "New visitor activity detected in your live traffic list.\n\n"
                    + format_visitor_rows(new_rows)
                )

                send_telegram_message(
                    title="New Visitor Detected",
                    message=alert_message
                )

            else:
                print("Rows changed, but exact new visitor could not be detected.")

                fallback_message = (
                    "Visitor list changed, but exact new visitor could not be identified.\n\n"
                    "Latest visitor information:\n"
                    f"Country: {current_rows[0]['country']}\n"
                    f"Browser: {current_rows[0]['browser']}\n"
                    f"Device/Platform: {current_rows[0]['platform']}"
                )

                send_telegram_message(
                    title="Visitor Activity Updated",
                    message=fallback_message
                )

            saved_rows = current_rows
            print("\nSaved rows updated.\n")

    except Exception as e:
        print("Error:", e)

        send_telegram_message(
            title="Visitor Tracker Error",
            message=f"Error occurred while checking visitor data:\n{e}"
        )

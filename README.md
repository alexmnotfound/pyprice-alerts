# Price Alert System
![img.png](img.png)
## Purpose
The Price Alert System is a Python script that enables users to track cryptocurrency prices and receive alerts when the prices reach certain thresholds.

---
The script integrates with Google Sheets and Binance API to fetch and compare cryptocurrency prices. Users can input their desired cryptocurrency symbols and target prices in a Google Spreadsheet, and the script periodically checks the current prices on Binance. Once a target price is reached, the system sends an alert message via Telegram to notify the user. The project leverages Google library for Google Sheets integration, python-telegram-bot library for Telegram communication, and requests library for making HTTP requests to the Binance API.

The Price Alert System provides a convenient way for cryptocurrency enthusiasts to stay informed about price movements and make timely investment decisions.

---


## Google Authorization Process

1. Enable the Google Sheets API and appropriate scopes for the application:
   - Go to the Google Cloud Console at https://console.cloud.google.com/w
   - Create a new project or select an existing one.
   - Navigate to APIs and Services, then to the "API Library" tab and search for "Google Sheets API". Click "Enable".
   - Navigate to APIs and Services, then to the "Credentials" tab and click "Create credentials" -> "Service account key".
   - Enter a name for the service account, choose "JSON" as the key type, and click "Create".
   - Save the resulting JSON file in `./credentials` and rename it into `creds.json` secure location.

## Telegram integration

1. Create a Telegram Bot & Get the Token
   * Open your **Telegram** application.
   * Search for `@BotFather` in the search bar (it is a bot provided by Telegram).
   * Start a chat with BotFather by clicking `Start`.
   * Create a **new bot** by sending the following command to **BotFather**: `/newbot`.
   * **BotFather** will ask you to provide a name for your bot. After you answer, it will ask for a username as well. The username must end in `bot`. For example, “MyTestBot” or “my_test_bot”.
   * After completing the bot creation, **BotFather** will provide you with your bot's token. This `token` is a string that looks something like `123456789:AAG90e14-0f8-40183D-18491dDE`.
   * Copy this token and keep it secure. Never share it with anyone.
2. Find Your Chat or Group ID
   * If you haven't done so already during the bot creation process, search for your bot on Telegram (by the username you provided) and start a conversation with it by clicking `Start`.
   * If you want to send messages to a group, add the bot to the group.
   * To get your chat or group ID, use any web browser to navigate to the following URL: https://api.telegram.org/bot<YourBOTToken>/getUpdates (replace <YourBOTToken> with the token you received from BotFather).
   * Send a message to the bot or group. You don't have to do this every time, just once to make it appear in the update's page.
   * Refresh the page, and you'll see an array of all your bot’s interactions. Look for the "chat" object in the array; within it, you can find `id`. This number (might be negative for groups) is your chat or group ID.
   * Copy this ID for usage in your script.


## How to run it
I personally recommend it to run it in a virtual environment, as follows:
1. Open a command prompt or terminal window.
2. Navigate to the directory where you want to create the virtual environment. You can use the `cd` command to change directories.
3. Enter the following command to create a new virtual environment: `python3 -m venv myenv`, replacing "myenv" with the name you want to give to your virtual environment.
4. Activate the virtual environment by entering the following command (Linux environments): `source myenv/bin/activate`
5. Once the virtual environment is activated, you can install Python packages using `pip` as usual. For example, to install the all the packages, 
you can enter the following command: `pip3 install -r requirements.txt`
6. Assuming you're on the project's folder, now you can run `python3 main.py`
7. When you're done using the virtual environment, you can deactivate it by entering the following command: `deactivate`


### References
- [Google Sheets API Python Quickstart](https://developers.google.com/sheets/api/quickstart/python#step_3_set_up_the_sample)
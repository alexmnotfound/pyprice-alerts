from helper.telegram import TelegramNotifier
from helper.google import SheetsHelper
import pandas as pd
import asyncio

async def main():
    try:
        # Main vars
        sheet_id = '1YtiY-KXPj3kBhye5QPkAqYnq5uQZpnTk34o_U2Bn10M'
        sheet_range = 'Watchlist!B8:Z'
        telegram_bot_token = "6471360054:AAG1XUUB0NWbAjd2cKzOrKvFeji2qVZ8ifU"
        telegram_chat_id = "808918721"

        # Initialize the SheetsHelper object
        helper = SheetsHelper()

        # Read data from the sheet
        print(f"Reading data from range {sheet_range} of the Spreadsheet {sheet_id}\n")
        data = helper.get_sheet_data(sheet_id, sheet_range)

        # Create dict with objects to send
        objects_to_send = dict()
        objects_to_send["Open Positions"] = format_df(data, style='positions')
        objects_to_send["Watchlist"] = format_df(data, style='watchlist')

        # Initialize your Telegram notifier class
        notifier = TelegramNotifier(bot_token=telegram_bot_token)

        # Send multiple dataframes into Telegram
        for title, dataframe in objects_to_send.items():
            # Send the image
            await notifier.send_dataframe(telegram_chat_id, dataframe, title=title)

    except Exception as e:
        print(f"An error occurred: {e}")  # Or use logging.
        # Optionally, add more specific error handling (e.g., for specific Google API errors)


def format_df(data, style="general"):
    if not data or not isinstance(data, list) or not all(isinstance(row, list) for row in data):
        raise ValueError("Invalid data format received")

    # Ensure there is more than one row (one for the header, at least one for the data)
    if len(data) < 2:
        raise ValueError("No data available to format")

    # Create Dataframe from data
    df = pd.DataFrame(data)

    new_header = df.iloc[0]  # Grab the first row for the header
    df = df[1:]  # Take the data less the header row
    df.columns = new_header  # Set the header row as the df header

    labels = ['Stop Loss', 'Details', 'Prices of interest', 'Aprox loss', 'Exchange','Stock Name']
    df.drop(columns=labels, axis=0, inplace=True)
    df.dropna(inplace=True)

    match style:
        case "positions":
            df = df[(df['# Shares'] != "")]
            columns = ['Price', 'Change', '% Change']
            df.drop(columns=columns, axis=0, inplace=True)
        case "watchlist":
            df = df[(df['# Shares'] == "")]
            columns = ['# Shares', 'Entry', 'Type', 'PnL', 'Value']
            df.drop(columns=columns, axis=0, inplace=True)
        case _:
            return df

    return df


if __name__ == '__main__':
    asyncio.run(main())

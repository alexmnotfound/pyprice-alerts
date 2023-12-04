import logging, asyncio, sys
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from .keyboard_layouts import MAIN_KEYBOARD, RETURN_KEYBOARD, REPORTS_KEYBOARD

sys.path.append("..")  # Add the parent directory to sys.path
from helpers.google import SheetsHelper
from config.settings import SHEET_ID, SHEET_RANGE


class MyMainBot:
    def __init__(self, token):
        self.logger = logging.getLogger(__name__)
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        self.sheet_id = SHEET_ID
        self.sheet_range = SHEET_RANGE
        # Initialize the SheetsHelper object
        self.sheetsHelper = SheetsHelper()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info(f"User {update.effective_user.id} started the bot")
        await update.message.reply_text('🤖: Hello there\nHow can I help you?:', reply_markup=MAIN_KEYBOARD)

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == 'get_reports':
            await query.edit_message_text(text="🤖: Choose which report you want to get.", reply_markup=REPORTS_KEYBOARD)
        elif query.data == 'analyze_trade':
            await query.edit_message_text(text="🤖: Sorry this isn't ready yet", reply_markup=RETURN_KEYBOARD)

        elif query.data == 'get_open_pos':
            self.logger.info(f"Reading data from range {self.sheet_range} of the Spreadsheet {self.sheet_id}\n")
            await query.edit_message_text(text="🤖: Retrieving data from Google. Please wait...")

            data = self.sheetsHelper.get_sheet_data(self.sheet_id, self.sheet_range)

            # Create dict with objects to send
            objects_to_send = dict()
            objects_to_send["Open Positions"] = format_df(data, style='positions')
            for title, dataframe in objects_to_send.items():
                await self.send_dataframe(context, update.effective_chat.id, dataframe, fmt="simple", title=title)

            await query.message.reply_text(text="🤖: Here are your positions pal\nWhat else can I do for you?",
                                           reply_markup=REPORTS_KEYBOARD)
        elif query.data == 'get_watchlist':
            self.logger.info(f"Reading data from range {self.sheet_range} of the Spreadsheet {self.sheet_id}\n")
            await query.edit_message_text(text="🤖: Retrieving data from Google. Please wait...")

            data = self.sheetsHelper.get_sheet_data(self.sheet_id, self.sheet_range)

            # Create dict with objects to send
            objects_to_send = dict()
            objects_to_send["Watchlist"] = format_df(data, style='watchlist')
            for title, dataframe in objects_to_send.items():
                await self.send_dataframe(context, update.effective_chat.id, dataframe, fmt="simple", title=title)

            await query.message.reply_text(text="🤖: Here is your Watchlist mate\nWhat else can I do for you?",
                                           reply_markup=REPORTS_KEYBOARD)
        elif query.data == 'get_all_reports':
            self.logger.info(
                f"Get All Reports: Reading data from range {self.sheet_range} of the Spreadsheet {self.sheet_id}\n")
            await query.edit_message_text(text="🤖: Retrieving data from Google. Please wait...")

            data = self.sheetsHelper.get_sheet_data(self.sheet_id, self.sheet_range)

            # Create dict with objects to send
            objects_to_send = dict()
            objects_to_send["Open Positions"] = format_df(data, style='positions')
            objects_to_send["Watchlist"] = format_df(data, style='watchlist')

            for title, dataframe in objects_to_send.items():
                await self.send_dataframe(context, update.effective_chat.id, dataframe, fmt="simple", title=title)

            await query.message.reply_text(text="🤖: There you go, you unsaciable beast\nWhat else can I do for you?",
                                           reply_markup=REPORTS_KEYBOARD)
        elif query.data == 'return':
            await query.edit_message_text('🤖: What else can I do for you?', reply_markup=MAIN_KEYBOARD)

    def setup_handlers(self):
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CallbackQueryHandler(self.button))

    async def send_dataframe(self, context, chat_id, dataframe, fmt="simple", title=None):
        table = dataframe.to_markdown(tablefmt=fmt)

        if title:
            title_str = f"<b>{title}</b>\n\n"
        else:
            title_str = ""

        message = title_str + f"<pre>{table}</pre>"

        # Use context.bot to send the message
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML'
        )

    def run(self):
        self.application.run_polling()


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

    labels = ['Stop Loss', 'Details', 'Prices of interest', 'Approx loss', 'Exchange', 'Stock Name']
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

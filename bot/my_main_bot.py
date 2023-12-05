import sys

sys.path.append("..")  # Add the parent directory to sys.path
import logging, asyncio
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from .keyboard_layouts import MAIN_KEYBOARD, RETURN_KEYBOARD, REPORTS_KEYBOARD
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
        try:
            await query.answer()

            if query.data in ['get_open_pos', 'get_watchlist', 'get_all_reports']:
                await self.handle_report_request(context, query, query.data)
            elif query.data == 'get_reports':
                await query.edit_message_text(text="🤖: Choose which report you want to get.",
                                              reply_markup=REPORTS_KEYBOARD)
            elif query.data == 'analyze_trade':
                await query.edit_message_text(text="🤖: Sorry this isn't ready yet",
                                              reply_markup=RETURN_KEYBOARD)
            elif query.data == 'return':
                await query.edit_message_text(text='🤖: What else can I do for you?',
                                              reply_markup=MAIN_KEYBOARD)
        except Exception as e:
            self.logger.error(f"Something failed while processing: {e}")
            await query.edit_message_text(text='⚠️ Sorry but something failed while processing query.\n'
                                               '🤖: What else can I do for you?',
                                          reply_markup=MAIN_KEYBOARD)

    async def handle_report_request(self, context, query, report_type):
        self.logger.info(f"Reading data from range {self.sheet_range} of the Spreadsheet {self.sheet_id}\n")
        await query.edit_message_text(text="🤖: Retrieving data from Google. Please wait...")

        try:
            data = self.sheetsHelper.get_sheet_data(self.sheet_id, self.sheet_range)

            # Process data based on report_type
            objects_to_send = {
                "Open Positions": format_df(data, style='positions') if report_type in ['get_open_pos',
                                                                                        'get_all_reports'] else None,
                "Watchlist": format_df(data, style='watchlist') if report_type in ['get_watchlist',
                                                                                   'get_all_reports'] else None
            }

            # Send data
            for title, dataframe in objects_to_send.items():
                if dataframe is not None:
                    await send_dataframe(context, query.message.chat_id, dataframe, fmt="simple", title=title)

            # Follow-up message
            follow_up_text = {
                'get_open_pos': "Here are your positions pal",
                'get_watchlist': "Here is your Watchlist mate",
                'get_all_reports': "There you go, you insatiable beast",
            }.get(report_type, "What else can I do for you?")

            await query.message.reply_text(text=f"🤖: {follow_up_text}\nWhat else can I do for you?",
                                           reply_markup=REPORTS_KEYBOARD)
        except Exception as e:
            self.logger.error(f"Something failed while processing: {e}")
            await query.edit_message_text(text='⚠️ Sorry but something failed while processing query.\n'
                                               '🤖: What else can I do for you?',
                                          reply_markup=REPORTS_KEYBOARD)
            
    def setup_handlers(self):
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CallbackQueryHandler(self.button))

    def run(self):
        self.application.run_polling()


def escape_chars(s):
    if s is None:
        return s  # or return an empty string or some placeholder text as appropriate
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


async def send_dataframe(context, chat_id, dataframe, fmt="simple", title=None):

    if title:
        title = escape_chars(title)
        title_str = f"<b>{title}</b>\n\n"
    else:
        title_str = ""

    # Apply the escape function to the dataframe content if necessary
    dataframe = dataframe.applymap(escape_chars)

    table = dataframe.to_markdown(tablefmt=fmt)
    message = title_str + f"<pre>{table}</pre>"

    # Use context.bot to send the message
    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode='HTML'
    )


def format_df(data, style="general"):
    if not data or not isinstance(data, list) or not all(isinstance(row, list) for row in data):
        raise ValueError("Invalid data format received")

    # Ensure there is more than one row (one for the header, at least one for the data)
    if len(data) < 2:
        raise ValueError("No data available to format")

    # Create DataFrame from data
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

    # Reset the index without adding a new column
    df.reset_index(drop=True, inplace=True)

    return df

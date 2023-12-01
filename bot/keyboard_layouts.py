from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Define keyboards
MAIN_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("📊 Get Reports", callback_data='get_reports')],
    [InlineKeyboardButton("📈 Analyze Trade", callback_data='analyze_trade')]
])

RETURN_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("◀️ Return", callback_data='return')]
])

REPORTS_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("💰 Open Positions", callback_data='get_open_pos'),
     InlineKeyboardButton("🤑 Watchlist", callback_data='get_watchlist')],
    [InlineKeyboardButton("🤨 Get all reports", callback_data='get_all_reports'), InlineKeyboardButton("◀️ Return", callback_data='return')]
])


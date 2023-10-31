from telegram import Bot  # This import assumes you're using an async-compatible library.
from telegram.error import TelegramError
import aiofiles  # Ensure you've installed this package, it's for async file reading.


class TelegramNotifier:
    """
    A helper class for sending messages to a Telegram group.
    """

    def __init__(self, bot_token):
        """
        Initializes the TelegramNotifier object.

        :param bot_token: str - The token of the Telegram bot.
        """
        self.bot_token = bot_token

    async def send_message(self, chat_id, message, disable_web_page_preview=True):
        """
        Sends a message to a specified chat.

        :param chat_id: str - The ID of the chat to send a message to.
        :param message: str - The message text to send.
        :param disable_web_page_preview: bool - Whether to disable URL previews for links in the message.
        """
        async with Bot(token=self.bot_token) as bot:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                disable_web_page_preview=disable_web_page_preview,
            )

    async def send_dataframe(self, chat_id, dataframe, fmt="simple", title=None):
        """
        Sends a dataframe as a formatted table to a specified chat.

        :param chat_id: str - The ID of the chat to send the table to.
        :param dataframe: pandas.DataFrame - The DataFrame to send.
        """
        # Convert DataFrame to a nicely formatted table text
        table = dataframe.to_markdown(tablefmt=fmt)

        # If a title was provided, add it above the table with some formatting
        if title:
            # You can format this title string to fit your needs
            title_str = f"<b>{title}</b>\n\n"
        else:
            title_str = ""

        # Prepare the message text, ensuring that Markdown formatting is preserved
        message = title_str + f"<pre>{table}</pre>"

        # Use the same bot instance to send the message
        bot = Bot(token=self.bot_token)
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML',  # This will allow correct rendering of the <pre> tags
        )

    async def send_image(self, chat_id, image_path):
        """
        Sends an image to a Telegram chat.

        :param chat_id: str - The ID of the Telegram chat.
        :param image_path: str - Filepath of the image to send.
        """
        # Use async with for aiofiles to read the file, as we're in an async function.
        async with aiofiles.open(image_path, 'rb') as photo_file:
            photo = await photo_file.read()

            # Use async with for the bot, consistent with how it's used in send_message.
            async with Bot(token=self.bot_token) as bot:
                try:
                    # Sending photo after reading it.
                    await bot.send_photo(chat_id=chat_id, photo=photo)
                except TelegramError as e:
                    print(f"An error occurred while sending the image to Telegram: {e}")

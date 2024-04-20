import logging
from datetime import datetime

import requests

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters



# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("TEST")


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Parse user input (/summary country [optional_date])
    text = update.message.text.split()
    if len(text) < 2 or len(text) > 3:
        await update.message.reply_text(
            "Please provide the country name after /summary command, followed by an optional date in the format YYYY-MM-DD.\n"
            "Example: /summary russia 2020-01-01 ")
        return

    country = text[1].capitalize()  # Capitalize the first letter of the country name
    date = text[2] if len(text) == 3 else datetime.now().strftime(
        "%Y-%m-%d")  # Use current date if date is not provided

    params = {"country": country}
    API_URL = 'https://api.api-ninjas.com/v1/covid19?country={}'.format(country)
    response = requests.get(API_URL, headers={'X-Api-Key': 'drrVI/f+ip+JcLT3Mly0vg==R2ktfeflGCrUQ4lk'})

    if response.status_code != 200:
        await update.message.reply_text("Failed to fetch data from the COVID-19 API.")
        return

    data = response.json()

    if not data:
        await update.message.reply_text("No data available for the specified country.")
        return

    country_data = data[0]
    cases_data = country_data.get("cases", {})

    total_cases = 0
    total_deaths = 0
    for date_str, case_data in cases_data.items():
        if date_str <= date:
            total_cases += case_data["total"]
            total_deaths += case_data["new"]

    # Format and send the summary to the user
    summary_message = (
        f"Summary for {country} up to {date}:\n"
        f"Total Cases: {total_cases}\n"
        f"Total Deaths: {total_deaths}\n"
    )
    await update.message.reply_text(summary_message)


def main() -> None:
    application = Application.builder().token("7019728106:AAGCAw57DKgWhHfAUIjyP5iL3cUsCfB22uI").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("summary", summary))


    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

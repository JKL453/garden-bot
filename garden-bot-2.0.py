# Import some useful packages
import os
import psycopg2
import logging, datetime, pytz
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater, 
    CommandHandler,
    ConversationHandler, 
    MessageHandler, 
    Filters,
    CallbackContext
)
from modules.YrUtils import WeatherReport
from modules.dbUtils import BotDatabase

# Check if garden-bot is run locally or on heroku
# If run locally import config vars form config file
if 'DYNO' in os.environ:
    debug = False
else:
    debug = True
    from modules.config import (
        BOT_TOKEN,
        WEBHOOK_URL,
        MY_CHAT_ID,
        MY_LOCATION,
        DATABASE_URL,
        UA_SITENAME
    )

# Import config variables
PORT = int(os.environ.get('PORT', 5000))
if debug == False:
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
    MY_CHAT_ID = os.environ.get('MY_CHAT_ID')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    MY_LOCATION = os.environ.get('MY_LOCATION')

# Specify timezone and create a datetime object
my_timezone = pytz.timezone("Europe/Berlin")
my_date = datetime.datetime.now(my_timezone)

time_now = datetime.datetime.now(pytz.timezone("Europe/Berlin"))
date_today  = time_now.replace(hour=6, minute=0)

wr = WeatherReport(location=MY_LOCATION, date=time_now)

date_tomorrow, date_after_tomorrow = WeatherReport.get_next_dates()

# Connect to your postgres DB (deprecated)
#conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# Initialize database object and connect to BotDatabase 
db = BotDatabase()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------- #
#      Conversation Handler       #   
# ------------------------------- # 

# Define states for ConversationHandler
GET_NAME, VERIFY_NAME, REGISTER_USER, VERIFY_USER, ID_IN_DB, OFFER_HELP = map(chr, range(0,6))

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    
    # Get users list from database
    users = db.get_all_users()
    
    # At first, check if user is already in database
    # Get chat_ids from database
    chat_ids = []
    names = []
    for user in users:
       chat_ids.append(user[1])
       names.append(user[2])
    
    # If user is already registered as a garden friend
    if update.message.chat_id in chat_ids:
        
        # Find name that belongs to chat_id
        garden_friend_name = names[chat_ids.index(update.message.chat_id)]
        
        reply = (
            "Moin " + garden_friend_name +
            ". Wir kennen uns schon, und du bist schon als User registriert. "
            "Deine chat_id lautet: " + str(update.message.chat_id) + ".\n"
            "Wie kann ich dir sonst noch weiterhelfen?"
        )
        
        reply_keyboard = [
            ['Hilfe', 'Wetterbericht'], # keyboard needs to be removed or is always shown
            ['Abbruch']
        ]
    
    # If user is not registered as a garden friend yet    
    else:
        reply = (
            "Hi, ich bin Gardenbot. \n"
            "Du bist scheinbar noch nicht als User registriert. \n"
            "Wenn du dich registrierst, kann ich dir in Zukunft Wettervorhersagen schicken "
            "und dich ans Gießen erinnern. \n"
            "Was möchtest du tun?"
        )
        reply_keyboard = [
            ['Registrieren'],
            ['Abbruch']
        ]
    
    update.message.reply_text(
        reply,
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    
    return GET_NAME

def ask_name(update: Update, context: CallbackContext):
    
    # Ask user for his name
    update.message.reply_text(
        "Wie heißt du?"
    )
    
    return VERIFY_NAME 

def verify_name(update: Update, context: CallbackContext):
    
    entered_name = update.message.text
    users = db.get_all_users()
    
    context.user_data['name'] = entered_name
    context.user_data['chat_id'] = update.message.chat_id
    
     # Get names from database
    names = []
    for user in users:
       names.append(user[2])
       
    if entered_name in names:
        reply = (
            ". Super, ich konnte deinen Namen in der Datenbank finden. \n"
            "Möchtest du dich jetzt registrieren?"
        )
        
        reply_keyboard = [
            ['Ja', 'Nein']
        ]
        
        update.message.reply_text(
            "Hi " + entered_name + reply,
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        
        return REGISTER_USER
        
    else:
        reply = (
            ". Ich konnte diesen Namen nicht in der Datenbank finden. \n"
            "Bitte gib deinen ersten Vornamen an, keine Spitznamen."
        )
        update.message.reply_text(
            "Hi " + entered_name + reply
        ) 

        return VERIFY_NAME
    
    
def get_name(update: Update, context: CallbackContext):
    name = update.message.text
    users = db.get_all_users()
    
    context.user_data['name'] = name
    context.user_data['chat_id'] = update.message.chat_id
    
     # Get names from database
    names = []
    for user in users:
       names.append(user[2])
    
    # Get chat_ids from database
    chat_ids = []
    for user in users:
       chat_ids.append(user[1])
    
    if update.message.chat_id in chat_ids:
        reply = (
            ". Wir kennen uns schon, und du bist schon als User registriert. "
            "Deine chat_id lautet: " + str(update.message.chat_id) + ".\n"
            "Wie kann ich dir sonst noch weiterhelfen?"
        )
        
        reply_keyboard = [
            ['Hilfe', 'Wetterbericht'], # keyboard needs to be removed or is always shown
            ['Abbruch']
        ]
        
    else:
        reply = (
            ". Wir kennen uns noch nicht. "
            "Wenn du möchtest kannst du dich jetzt registrieren "
            "und in Zukunft meine Dienste in Anspruch nehmen."
        )
        reply_keyboard = [
            ['Registrieren'],
            ['Abbruch']
        ]
    
    update.message.reply_text(
         "Hi " + name + reply,
         reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    ) 
     
    return VERIFY_NAME

def register_user(update: Update, context: CallbackContext):
    # Trage chat_id in Datenbank ein
    user_name = context.user_data['name']
    user_chat_id = context.user_data['chat_id']
    
    db.write_database(user_name, user_chat_id)
    
    reply_keyboard = [
            ['Hilfe', 'Wetterbericht'], # keyboard needs to be removed or is always shown
            ['Abbruch']
    ]
    
    update.message.reply_text(
         "Herzlichen Glückwunsch! "
         "Du wurdest erfolgreich in die Datenbank aufgenommen. \n"
         "Wie kann ich dir sonst noch weiterhelfen?",
         reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    ) 
    
    # hier muss noch ein Verweis auf die Funktionen hin
    
    return ConversationHandler.END

def done(update: Update, context: CallbackContext):
    # Abbruch der Unterhaltung
    update.message.reply_text(
        "Ok, bis zum nächsten mal!",
        reply_markup = ReplyKeyboardRemove()
    )
    
    return ConversationHandler.END
    
def set_name(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'Hallo ' 
        + update.message.text
    ) 
    
def help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        "Wenn du registriert bist, sende ich dir jeden morgen um 10:00 Uhr "
        "die aktuelle Wettervorhersage und eine Gieß-Erinnerung.\n \n"
        "Außerdem kannst du folgende Befehle senden: \n"
        "/forecast - den aktuellen Wetterbericht anfordern \n"
        "/cancel - den aktuellen Dialog abbrechen \n \n"
        "Wenn du genauer wissen möchtest, wie ich funktioniere, "
        "kannst du hier nachschauen: www.github.com"
    )
    
    return ConversationHandler.END

def send_forecast(update: Update, context: CallbackContext): 
    """Send a message when the command /forecast is issued."""
    # Send forecast
    
    forecast = wr.get_weather_data()

    weather_tomorrow = wr.weather_from_time(date_tomorrow, return_repr='str')
    
    weather_msg = wr.daily_forecast(date_tomorrow)
    #print(weather_msg)

    """
    forecast = get_forecast()
    bot.send_message(
        chat_id=chat_id,
        text=forecast
    )
    """
    update.message.reply_text(
        text=weather_msg
    )  

# ------------------------------- #
#    Conversation Handler End     #   
# ------------------------------- # 

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

     # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(Filters.regex('^Hilfe$'), help),
            MessageHandler(Filters.regex('^Wetterbericht$'), send_forecast),
            MessageHandler(Filters.regex('^Abbruch$'), done)
        ],
        states={
            GET_NAME: [
                MessageHandler(Filters.regex('^Hilfe$'), help),
                MessageHandler(Filters.regex('^Wetterbericht$'), send_forecast),
                MessageHandler(Filters.regex('^Registrieren$'), ask_name),
                MessageHandler(Filters.regex('^Abbruch$'), done)
            ],
            VERIFY_NAME: [
                MessageHandler(Filters.text, verify_name),
            ],
            REGISTER_USER: [
                MessageHandler(Filters.regex('^Ja'), register_user),
                MessageHandler(Filters.regex('^Nein'), done),
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^Abbruch$'), done)],
    )
    
    # on different commands - answer in Telegram
    #dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("forecast", send_forecast))
    #dp.add_handler(CommandHandler("db_test", db_test))
    dp.add_handler(conv_handler)

    users = db.get_all_users()
    watering_user_id = db.get_water_person()
    for user in users:
        if user[0] == watering_user_id:
            watering_user_name = user[2]
    
     # Check if time is 10:00 and if true, send daily reminder for watering of plants
     # waking up the scheduler might take up to 1 minute,
     # therefore my_date.minute is compared to 2 or equal
    if my_date.hour == 10 and my_date.minute <= 1:
        morning_forecast = (
            "GardenBot meldet sich zum Dienst\.\n"
            "Es ist jetzt 10:00 Uhr morgens\.\n"
            "Hier die Wettervorhersage für heute, den " 
            + str(my_date.today().day) + "\." 
            + str(my_date.today().month) + "\." 
            + str(my_date.today().year) + ":\n \n"
            + send_forecast() + "\n \n"
            "Wasserdienst heute: {}".format(watering_user_name)
        )
        
        chat_ids = []
        for user in users:
            chat_ids.append(user[1])
        
        if debug == False:
            for chat_id in chat_ids:
                if chat_id != None:
                    updater.bot.send_message(
                        chat_id=chat_id, 
                        text=morning_forecast, 
                        parse_mode='MarkdownV2'
                    )
        
        else:
            updater.bot.send_message(
                        chat_id=MY_CHAT_ID, 
                        text=morning_forecast, 
                        parse_mode='MarkdownV2'
                    )
                    
    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    if debug == True:
        updater.start_polling()
    else:
        updater.start_webhook(
            listen = "0.0.0.0",
            port = int(PORT), 
            url_path = BOT_TOKEN
        )
        updater.bot.setWebhook(WEBHOOK_URL + BOT_TOKEN)
    
    updater.idle()

if __name__ == '__main__':
    main()
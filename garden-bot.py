# GardenBot

# Import some useful packages
import os
import psycopg2
from yr.libyr import Yr
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

# Check if garden-bot is run locally or on heroku
# If run locally import config vars form config file
if 'DYNO' in os.environ:
    debug = False
else:
    debug = True
    from config import (
        BOT_TOKEN,
        WEBHOOK_URL,
        MY_CHAT_ID,
        MY_LOCATION,
        DATABASE_URL
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

# Connect to your postgres DB
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define states for ConversationHandler
GET_NAME, VERIFY_NAME, REGISTER_USER, VERIFY_USER, ID_IN_DB, OFFER_HELP = map(chr, range(0,6))

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    
    # Get users list from database
    users = read_database(conn)
    
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
    users = read_database(conn)
    
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
    users = read_database(conn)
    
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
    
    write_database(conn, user_name, user_chat_id)
    
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
    
def set_name(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'Hallo ' 
        + update.message.text
    ) 
    
def help(update, context):
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
    
def db_test(update, context):
    read_database(conn)
    update.message.reply_text('Reading db...')
    
def forecast(update, context):
    
    introduction = (
        "Wetterbericht für heute\, den " 
        + str(my_date.today().day) +"\." 
        + str(my_date.today().month) +"\." 
        + str(my_date.today().year) + ",\nund Folgetag: \n\n"
    )
    
    update.message.reply_text(
        introduction + get_forecast(), parse_mode='MarkdownV2'
    )

def send_forecast(update: Update, context: CallbackContext):
    
    introduction = (
        "Wetterbericht für heute\, den " 
        + str(my_date.today().day) +"\." 
        + str(my_date.today().month) +"\." 
        + str(my_date.today().year) + ",\nund Folgetag: \n\n"
    )
    
    update.message.reply_text(
        introduction + get_forecast(), parse_mode='MarkdownV2'
    )
    
    return ConversationHandler.END 

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
    dp.add_handler(CommandHandler("forecast", forecast))
    dp.add_handler(CommandHandler("db_test", db_test))
    dp.add_handler(conv_handler)

    users = read_database(conn)
    watering_user_id = get_water_person(conn)
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
            + get_forecast() + "\n \n"
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

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.

def get_yr_weather():
    # Get weather data from https://www.yr.no/
    weather = Yr(location_name=MY_LOCATION)
    
    # Get temperature data
    temperature = dict()
    temperature['data'] = [{'from': forecast['@from'], 'to': forecast['@to'], 'temperature': float(forecast['temperature']['@value'])} for forecast in weather.forecast()]

    # Get rain data
    rain = dict()
    rain['data'] = [{'from': forecast['@from'], 'to': forecast['@to'], 'rain': float(forecast['precipitation']['@value'])} for forecast in weather.forecast()]
    
    # Build forecast string
    forecast_string = "Wetterbericht für heute\, den " + str(my_date.today().day) +"\." + str(my_date.today().month) +"\." + str(my_date.today().year) +":\n \n" 
    forecast_string += "*Temperatur\(°C\):*\n " 
    forecast_string += "```"
    forecast_string += "  " + str(round(temperature['data'][0]['temperature'])) 
    forecast_string += "``` \n"
    
    forecast_string += "*Regen\(mm\):*\n " 
    forecast_string += "```"
    forecast_string += "  " + str(round(rain['data'][0]['rain'])) 
    forecast_string += "```" 
    
    # Fetching day times
    #for item in range(0,4):
     #   print(str(temperature['data'][item]['from']) + " " + str(temperature['data'][item]['to']))
    
    #for forecast in weather.forecast():
    #    print(forecast)
    
    return forecast_string
    
def get_forecast():
    # Call Yr API twice to make sure the final call contains current weather data
    weather_data_temp0=Yr(location_name=MY_LOCATION)
    weather_data_temp1=Yr(location_name=MY_LOCATION)
    weather_data_temp2=Yr(location_name=MY_LOCATION)
    
    # Get current weather data from yr.no
    weather_data=Yr(location_name=MY_LOCATION)
    
    # Read weather forecast data to dictionary
    forecast_data = dict()
    forecast_data['data'] = [{'from': forecast['@from'], 
                              'to': forecast['@to'], 
                              'temperature': float(forecast['temperature']['@value']), 
                              'rain': float(forecast['precipitation']['@value'])} 
                             for forecast in weather_data.forecast()]
    
    # Create forecast message string (markdown)
    forecast_str = "*Uhrzeit                       Temp\.    Regen* ``` \n"
    for item in range(0,4):
        # Get daytime of forecast
        times_from = str(forecast_data['data'][item]['from']).split('T')[1].split(':')[0]
        times_to = str(forecast_data['data'][item]['to']).split('T')[1].split(':')[0]
        
        # Get temperature and rain values
        temperature = int(forecast_data['data'][item]['temperature'])
        rain = int(forecast_data['data'][item]['rain'])
        print(times_from + " bis " + times_to + " Uhr : " + str(temperature) + " °C, " + str(rain) + " mm")
        
        # Create return string
        forecast_str += times_from + " bis " + times_to + " Uhr   " + str(temperature) + "°C    " + str(rain) + " mm \n"
        
    # Prepare string for markdown
    forecast_str += "```" 
    return forecast_str

def read_database(conn):
    
    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a query
    cur.execute("SELECT * FROM users")

    # Retrieve query results
    users = cur.fetchall()    
    
    '''for row in users:
        print("id = ", row[0], )
        print("chat_id = ", row[1])
        print("first_name  = ", row[2], "\n")'''
        
    # Close communication with the database
    cur.close()
    #conn.close()
    
    return users
    
def write_database(conn, user_name, user_chat_id):
    
    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a query
    # (person_id int, chat_id int, first_name varchar)
    sql_command = (
        "UPDATE users "
        "SET chat_id = {chat_id} ".format(chat_id = user_chat_id) +
        "WHERE first_name = '{first_name}';".format(first_name = user_name)
    )
    
    cur.execute(sql_command)
    
    # Make the changes to the database persistent 
    conn.commit()
    
    # Close communication with the database
    cur.close()
    #conn.close()

def get_water_person(conn):
    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a query
    # Update the water_person_id
    
    # das muss besser mit einem Datum verknüpft werden
    # wenn sonst mal einen Tag der Server aussetzt, ist die Reihenfolge im Arsch
    
    sql_read = (
        "SELECT * FROM tasks;"
    )
    
    cur.execute(sql_read)
    
    sql_data = cur.fetchall()
    last_water_person_id = sql_data[0][1]
    last_watering_date = sql_data[0][2]
    
    duration =  datetime.datetime.now().date() - last_watering_date
    days_passed = duration.days
    
    print("days passed: " + str(days_passed))
    
    if last_water_person_id < 7:
        today_water_person_id = last_water_person_id + days_passed
    
    else: 
        today_water_person_id = days_passed-1
    
    sql_update = (
        "UPDATE tasks "
        "SET person_id = {}, ".format(today_water_person_id) +
        "date = '{}'::DATE ".format(datetime.datetime.now().date()) + 
        "WHERE task = 'last_watering';"
    )
    
    #print("today water person id: " + str(today_water_person_id))
    #print("last_water_person_id: " + str(last_water_person_id))
    #print(read_database(conn))
    
    cur.execute(sql_update)
    
    # Make the changes to the database persistent 
    conn.commit()
    
    # Close communication with the database
    cur.close()
    #conn.close()
    
    return today_water_person_id

if __name__ == '__main__':
    main()

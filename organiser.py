from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ContextTypes, ApplicationBuilder, ConversationHandler, filters, MessageHandler
import logging
import os
from dotenv import load_dotenv
from functools import partial
import firebase_admin
from firebase_admin import db
import datetime
#import requests

NAME, ORG, CONTACT = range(3)
EVENT_NAME, TIME, LOCATION, POSTER, LINK = range(5)

#insert token
load_dotenv()
bot = ApplicationBuilder().token(os.environ['ORG_TOKEN']).build()

#firebase
cred = firebase_admin.credentials.Certificate('./serviceAccountKey.json')
app = firebase_admin.initialize_app(cred, {
	'databaseURL':os.environ['FIREBASE_URL']
	})
organisersDB = db.reference('/organisers')

async def toDatabase(userId,var,input):
    nav = organisersDB.child(f"{userId}")
    nav.update({var:input})

async def fromDatabase(userId):
    x = organisersDB.get(shallow=True)
    print(x)





# Command functions
async def start(update, context):
    userId = update.message.from_user.id
    await fromDatabase(userId)
    #if str(user.id) in users:
    # Welcome back

    #else:
    await context.bot.send_message(userId,f"Hello {update.effective_user.first_name}! I'm the Help for All bot <summary>")
    data = {
        userId: {
            "name": "",
            "age": "",
            "gender":"",
            "skills":"",
            "dietary":""
        }
    }
    organisersDB.set(data) #check this again, it overwrites
    await update.message.reply_text("What is your full name?")
    return NAME

async def help(update, context):
    await update.message.reply_text(f"help")

async def pref(update, context):
    pass

async def createEvent(update, context):
    userId = update.message.from_user.id
    await fromDatabase(userId)
    await update.message.reply_text("What is the name of your event?")
    return ConversationHandler.END

async def save(update, context, var:str):
    userId = update.message.from_user.id
    input = update.message.text

    await toDatabase(userId,var,input)

    if var == "name":
        await update.message.reply_text("What is the name of your organisation?")
        return ORG
    elif var == "org":
        await update.message.reply_text("What is your contact number?")
        return CONTACT
    elif var == "contact":
        return ConversationHandler.END
    else:
        await update.message.reply_text("I don't understand")
        return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text("Ok, cancelling setup. Use /start to start again.")
    return ConversationHandler.END


start_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states = {
        NAME: [MessageHandler(filters.TEXT, partial(save, var="name"))],
        ORG: [MessageHandler(filters.TEXT, partial(save, var="org"))],
        CONTACT: [MessageHandler(filters.TEXT, partial(save, var="contact"))]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

event_handler = ConversationHandler(
    entry_points=[CommandHandler('create', createEvent)],
    states = {
        EVENT_NAME: [MessageHandler(filters.TEXT, partial(save, var="eventName"))],
        TIME: [MessageHandler(filters.TEXT, partial(save, var="time"))],
        LOCATION: [MessageHandler(filters.TEXT, partial(save, var="location"))],
        POSTER: [MessageHandler(filters.TEXT, partial(save, var="poster"))],
        LINK: [MessageHandler(filters.TEXT, partial(save, var="link"))]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)



#Load commands
bot.add_handler(start_handler)
bot.add_handler(CommandHandler("help", help))


bot.run_polling()
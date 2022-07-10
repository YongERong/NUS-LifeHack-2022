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

NAME, AGE, GENDER, DIETARY, SKILLS = range(5)

#insert token
load_dotenv()
bot = ApplicationBuilder().token(os.environ['VOL_TOKEN']).build()

#firebase
cred = firebase_admin.credentials.Certificate('./serviceAccountKey.json')
app = firebase_admin.initialize_app(cred, {
	'databaseURL':os.environ['FIREBASE_URL']
	})
ref = db.reference('volunteers')

async def toDatabase(userId,var,input):
    nav = ref.child(f"{userId}")
    nav.update({var:input})

async def fromDatabase(userId):
    x = ref.get(shallow=True)
    print(x)

# events push
# detect new event




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
    ref.set(data) #check this again, it overwrites
    await update.message.reply_text("What is your full name?")
    return NAME

async def help(update, context):
    await update.message.reply_text(f"help")

async def pref(update, context):
    pass

async def save(update, context, var:str):
    userId = update.message.from_user.id
    input = update.message.text

    await toDatabase(userId,var,input)

    if var == "name":
        await update.message.reply_text("How old are you?")
        return AGE
    elif var == "age":
        await update.message.reply_text("What is your gender?")
        return GENDER
    elif var == "gender":
        await update.message.reply_text("What skills do you wish to contribute?")
        return SKILLS
    elif var == "skills":
        await update.message.reply_text("Do you have any dietary requirements?")
        return DIETARY
    elif var == "dietary":
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
        AGE: [MessageHandler(filters.TEXT, partial(save, var="age"))],
        GENDER: [MessageHandler(filters.TEXT, partial(save, var="gender"))],
        SKILLS: [MessageHandler(filters.TEXT, partial(save, var="skills"))],
        DIETARY: [MessageHandler(filters.TEXT, partial(save, var="dietary"))]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)



#Load commands
bot.add_handler(start_handler)
bot.add_handler(CommandHandler("help", help))


bot.run_polling()
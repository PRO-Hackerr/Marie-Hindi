from io import BytesIO
from time import sleep
from typing import Optional, List
from telegram import TelegramError, Chat, Message
from telegram import Update, Bot
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async
from tg_bot.modules.helper_funcs.chat_status import is_user_ban_protected, bot_admin

import tg_bot.modules.sql.users_sql as sql
from tg_bot import dispatcher, OWNER_ID, LOGGER
from tg_bot.modules.helper_funcs.filters import CustomFilters

USERS_GROUP = 4


@run_async
def quickscope(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = str(args[1])
        to_kick = str(args[0])
    else:
        update.effective_message.reply_text("आप किसी यूजर को टैग नहीं कर रहे हैं")
    try:
        bot.kick_chat_member(chat_id, to_kick)
        update.effective_message.reply_text( + to_kick + "को" + chat_id "से निकाल दिया गया")
    except BadRequest as excp:
        update.effective_message.reply_text(excp.message + " " + to_kick)


@run_async
def quickunban(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = str(args[1])
        to_kick = str(args[0])
    else:
        update.effective_message.reply_text("आप किसी यूजर को टैग नहीं कर रहे हैं")
    try:
        bot.unban_chat_member(chat_id, to_kick)
        update.effective_message.reply_text(+ to_kick + " को" + chat_id "से निकाल दिया गया)
    except BadRequest as excp:
        update.effective_message.reply_text(excp.message + " " + to_kick)


@run_async
def banall(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = str(args[0])
        all_mems = sql.get_chat_members(chat_id)
    else:
        chat_id = str(update.effective_chat.id)
        all_mems = sql.get_chat_members(chat_id)
    for mems in all_mems:
        try:
            bot.kick_chat_member(chat_id, mems.user)
            update.effective_message.reply_text(+ str(mems.user) "को हटाने की कोशिश की")
            sleep(0.1)
        except BadRequest as excp:
            update.effective_message.reply_text(excp.message + " " + str(mems.user))
            continue


@run_async
def snipe(bot: Bot, update: Update, args: List[str]):
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError as excp:
        update.effective_message.reply_text("कृपया मुझे इको करने के लिए एक चैट दें")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            bot.sendMessage(int(chat_id), str(to_send))
        except TelegramError:
            LOGGER.warning("Couldn't send to group %s", str(chat_id))
            update.effective_message.reply_text("मैसेज नहीं भेज सका। शायद मैं उस ग्रुप का हिस्सा नहीं हूं?")


@run_async
@bot_admin
def getlink(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = int(args[0])
    else:
        update.effective_message.reply_text("आप किसी यूजर को टैग नहीं कर रहे हैं")
    chat = bot.getChat(chat_id)
    bot_member = chat.get_member(bot.id)
    if bot_member.can_invite_users:
        invitelink = bot.get_chat(chat_id).invite_link
        update.effective_message.reply_text(invitelink)
    else:
        update.effective_message.reply_text("मुझे इन्विते लिंक तक पहुंच नहीं है!")


@bot_admin
def leavechat(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = int(args[0])
        bot.leaveChat(chat_id)
    else:
        update.effective_message.reply_text("आप किसी यूजर को टैग नहीं कर रहे हैं")

__help__ = """
**Owner only:**
- /getlink **chatid**: इन्विते लिंक जानने के लिए
- /banall: सभी सदस्यों को चैट से निकालें
- /leavechat **chatid** : ग्रुप छोड़ो
**Sudo/owner only:**
- /quickscope **userid** **chatid**: यूजर उपयोगकर्ता चैट से प्रतिबंध.
- /quickunban **userid** **chatid**: प्रतिबंध हटाए.
- /snipe **chatid** **string**: मुझे एक विशिष्ट चैट के लिए एक संदेश भेजें.
- /rban **userid** **chatid** दूर से एक यूजर चैट से हटा दें
- /runban **userid** **chatid** प्रतिबंध हटाए.
- /Stats: बॉट की स्थिति की जाँच करें
- /chatlist: चैटलिस्ट प्राप्त करें
- /gbanlist: gbanned यूजर सूची प्राप्त करें
- /gmutelist: gmuted यूजर सूची प्राप्त करें
- Chat bans via /restrict chat_id and /unrestrict chat_id commands
**Support user:**
- /Gban : Global ban a user
- /Ungban : Ungban a user
- /Gmute : Gmute a user
- /Ungmute : Ungmute a user
Sudo/owner can use these commands too.
**Users:**
- /listsudo Gives a list of sudo users
- /listsupport gives a list of support users
"""
__mod_name__ = "Special"

SNIPE_HANDLER = CommandHandler("snipe", snipe, pass_args=True, filters=CustomFilters.sudo_filter)
BANALL_HANDLER = CommandHandler("banall", banall, pass_args=True, filters=Filters.user(OWNER_ID))
QUICKSCOPE_HANDLER = CommandHandler("quickscope", quickscope, pass_args=True, filters=CustomFilters.sudo_filter)
QUICKUNBAN_HANDLER = CommandHandler("quickunban", quickunban, pass_args=True, filters=CustomFilters.sudo_filter)
GETLINK_HANDLER = CommandHandler("getlink", getlink, pass_args=True, filters=Filters.user(OWNER_ID))
LEAVECHAT_HANDLER = CommandHandler("leavechat", leavechat, pass_args=True, filters=Filters.user(OWNER_ID))

dispatcher.add_handler(SNIPE_HANDLER)
dispatcher.add_handler(BANALL_HANDLER)
dispatcher.add_handler(QUICKSCOPE_HANDLER)
dispatcher.add_handler(QUICKUNBAN_HANDLER)
dispatcher.add_handler(GETLINK_HANDLER)
dispatcher.add_handler(LEAVECHAT_HANDLER)

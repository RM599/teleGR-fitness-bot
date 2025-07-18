import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes
)

# مراحل گفتگو
AGE, GENDER, GOAL, LEVEL, DAYS, LOCATION = range(6)

# تولید برنامه تمرینی و غذایی
def generate_ai_plan(data):
    age = data['age']
    gender = data['gender']
    goal = data['goal']
    level = data['level']
    days = int(data['days'])
    location = data['location']

    workout = f"🏋️‍♂️ برنامه تمرینی برای {days} روز در هفته:\n"
    for i in range(1, days + 1):
        workout += f"\nروز {i}:\n"
        if goal == "چربی‌سوزی":
            workout += "- هوازی سبک + تمرینات با وزن بدن\n"
        elif goal == "حجم‌گیری":
            workout += "- تمرینات قدرتی با وزنه\n"
        elif goal == "قدرت":
            workout += "- تمرینات سنگین با وزنه بالا\n"
        workout += f"- سطح: {level} | محل تمرین: {location}\n"

    nutrition = f"\n🍽️ برنامه غذایی پیشنهادی:\n"
    if goal == "چربی‌سوزی":
        nutrition += "- کالری کنترل‌شده با پروتئین بالا\n- حذف قندهای ساده\n"
    elif goal == "حجم‌گیری":
        nutrition += "- افزایش کالری با کربوهیدرات پیچیده\n- مصرف پروتئین بعد تمرین\n"
    elif goal == "قدرت":
        nutrition += "- پروتئین بالا + چربی سالم\n- وعده‌های منظم\n"

    return workout + nutrition

# هندلرها
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("زیر ۲۰", callback_data='زیر ۲۰')],
        [InlineKeyboardButton("۲۰ تا ۳۰", callback_data='۲۰ تا ۳۰')],
        [InlineKeyboardButton("۳۰ تا ۴۰", callback_data='۳۰ تا ۴۰')],
        [InlineKeyboardButton("بالای ۴۰", callback_data='بالای ۴۰')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_chat.send_message("سن شما چقدر است؟", reply_markup=reply_markup)
    return AGE

async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['age'] = query.data
    keyboard = [[InlineKeyboardButton("مرد", callback_data='مرد')],
                [InlineKeyboardButton("زن", callback_data='زن')]]
    await query.edit_message_text("جنسیت شما چیست؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return GENDER

async def gender_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['gender'] = query.data
    keyboard = [[InlineKeyboardButton("چربی‌سوزی", callback_data='چربی‌سوزی')],
                [InlineKeyboardButton("حجم‌گیری", callback_data='حجم‌گیری')],
                [InlineKeyboardButton("قدرت", callback_data='قدرت')]]
    await query.edit_message_text("هدف تمرینی شما چیست؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return GOAL

async def goal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['goal'] = query.data
    keyboard = [[InlineKeyboardButton("مبتدی", callback_data='مبتدی')],
                [InlineKeyboardButton("متوسط", callback_data='متوسط')],
                [InlineKeyboardButton("حرفه‌ای", callback_data='حرفه‌ای')]]
    await query.edit_message_text("سطح تمرینی شما چیست؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return LEVEL

async def level_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['level'] = query.data
    keyboard = [[InlineKeyboardButton("۲ روز", callback_data='2')],
                [InlineKeyboardButton("۳ روز", callback_data='3')],
                [InlineKeyboardButton("۴ روز", callback_data='4')],
                [InlineKeyboardButton("۵ روز", callback_data='5')]]
    await query.edit_message_text("چند روز در هفته تمرین می‌کنید؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return DAYS

async def days_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['days'] = query.data
    keyboard = [[InlineKeyboardButton("باشگاه", callback_data='باشگاه')],
                [InlineKeyboardButton("خانه", callback_data='خانه')]]
    await query.edit_message_text("تمرین شما در باشگاه است یا خانه؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return LOCATION

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['location'] = query.data
    summary = f"""✅ اطلاعات شما:
سن: {context.user_data['age']}
جنسیت: {context.user_data['gender']}
هدف: {context.user_data['goal']}
سطح: {context.user_data['level']}
روزهای تمرین: {context.user_data['days']}
محل تمرین: {context.user_data['location']}
"""
    plan = generate_ai_plan(context.user_data)
    await query.edit_message_text(summary + "\n\n" + plan)
    return ConversationHandler.END

# ساخت اپلیکیشن تلگرام
token = os.getenv("BOT_TOKEN")
app = ApplicationBuilder().token(token).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        AGE: [CallbackQueryHandler(age_handler)],
        GENDER: [CallbackQueryHandler(gender_handler)],
        GOAL: [CallbackQueryHandler(goal_handler)],
        LEVEL: [CallbackQueryHandler(level_handler)],
        DAYS: [CallbackQueryHandler(days_handler)],
        LOCATION: [CallbackQueryHandler(location_handler)],
    },
    fallbacks=[],
)

app.add_handler(conv_handler)

# اجرای بات با polling
if __name__ == "__main__":
    app.run_polling()

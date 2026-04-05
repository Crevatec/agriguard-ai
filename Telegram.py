"""
AgriGuard AI - Telegram Bot v2
Powered by Clevatec
Developed by Olakunle Sunday Olalekan
"""

import logging
import os
import asyncio
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# ── Config ────────────────────────────────────────────────────────────────────

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8795890099:AAEEuGtrfugSwqYdNqk4yVeTkCPN3BVCOY8")
AI_API    = os.environ.get("AI_API", "https://agriguard-ai-a7vf.onrender.com")

logging.basicConfig(level=logging.INFO)

# ── Conversation States ───────────────────────────────────────────────────────

(
    MENU,
    D_CATEGORY, D_CROP, D_WEATHER, D_HUMIDITY, D_RAIN, D_LEAVES,
    Y_CATEGORY, Y_CROP, Y_WEATHER, Y_RAIN, Y_FERT,
    F_CATEGORY, F_CROP, F_SOIL, F_LAST_FERT
) = range(16)

# ── Crop Data ─────────────────────────────────────────────────────────────────

CROP_CATEGORIES = {
    "🌾 Grains & Cereals":    ["Maize", "Rice", "Sorghum", "Millet"],
    "🥔 Tubers & Roots":      ["Cassava", "Yam", "Sweet Potato", "Cocoyam"],
    "🍅 Vegetables & Fruits": ["Tomato", "Pepper", "Onion", "Cabbage"],
    "🌿 Legumes & Beans":     ["Cowpea", "Soybean", "Groundnut", "Beans"],
}

CROP_TO_MODEL = {
    "Maize": "Maize",    "Rice": "Rice",          "Sorghum": "Maize",    "Millet": "Maize",
    "Cassava": "Cassava","Yam": "Cassava",         "Sweet Potato": "Cassava", "Cocoyam": "Cassava",
    "Tomato": "Tomato",  "Pepper": "Tomato",       "Onion": "Tomato",     "Cabbage": "Tomato",
    "Cowpea": "Maize",   "Soybean": "Maize",       "Groundnut": "Maize",  "Beans": "Maize",
}

# ── Conversion Maps ───────────────────────────────────────────────────────────

WEATHER_MAP = {
    "☀️ Very Hot":  38,
    "🌤 Warm":      28,
    "🌥 Cool":      22,
    "🌧 Cold":      16,
}

HUMIDITY_MAP = {
    "💧 Very Wet & Misty":  90,
    "🌫 A Bit Humid":       68,
    "🏜 Dry & Dusty":       35,
}

RAINFALL_MAP = {
    "🌧 Heavy Rain Every Day":       250,
    "🌦 Rain a Few Times a Week":    130,
    "☁️ Light Rain Occasionally":     50,
    "☀️ No Rain At All":              10,
}

SOIL_MAP = {
    "🟤 Very Dark & Rich":  7.0,
    "🟫 Normal Brown Soil": 6.5,
    "⚪ Light Sandy Soil":  5.5,
    "🔴 Red/Laterite Soil": 5.0,
}

LAST_FERT_MAP = {
    "✅ This Season":            50,
    "📅 Last Season":            25,
    "🗓 Over a Year Ago":        10,
    "❌ Never Used Fertilizer":   0,
}

LEAVES_MAP = {
    "💧 Leaves Wet Most of the Day": 18,
    "🌿 Leaves Wet Sometimes":       10,
    "🍂 Leaves Usually Dry":          3,
}

FERT_USAGE_MAP = {
    "🌱 I use a lot of fertilizer":    180,
    "🌿 I use some fertilizer":         100,
    "🍂 I use very little fertilizer":   40,
    "❌ I don't use any fertilizer":      0,
}

# ── Keyboards ─────────────────────────────────────────────────────────────────

def make_keyboard(options):
    keys = [KeyboardButton(o) for o in options]
    rows = [keys[i:i+2] for i in range(0, len(keys), 2)]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)

MAIN_MENU         = make_keyboard([
    "🦠 Check for Disease",
    "🌾 Predict My Harvest",
    "💊 Get Fertilizer Advice",
    "ℹ️ About AgriGuard"
])
CATEGORY_KEYBOARD = make_keyboard(list(CROP_CATEGORIES.keys()))
WEATHER_KEYBOARD  = make_keyboard(list(WEATHER_MAP.keys()))
HUMIDITY_KEYBOARD = make_keyboard(list(HUMIDITY_MAP.keys()))
RAINFALL_KEYBOARD = make_keyboard(list(RAINFALL_MAP.keys()))
SOIL_KEYBOARD     = make_keyboard(list(SOIL_MAP.keys()))
FERT_KEYBOARD     = make_keyboard(list(LAST_FERT_MAP.keys()))
LEAVES_KEYBOARD   = make_keyboard(list(LEAVES_MAP.keys()))
FERT_USAGE_KBD    = make_keyboard(list(FERT_USAGE_MAP.keys()))

def crop_keyboard(category):
    return make_keyboard(CROP_CATEGORIES.get(category, []))

def all_crops():
    return [c for crops in CROP_CATEGORIES.values() for c in crops]

# ── Keep Alive ────────────────────────────────────────────────────────────────

async def keep_alive():
    """Ping the Flask API every 10 minutes to prevent it sleeping."""
    while True:
        try:
            requests.get(AI_API, timeout=10)
            print("✅ Keep-alive ping sent to AI engine")
        except Exception:
            print("⚠️ Keep-alive ping failed — retrying next cycle")
        await asyncio.sleep(600)

# ── Start ─────────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"🌿 Welcome to *AgriGuard AI*, {name}!\n\n"
        f"I am your smart farming assistant.\n\n"
        f"I can help you:\n"
        f"🦠 Detect disease on your crops\n"
        f"🌾 Predict how much you will harvest\n"
        f"💊 Tell you the right fertilizer to use\n\n"
        f"No numbers needed — just tap and answer!\n\n"
        f"What would you like to do today?",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU
    )
    return MENU

# ── Menu ──────────────────────────────────────────────────────────────────────

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data.clear()

    if "Disease" in text:
        await update.message.reply_text(
            "🦠 *Disease Check*\n\n"
            "Question 1️⃣: What *type* of crop are you growing?",
            parse_mode="Markdown",
            reply_markup=CATEGORY_KEYBOARD
        )
        return D_CATEGORY

    elif "Harvest" in text:
        await update.message.reply_text(
            "🌾 *Harvest Prediction*\n\n"
            "Question 1️⃣: What *type* of crop are you growing?",
            parse_mode="Markdown",
            reply_markup=CATEGORY_KEYBOARD
        )
        return Y_CATEGORY

    elif "Fertilizer" in text:
        await update.message.reply_text(
            "💊 *Fertilizer Advice*\n\n"
            "Question 1️⃣: What *type* of crop are you growing?",
            parse_mode="Markdown",
            reply_markup=CATEGORY_KEYBOARD
        )
        return F_CATEGORY

    elif "About" in text:
        await update.message.reply_text(
            "🌿 *About AgriGuard AI*\n\n"
            "AgriGuard AI helps smallholder farmers across Africa "
            "protect their crops and maximize their harvest using "
            "artificial intelligence.\n\n"
            "No expensive equipment needed.\n"
            "No agricultural degree required.\n"
            "Just simple questions and instant answers.\n\n"
            "🌐 Dashboard: https://crevaagriguard-ai.netlify.app\n\n"
            "Powered by *Clevatec*\n"
            "Developed by *Olakunle Sunday Olalekan*",
            parse_mode="Markdown",
            reply_markup=MAIN_MENU
        )
        return MENU

    else:
        await update.message.reply_text(
            "Please choose an option 👇",
            reply_markup=MAIN_MENU
        )
        return MENU

# ════════════════════════════════════════════════════════════════════════════════
# DISEASE FLOW
# ════════════════════════════════════════════════════════════════════════════════

async def d_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat = update.message.text.strip()
    if cat not in CROP_CATEGORIES:
        await update.message.reply_text("Please select a category 👇", reply_markup=CATEGORY_KEYBOARD)
        return D_CATEGORY
    context.user_data['cat'] = cat
    await update.message.reply_text("Question 2️⃣: Which crop specifically?", reply_markup=crop_keyboard(cat))
    return D_CROP

async def d_crop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crop = update.message.text.strip()
    if crop not in all_crops():
        await update.message.reply_text("Please select your crop 👇", reply_markup=crop_keyboard(context.user_data.get('cat','')))
        return D_CROP
    context.user_data['crop'] = crop
    await update.message.reply_text(
        f"Great! You grow *{crop}* 🌱\n\nQuestion 3️⃣: How is the weather today?",
        parse_mode="Markdown", reply_markup=WEATHER_KEYBOARD)
    return D_WEATHER

async def d_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    w = update.message.text.strip()
    if w not in WEATHER_MAP:
        await update.message.reply_text("Please select 👇", reply_markup=WEATHER_KEYBOARD)
        return D_WEATHER
    context.user_data['temp'] = WEATHER_MAP[w]
    await update.message.reply_text("Question 4️⃣: How does the air feel on your farm?", reply_markup=HUMIDITY_KEYBOARD)
    return D_HUMIDITY

async def d_humidity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    h = update.message.text.strip()
    if h not in HUMIDITY_MAP:
        await update.message.reply_text("Please select 👇", reply_markup=HUMIDITY_KEYBOARD)
        return D_HUMIDITY
    context.user_data['humidity'] = HUMIDITY_MAP[h]
    await update.message.reply_text("Question 5️⃣: How much rain this month?", reply_markup=RAINFALL_KEYBOARD)
    return D_RAIN

async def d_rain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = update.message.text.strip()
    if r not in RAINFALL_MAP:
        await update.message.reply_text("Please select 👇", reply_markup=RAINFALL_KEYBOARD)
        return D_RAIN
    context.user_data['rainfall'] = RAINFALL_MAP[r]
    await update.message.reply_text("Question 6️⃣: How wet are the leaves on your crops?", reply_markup=LEAVES_KEYBOARD)
    return D_LEAVES

async def d_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lv = update.message.text.strip()
    if lv not in LEAVES_MAP:
        await update.message.reply_text("Please select 👇", reply_markup=LEAVES_KEYBOARD)
        return D_LEAVES

    await update.message.reply_text("🔬 Analysing your farm data. Please wait...")

    crop = context.user_data['crop']
    try:
        res = requests.post(f"{AI_API}/predict_disease", json={
            "temp": context.user_data['temp'], "humidity": context.user_data['humidity'],
            "rainfall": context.user_data['rainfall'], "leaf_wetness": LEAVES_MAP[lv],
            "soil_ph": 6.5, "wind_speed": 10
        }, timeout=30)
        data = res.json()

        disease    = data['disease']
        confidence = round(data['confidence'] * 100)
        urgency    = data['urgency']

        if disease == "Healthy":
            emoji, status = "✅", "No disease detected"
            action = f"Your *{crop}* looks healthy! Keep monitoring regularly."
        elif urgency == "Critical":
            emoji, status = "🚨", "CRITICAL — Act Immediately"
            action = f"Your *{crop}* needs urgent attention. Visit your agro-dealer today and ask for treatment for *{disease}*."
        elif urgency == "High":
            emoji, status = "⚠️", "High Risk — Act Within 48 Hours"
            action = f"Spray fungicide on your *{crop}* within 48 hours. Ask your agro-dealer for the right product."
        else:
            emoji, status = "⚡", "Low Risk — Monitor Closely"
            action = f"Your *{crop}* shows early signs. Monitor closely and improve drainage if possible."

        await update.message.reply_text(
            f"{emoji} *AgriGuard Disease Report*\n{'─'*30}\n"
            f"🌱 Crop: *{crop}*\n🦠 Finding: *{disease}*\n"
            f"📊 Certainty: *{confidence}%*\n🚨 Status: *{status}*\n\n"
            f"📋 *What To Do:*\n{action}\n\n"
            f"_Tap below to check something else._",
            parse_mode="Markdown", reply_markup=MAIN_MENU
        )
    except Exception:
        await update.message.reply_text("⚠️ Could not reach AI engine. Try again shortly.", reply_markup=MAIN_MENU)

    return MENU

# ════════════════════════════════════════════════════════════════════════════════
# YIELD FLOW
# ════════════════════════════════════════════════════════════════════════════════

async def y_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat = update.message.text.strip()
    if cat not in CROP_CATEGORIES:
        await update.message.reply_text("Please select a category 👇", reply_markup=CATEGORY_KEYBOARD)
        return Y_CATEGORY
    context.user_data['cat'] = cat
    await update.message.reply_text("Question 2️⃣: Which crop specifically?", reply_markup=crop_keyboard(cat))
    return Y_CROP

async def y_crop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crop = update.message.text.strip()
    if crop not in all_crops():
        await update.message.reply_text("Please select your crop 👇", reply_markup=crop_keyboard(context.user_data.get('cat','')))
        return Y_CROP
    context.user_data['crop'] = crop
    await update.message.reply_text(
        f"Great! You grow *{crop}* 🌱\n\nQuestion 3️⃣: How is the weather this season?",
        parse_mode="Markdown", reply_markup=WEATHER_KEYBOARD)
    return Y_WEATHER

async def y_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    w = update.message.text.strip()
    if w not in WEATHER_MAP:
        await update.message.reply_text("Please select 👇", reply_markup=WEATHER_KEYBOARD)
        return Y_WEATHER
    context.user_data['temp'] = WEATHER_MAP[w]
    await update.message.reply_text("Question 4️⃣: How much rain this month?", reply_markup=RAINFALL_KEYBOARD)
    return Y_RAIN

async def y_rain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = update.message.text.strip()
    if r not in RAINFALL_MAP:
        await update.message.reply_text("Please select 👇", reply_markup=RAINFALL_KEYBOARD)
        return Y_RAIN
    context.user_data['rainfall'] = RAINFALL_MAP[r]
    await update.message.reply_text("Question 5️⃣: How much fertilizer do you use?", reply_markup=FERT_USAGE_KBD)
    return Y_FERT

async def y_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fu = update.message.text.strip()
    if fu not in FERT_USAGE_MAP:
        await update.message.reply_text("Please select 👇", reply_markup=FERT_USAGE_KBD)
        return Y_FERT

    await update.message.reply_text("📊 Calculating your harvest forecast. Please wait...")

    crop = context.user_data['crop']
    try:
        res = requests.post(f"{AI_API}/predict_yield", json={
            "temp": context.user_data['temp'], "humidity": 70, "soil_ph": 6.5,
            "rainfall": context.user_data['rainfall'], "fertilizer_kg": FERT_USAGE_MAP[fu],
            "sunlight_hrs": 8
        }, timeout=30)
        data = res.json()

        yield_kg  = data['yield_kg_per_hectare']
        rating    = data['rating']
        advice    = data['advice']
        tons      = round(yield_kg / 1000, 2)
        bags_50kg = int(yield_kg / 50)

        emoji = {"Excellent": "🌟", "Good": "✅", "Fair": "⚡", "Poor": "⚠️"}.get(rating, "📊")

        await update.message.reply_text(
            f"🌾 *AgriGuard Harvest Forecast*\n{'─'*30}\n"
            f"🌱 Crop: *{crop}*\n"
            f"📦 Expected: *{yield_kg:,.0f} kg per hectare*\n"
            f"🏋️ That is: *{tons} tonnes*\n"
            f"🛄 About: *{bags_50kg} bags of 50kg*\n"
            f"{emoji} Rating: *{rating}*\n\n"
            f"📋 *Advice:*\n{advice}\n\n"
            f"_Tap below to check something else._",
            parse_mode="Markdown", reply_markup=MAIN_MENU
        )
    except Exception:
        await update.message.reply_text("⚠️ Could not reach AI engine. Try again shortly.", reply_markup=MAIN_MENU)

    return MENU

# ════════════════════════════════════════════════════════════════════════════════
# FERTILIZER FLOW
# ════════════════════════════════════════════════════════════════════════════════

async def f_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat = update.message.text.strip()
    if cat not in CROP_CATEGORIES:
        await update.message.reply_text("Please select a category 👇", reply_markup=CATEGORY_KEYBOARD)
        return F_CATEGORY
    context.user_data['cat'] = cat
    await update.message.reply_text("Question 2️⃣: Which crop specifically?", reply_markup=crop_keyboard(cat))
    return F_CROP

async def f_crop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crop = update.message.text.strip()
    if crop not in all_crops():
        await update.message.reply_text("Please select your crop 👇", reply_markup=crop_keyboard(context.user_data.get('cat','')))
        return F_CROP
    context.user_data['crop'] = crop
    await update.message.reply_text(
        f"Great! You grow *{crop}* 🌱\n\nQuestion 3️⃣: What does your soil look like?",
        parse_mode="Markdown", reply_markup=SOIL_KEYBOARD)
    return F_SOIL

async def f_soil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = update.message.text.strip()
    if s not in SOIL_MAP:
        await update.message.reply_text("Please select 👇", reply_markup=SOIL_KEYBOARD)
        return F_SOIL
    context.user_data['soil_ph'] = SOIL_MAP[s]
    await update.message.reply_text("Question 4️⃣: When did you last add fertilizer?", reply_markup=FERT_KEYBOARD)
    return F_LAST_FERT

async def f_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lf = update.message.text.strip()
    if lf not in LAST_FERT_MAP:
        await update.message.reply_text("Please select 👇", reply_markup=FERT_KEYBOARD)
        return F_LAST_FERT

    await update.message.reply_text("🔬 Analysing your soil profile. Please wait...")

    crop       = context.user_data['crop']
    model_crop = CROP_TO_MODEL.get(crop, "Maize")
    try:
        res = requests.post(f"{AI_API}/recommend_fertilizer", json={
            "crop_type": model_crop, "soil_ph": context.user_data['soil_ph'],
            "nitrogen": LAST_FERT_MAP[lf], "phosphorus": 30,
            "potassium": 50, "moisture": 40
        }, timeout=30)
        data = res.json()

        fert       = data['recommended_fertilizer']
        confidence = round(data['confidence'] * 100)
        dosage     = data['dosage_guide']

        await update.message.reply_text(
            f"💊 *AgriGuard Fertilizer Report*\n{'─'*30}\n"
            f"🌱 Crop: *{crop}*\n"
            f"🧪 Recommended: *{fert}*\n"
            f"📊 Certainty: *{confidence}%*\n\n"
            f"📋 *How To Apply:*\n{dosage}\n\n"
            f"💡 Ask for *{fert}* at your nearest agro-dealer.\n\n"
            f"_Tap below to check something else._",
            parse_mode="Markdown", reply_markup=MAIN_MENU
        )
    except Exception:
        await update.message.reply_text("⚠️ Could not reach AI engine. Try again shortly.", reply_markup=MAIN_MENU)

    return MENU

# ── Cancel ────────────────────────────────────────────────────────────────────

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled. Returning to menu 👇", reply_markup=MAIN_MENU)
    return MENU

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU:       [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            D_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, d_category)],
            D_CROP:     [MessageHandler(filters.TEXT & ~filters.COMMAND, d_crop)],
            D_WEATHER:  [MessageHandler(filters.TEXT & ~filters.COMMAND, d_weather)],
            D_HUMIDITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, d_humidity)],
            D_RAIN:     [MessageHandler(filters.TEXT & ~filters.COMMAND, d_rain)],
            D_LEAVES:   [MessageHandler(filters.TEXT & ~filters.COMMAND, d_result)],
            Y_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, y_category)],
            Y_CROP:     [MessageHandler(filters.TEXT & ~filters.COMMAND, y_crop)],
            Y_WEATHER:  [MessageHandler(filters.TEXT & ~filters.COMMAND, y_weather)],
            Y_RAIN:     [MessageHandler(filters.TEXT & ~filters.COMMAND, y_rain)],
            Y_FERT:     [MessageHandler(filters.TEXT & ~filters.COMMAND, y_result)],
            F_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, f_category)],
            F_CROP:     [MessageHandler(filters.TEXT & ~filters.COMMAND, f_crop)],
            F_SOIL:     [MessageHandler(filters.TEXT & ~filters.COMMAND, f_soil)],
            F_LAST_FERT:[MessageHandler(filters.TEXT & ~filters.COMMAND, f_result)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)

    # Start keep-alive ping loop
    loop = asyncio.get_event_loop()
    loop.create_task(keep_alive())

    print("🌿 AgriGuard AI Bot v2 is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
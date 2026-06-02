from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def get_language_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🇱🇰 සිංහල", callback_data="lang_si"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu(lang):
    if lang == "si":
        keyboard = [
            ["🧮 කැල්කියුලේටර්", "📜 පඩිපාලක සභා තීරණ"],
            ["📘 කම්කරු නීති සහ FAQ", "📞 කම්කරු කාර්යාල ලිපින"],
            ["📝 පෝරම සහ අයදුම්පත්", "⏳ මගේ ගණනය කිරීම්"],
            ["💬 AI කම්කරු සහකරු", "🌐 Change Language"]
        ]
    else:
        keyboard = [
            ["🧮 Calculators", "📜 Wages Boards"],
            ["📘 Labor Laws & FAQ", "📞 Labor Offices"],
            ["📝 Official Forms", "⏳ Calculation History"],
            ["💬 AI Assistant", "🌐 භාෂාව වෙනස් කරන්න"]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_calculator_menu(lang):
    if lang == "si":
        keyboard = [
            ["💰 EPF & ETF", "🎁 පාරිතෝෂිකය (Gratuity)"],
            ["⏱️ අතිකාල (Overtime)", "🔙 ප්‍රධාන මෙනුවට"]
        ]
    else:
        keyboard = [
            ["💰 EPF & ETF", "🎁 Gratuity"],
            ["⏱️ Overtime", "🔙 Main Menu"]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_cancel_keyboard(lang):
    if lang == "si":
        keyboard = [["❌ අවලංගු කරන්න"]]
    else:
        keyboard = [["❌ Cancel"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_wages_board_inline_keyboard(wages_boards, lang):
    keyboard = []
    for wb in wages_boards:
        name = wb["trade_name_si"] if lang == "si" else wb["trade_name_en"]
        keyboard.append([InlineKeyboardButton(name, callback_data=f"wb_{wb['id']}")])
    return InlineKeyboardMarkup(keyboard)

def get_faq_categories_keyboard(categories, lang):
    keyboard = []
    # Display categories as buttons
    # 2 categories per row
    row = []
    for cat in categories:
        row.append(InlineKeyboardButton(cat, callback_data=f"faqcat_{cat}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

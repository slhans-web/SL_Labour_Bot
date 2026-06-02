import logging
import json
from telegram import Update, ReplyKeyboardRemove
from telegram.error import BadRequest
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)

import config
import database
import calculators
import keyboards
import ai_assistant


# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
(
    # EPF/ETF
    STATE_EPF_BASIC,
    STATE_EPF_ALLOWANCE,
    
    # Gratuity
    STATE_GRATUITY_BASIC,
    STATE_GRATUITY_YEARS,
    
    # Overtime
    STATE_OT_BASIC,
    STATE_OT_HOURS,
    STATE_OT_DIVISOR
) = range(7)

# Helper: Get user language or default to Sinhala
def get_user_lang(user_data):
    return user_data.get("lang", "si")

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f"User {user.username or user.id} started the bot.")
    
    # Check if database is initialized, do it dynamically
    database.init_db()
    
    # Welcome messages
    welcome_si = (
        f"ආයුබෝවන් {user.first_name}! 👋\n\n"
        "කම්කරු නිලධාරී සහායක Telegram Bot වෙත සාදරයෙන් පිළිගනිමු.\n"
        "ශ්‍රී ලංකාවේ කම්කරු නීති, පඩිපාලක සභා තීරණ, කාර්යාල විස්තර සහ විවිධ ගණනය කිරීම් (EPF, ETF, Gratuity, Overtime) සඳහා ඔබට මෙතැනින් සහාය ලබාගත හැක.\n\n"
        "කරුණාකර පහතින් ඔබේ භාෂාව තෝරන්න:"
    )
    welcome_en = (
        f"Hello {user.first_name}! 👋\n\n"
        "Welcome to the Labor Officer Assistant Telegram Bot.\n"
        "This bot helps you quickly access Sri Lankan labor laws, Wages Board determinations, office contact details, and perform calculators (EPF, ETF, Gratuity, Overtime).\n\n"
        "Please choose your language below:"
    )
    
    # Send welcoming message with inline keyboard for language
    await update.message.reply_text(
        f"{welcome_si}\n\n{"═"*30}\n\n{welcome_en}",
        reply_markup=keyboards.get_language_keyboard()
    )

# Callback: Language Selection
async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    lang = "si" if query.data == "lang_si" else "en"
    context.user_data["lang"] = lang
    
    if lang == "si":
        msg = "ඔබ සිංහල භාෂාව තෝරාගන්නා ලදී. පහත මෙනුවෙන් ඔබට අවශ්‍ය සේවාව තෝරන්න:"
    else:
        msg = "You have selected English. Please select your desired service from the menu below:"
        
    await query.message.reply_text(
        msg,
        reply_markup=keyboards.get_main_menu(lang)
    )

# Command/Button Handler: Language Swap
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "කරුණාකර භාෂාව තෝරන්න / Please choose your language:",
        reply_markup=keyboards.get_language_keyboard()
    )

# Main Menu Navigation Routing
async def handle_menu_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    lang = get_user_lang(context.user_data)
    
    # 1. Calculators Menu
    if text in ["🧮 කැල්කියුලේටර්", "🧮 Calculators"]:
        msg = (
            "ඔබට අවශ්‍ය ගණනය කිරීම තෝරන්න:" if lang == "si"
            else "Select the calculation you want to perform:"
        )
        await update.message.reply_text(msg, reply_markup=keyboards.get_calculator_menu(lang))
        
    # 2. Wages Board Determinations
    elif text in ["📜 පඩිපාලක සභා තීරණ", "📜 Wages Boards"]:
        await show_wages_boards(update, context)
        
    # 3. Labor Laws & FAQ
    elif text in ["📘 කම්කරු නීති සහ FAQ", "📘 Labor Laws & FAQ"]:
        await show_faq_categories(update, context)
        
    # 4. Labor Offices Directory
    elif text in ["📞 කම්කරු කාර්යාල ලිපින", "📞 Labor Offices"]:
        await show_labor_offices(update, context)
        
    # 5. Official Forms
    elif text in ["📝 පෝරම සහ අයදුම්පත්", "📝 Official Forms"]:
        await show_official_forms(update, context)
        
    # 6. Calculation History
    elif text in ["⏳ මගේ ගණනය කිරීම්", "⏳ Calculation History"]:
        await show_calculation_history(update, context)
        
    # 7. AI Assistant Intro
    elif text in ["💬 AI කම්කරු සහකරු", "💬 AI Assistant"]:
        await show_ai_assistant_intro(update, context)
        
    # 8. Back/Main Menu Return
    elif text in ["🔙 ප්‍රධාන මෙනුවට", "🔙 Main Menu", "🔙 Back", "🔙 ආපසු"]:
        msg = "ප්‍රධාන මෙනුව:" if lang == "si" else "Main Menu:"
        await update.message.reply_text(msg, reply_markup=keyboards.get_main_menu(lang))
        
    # 9. Trigger Language selection
    elif text in ["🌐 Change Language", "🌐 භාෂාව වෙනස් කරන්න"]:
        await change_language(update, context)
        
    # 10. Free text query to AI Assistant
    else:
        # Show a typing placeholder so the user knows it's thinking
        await update.message.reply_chat_action("typing")
        
        # Query the AI Assistant
        response = ai_assistant.ask_ai_assistant(text)
        
        # Reply to the user
        try:
            await update.message.reply_text(response, parse_mode="Markdown")
        except BadRequest as e:
            logger.warning(f"Failed to send with Markdown formatting: {e}. Falling back to plain text.")
            await update.message.reply_text(response)

async def show_ai_assistant_intro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_user_lang(context.user_data)
    if lang == "si":
        msg = (
            "💬 *AI කම්කරු නීති සහය (AI Labor Assistant)*\n\n"
            "මම කම්කරු නිලධාරියෙකුගේ කටයුතු සඳහා විශේෂයෙන් පුහුණු කළ කෘතිම බුද්ධි (AI) සහායකයෙක්මි.\n"
            "ඔබට අවශ්‍ය ඕනෑම ප්‍රශ්නයක් කෙලින්ම ලියා එවන්න. මම විනාඩියක් ඇතුළත පිළිතුරු සකස් කර දෙන්නෙමි.\n\n"
            "💡 *උදාහරණ ලෙස ඔබට විමසිය හැකි දේ:*\n"
            "• *ලිපි කෙටුම්පත් කිරීම:* `වැටුප් නොගෙවූ සේවකයෙකුගේ පැමිණිල්ලක් මත සේවා යෝජකයාට ලිවිය යුතු නිල දැනුම්දීමේ ලිපියක් සිංහලෙන් සකස් කරන්න.`\n"
            "• *නීතිමය විමසුම්:* `දින 90ක් සේවය කළ සේවකයෙකුට Shop and Office Employees Act යටතේ ලැබෙන අවම වාර්ෂික නිවාඩු දින ගණන කීයද?`\n"
            "• *බේරුම්කරණ තර්ක:* `රබර් කර්මාන්තශාලාවක කම්කරුවන් 50කගේ අතිකාල වේතන නොගෙවීම සම්බන්ධ බේරුම්කරණයකදී ඉදිරිපත් කළ හැකි තර්ක 5ක් සිංහලෙන් ලියන්න.`\n"
            "• *පරීක්ෂණ චෙක්ලිස්ට්:* `මාසික කර්මාන්තශාලා පරීක්ෂාව සඳහා අවශ්‍ය කරුණු 15ක් ඇතුළත් චෙක්ලිස්ට් එකක් සිංහලෙන් හදන්න.`\n"
            "• *නීති වගන්ති:* `Industrial Disputes Act හි 31B වගන්තියේ අර්ථය සරල සිංහලෙන් විස්තර කරන්න.`\n\n"
            "📥 ඔබට අවශ්‍ය ප්‍රශ්නය දැන්ම ටයිප් කර එවන්න!"
        )
    else:
        msg = (
            "💬 *AI Labor Law Assistant*\n\n"
            "I am an AI assistant trained in Sri Lankan Labor Laws to support Labor Officers.\n"
            "You can type any free-text query, and I will generate a comprehensive response in under a minute.\n\n"
            "💡 *Example Queries:*\n"
            "• *Drafting Letters:* `Draft a warning letter in Sinhala to an employer for not paying EPF on time.`\n"
            "• *Legal Inquiries:* `What is the maternity leave entitlement for a second child under Shop & Office Act?`\n"
            "• *Inspection Checklists:* `Create a checklist of 15 items in Sinhala for a monthly factory inspection.`\n"
            "• *Legal Interpretations:* `Explain Section 31B of Industrial Disputes Act simply.`\n\n"
            "📥 Simply type your question now and send it!"
        )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ----------------- Wages Boards Handling -----------------
async def show_wages_boards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_user_lang(context.user_data)
    wbs = database.get_all_wages_boards()
    
    msg = (
        "පඩිපාලක සභා තීරණ බැලීමට පහතින් අදාළ ක්ෂේත්‍රය තෝරන්න:" if lang == "si"
        else "Select a trade to view its Wages Board determinations:"
    )
    await update.message.reply_text(
        msg,
        reply_markup=keyboards.get_wages_board_inline_keyboard(wbs, lang)
    )

async def handle_wages_board_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context.user_data)
    
    wb_id = int(query.data.split("_")[1])
    wb = database.get_wages_board_by_id(wb_id)
    
    if not wb:
        return
    
    if lang == "si":
        details = (
            f"📜 *{wb['trade_name_si']}*\n"
            f"💰 අවම මූලික වැටුප: රු. {wb['minimum_wage']:,}\n"
            f"⏱️ අතිකාල අනුපාතය: {wb['overtime_rate_multiplier']}x\n"
            f"📅 සාමාන්‍ය වැඩ කරන පැය: දිනකට පැය {wb['normal_working_hours_daily']}\n"
            f"🏖️ සතිපතා නිවාඩු: {wb['weekly_holidays_si']}\n\n"
            f"💡 *විශේෂ සටහන්:*\n{wb['notes_si']}"
        )
    else:
        details = (
            f"📜 *{wb['trade_name_en']}*\n"
            f"💰 Minimum wage/rate: LKR {wb['minimum_wage']:,}\n"
            f"⏱️ Overtime rate: {wb['overtime_rate_multiplier']}x\n"
            f"📅 Normal working hours: {wb['normal_working_hours_daily']} hours/day\n"
            f"🏖️ Weekly holidays: {wb['weekly_holidays_en']}\n\n"
            f"💡 *Special Notes:*\n{wb['notes_en']}"
        )
        
    await query.message.reply_text(details, parse_mode="Markdown")

# ----------------- Labor Offices Handling -----------------
async def show_labor_offices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_user_lang(context.user_data)
    offices = database.get_all_labor_offices()
    
    header = "📞 *කම්කරු දෙපාර්තමේන්තු කාර්යාල ලිපින සහ දුරකථන අංක:*\n\n" if lang == "si" else "📞 *Labor Offices Directory:*\n\n"
    body = ""
    
    for o in offices:
        name = o["name_si"] if lang == "si" else o["name_en"]
        addr = o["address_si"] if lang == "si" else o["address_en"]
        body += f"🏢 *{name}*\n📍 {addr}\n☎️ {o['phone']}\n\n"
        
    await update.message.reply_text(header + body, parse_mode="Markdown")

# ----------------- FAQs & Labor Laws Handling -----------------
async def show_faq_categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_user_lang(context.user_data)
    categories = database.get_faq_categories()
    
    msg = (
        "කම්කරු නීති සහ FAQ කාණ්ඩ පහතින් දැක්වේ. විස්තර බැලීමට අදාළ කාණ්ඩය තෝරන්න:" if lang == "si"
        else "Select a category to view FAQs and Labor Law guides:"
    )
    await update.message.reply_text(
        msg,
        reply_markup=keyboards.get_faq_categories_keyboard(categories, lang)
    )

async def handle_faq_category_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context.user_data)
    
    cat = query.data.split("_")[1]
    faqs = database.get_faqs_by_category(cat)
    
    if not faqs:
        return
    
    response = f"📘 *Category: {cat}*\n\n"
    for faq in faqs:
        q = faq["question_si"] if lang == "si" else faq["question_en"]
        a = faq["answer_si"] if lang == "si" else faq["answer_en"]
        response += f"❓ *{q}*\n💡 {a}\n\n"
        
    await query.message.reply_text(response, parse_mode="Markdown")

# ----------------- Official Forms -----------------
async def show_official_forms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_user_lang(context.user_data)
    
    if lang == "si":
        msg = (
            "📝 *නිල කම්කරු පෝරම සහ අයදුම්පත් බාගත කිරීම්:*\n\n"
            "1. *EPF මුදල් ලබාගැනීමේ පෝරමය (K Form)*\n"
            "👉 [මෙහි ක්ලික් කර බාගන්න](https://www.epf.lk/wp-content/uploads/2021/04/K-Form.pdf)\n\n"
            "2. *ETF මුදල් ලබාගැනීමේ අයදුම්පත්*\n"
            "👉 [ETF වෙබ් අඩවියට පිවිසෙන්න](https://etfb.lk/)\n\n"
            "3. *කම්කරු පැමිණිලි ඉදිරිපත් කිරීමේ ආකෘති පත්‍රය*\n"
            "👉 [කම්කරු දෙපාර්තමේන්තු පැමිණිලි අංශය](http://www.labourdept.gov.lk/)"
        )
    else:
        msg = (
            "📝 *Official Labor Forms & Downloads:*\n\n"
            "1. *EPF Withdrawal Form (K Form)*\n"
            "👉 [Click here to download PDF](https://www.epf.lk/wp-content/uploads/2021/04/K-Form.pdf)\n\n"
            "2. *ETF Claim Forms*\n"
            "👉 [Visit ETF Website](https://etfb.lk/)\n\n"
            "3. *Submit Labor Dispute/Complaint Form*\n"
            "👉 [Visit Labor Department Complaints portal](http://www.labourdept.gov.lk/)"
        )
    await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)

# ----------------- Calculation History -----------------
async def show_calculation_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    lang = get_user_lang(context.user_data)
    history = database.get_user_history(user.id, limit=5)
    
    if not history:
        msg = (
            "⚠️ ඔබ තවමත් කිසිදු ගණනය කිරීමක් සිදු කර නැත." if lang == "si"
            else "⚠️ You have not performed any calculations yet."
        )
        await update.message.reply_text(msg)
        return
        
    header = "⏳ *ඔබේ අවසන් ගණනය කිරීම් 5 (Last 5 Calculations):*\n\n" if lang == "si" else "⏳ *Your Last 5 Calculations:*\n\n"
    body = ""
    
    for item in history:
        calc_type = item["calc_type"]
        inputs = item["inputs"]
        results = item["results"]
        date = item["calculated_at"]
        
        body += f"🗓️ *{date} - {calc_type}*\n"
        
        if calc_type == "EPF/ETF":
            body += (
                f"   • Basic/Allowances: LKR {inputs['basic']:,} / {inputs['allowances']:,}\n"
                f"   • Employee EPF (8%): LKR {results['epf_employee']:,}\n"
                f"   • Employer EPF (12%): LKR {results['epf_employer']:,}\n"
                f"   • Employer ETF (3%): LKR {results['etf_employer']:,}\n"
            )
        elif calc_type == "Gratuity":
            body += (
                f"   • Last Basic: LKR {inputs['basic']:,} | Service: {inputs['years']} Years\n"
                f"   • Amount: LKR {results['gratuity_amount']:,}\n"
            )
        elif calc_type == "Overtime":
            body += (
                f"   • Basic: LKR {inputs['basic']:,} | OT Hours: {inputs['hours']}\n"
                f"   • OT Pay: LKR {results['ot_pay']:,} (Rate: LKR {results['ot_hourly_rate']}/hr)\n"
            )
        body += "\n"
        
    await update.message.reply_text(header + body, parse_mode="Markdown")

# ----------------- Conversational Calculators -----------------

# 1. EPF/ETF Conversational Flow
async def calc_epf_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_user_lang(context.user_data)
    msg = (
        "💰 *EPF & ETF ගණනය කිරීම:*\n\nකරුණාකර සේවකයාගේ *මූලික වැටුප (Basic Salary)* රුපියල් වලින් ඇතුළත් කරන්න:" if lang == "si"
        else "💰 *EPF & ETF Calculator:*\n\nPlease enter the employee's *Basic Salary* in LKR:"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=keyboards.get_cancel_keyboard(lang))
    return STATE_EPF_BASIC

async def calc_epf_basic_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    lang = get_user_lang(context.user_data)
    
    if text in ["❌ අවලංගු කරන්න", "❌ Cancel"]:
        await update.message.reply_text("ගණනය කිරීම අවලංගු කරන ලදී.", reply_markup=keyboards.get_calculator_menu(lang))
        return ConversationHandler.END
        
    try:
        basic = float(text)
        if basic <= 0:
            raise ValueError
        context.user_data["temp_basic"] = basic
    except ValueError:
        msg = "අවලංගු අගයක්. කරුණාකර නිවැරදි මූලික වැටුප ඇතුළත් කරන්න:" if lang == "si" else "Invalid salary. Please enter a valid number:"
        await update.message.reply_text(msg)
        return STATE_EPF_BASIC
        
    msg = (
        "කරුණාකර සේවා නියුක්තිය සඳහා හිමිවන වෙනත් *ස්ථාවර දීමනා (Fixed Allowances)* ඇතුළත් කරන්න:\n(දීමනා නොමැති නම් 0 ඇතුළත් කරන්න)" if lang == "si"
        else "Please enter any other *Fixed Allowances*:\n(Enter 0 if there are no allowances)"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")
    return STATE_EPF_ALLOWANCE

async def calc_epf_allowance_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    lang = get_user_lang(context.user_data)
    
    if text in ["❌ අවලංගු කරන්න", "❌ Cancel"]:
        await update.message.reply_text("ගණනය කිරීම අවලංගු කරන ලදී.", reply_markup=keyboards.get_calculator_menu(lang))
        return ConversationHandler.END
        
    try:
        allowances = float(text)
        if allowances < 0:
            raise ValueError
    except ValueError:
        msg = "අවලංගු අගයක්. කරුණාකර නිවැරදි දීමනා අගය ඇතුළත් කරන්න (හෝ 0):" if lang == "si" else "Invalid allowance. Please enter a valid number (or 0):"
        await update.message.reply_text(msg)
        return STATE_EPF_ALLOWANCE
        
    basic = context.user_data.pop("temp_basic")
    res = calculators.calculate_epf_etf(basic, allowances)
    
    # Save to history DB
    user = update.effective_user
    database.save_calculation(
        user_id=user.id,
        username=user.username or str(user.id),
        calc_type="EPF/ETF",
        inputs_dict={"basic": basic, "allowances": allowances},
        results_dict=res
    )
    
    if lang == "si":
        result_msg = (
            "📊 *EPF & ETF ගණනය කිරීම් වාර්තාව:*\n\n"
            f"💵 මූලික වැටුප: රු. {basic:,.2f}\n"
            f"➕ දීමනා: රු. {allowances:,.2f}\n"
            f"📈 දායකත්ව ලැබෙන මුළු වැටුප: *රු. {res['total_earnings']:,.2f}*\n\n"
            f"👤 සේවකයාගේ EPF දායකත්වය (8%): *රු. {res['epf_employee']:,.2f}*\n"
            f"🏢 සේවායෝජක EPF දායකත්වය (12%): රු. {res['epf_employer']:,.2f}\n"
            f"🏦 මුළු EPF එකතුව (20%): රු. {res['epf_total']:,.2f}\n"
            f"🛡️ සේවායෝජක ETF දායකත්වය (3%): *රු. {res['etf_employer']:,.2f}*\n\n"
            f"💵 EPF අඩු කිරීමෙන් පසු ශේෂය (Net Salary Base): *රු. {res['net_salary_base']:,.2f}*\n\n"
            "ℹ️ *සටහන:* සේවායෝජකයා 12% EPF සහ 3% ETF සම්පූර්ණයෙන්ම තමාගේ වියදමෙන් ගෙවිය යුතු අතර සේවකයාගේ වැටුපෙන් කපා ගත හැක්කේ 8% පමණි."
        )
    else:
        result_msg = (
            "📊 *EPF & ETF Calculation Report:*\n\n"
            f"💵 Basic Salary: LKR {basic:,.2f}\n"
            f"➕ Allowances: LKR {allowances:,.2f}\n"
            f"📈 Total Earnings for EPF/ETF: *LKR {res['total_earnings']:,.2f}*\n\n"
            f"👤 Employee EPF Contribution (8%): *LKR {res['epf_employee']:,.2f}*\n"
            f"🏢 Employer EPF Contribution (12%): LKR {res['epf_employer']:,.2f}\n"
            f"🏦 Total EPF to Central Bank (20%): LKR {res['epf_total']:,.2f}\n"
            f"🛡️ Employer ETF Contribution (3%): *LKR {res['etf_employer']:,.2f}*\n\n"
            f"💵 Net Salary Base (After 8% deduction): *LKR {res['net_salary_base']:,.2f}*\n\n"
            "ℹ️ *Note:* The employer must bear the 12% EPF and 3% ETF entirely, and only 8% can be deducted from the employee's earnings."
        )
        
    await update.message.reply_text(result_msg, parse_mode="Markdown", reply_markup=keyboards.get_calculator_menu(lang))
    return ConversationHandler.END


# 2. Gratuity Conversational Flow
async def calc_gratuity_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_user_lang(context.user_data)
    msg = (
        "🎁 *පාරිතෝෂික (Gratuity) ගණනය කිරීම:*\n\nකරුණාකර සේවකයාගේ *අවසන් වරට ලබාගත් මූලික වැටුප* රුපියල් වලින් ඇතුළත් කරන්න:" if lang == "si"
        else "🎁 *Gratuity Calculator:*\n\nPlease enter the employee's *Last Drawn Basic Salary* in LKR:"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=keyboards.get_cancel_keyboard(lang))
    return STATE_GRATUITY_BASIC

async def calc_gratuity_basic_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    lang = get_user_lang(context.user_data)
    
    if text in ["❌ අවලංගු කරන්න", "❌ Cancel"]:
        await update.message.reply_text("ගණනය කිරීම අවලංගු කරන ලදී.", reply_markup=keyboards.get_calculator_menu(lang))
        return ConversationHandler.END
        
    try:
        basic = float(text)
        if basic <= 0:
            raise ValueError
        context.user_data["temp_basic"] = basic
    except ValueError:
        msg = "අවලංගු අගයක්. කරුණාකර නිවැරදි මූලික වැටුප ඇතුළත් කරන්න:" if lang == "si" else "Invalid salary. Please enter a valid number:"
        await update.message.reply_text(msg)
        return STATE_GRATUITY_BASIC
        
    msg = (
        "කරුණාකර සේවකයාගේ *අඛණ්ඩ සේවා කාලය (සම්පූර්ණ කරන ලද වසර ගණන)* ඇතුළත් කරන්න:" if lang == "si"
        else "Please enter the employee's *Continuous Service (Completed Years)*:"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")
    return STATE_GRATUITY_YEARS

async def calc_gratuity_years_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    lang = get_user_lang(context.user_data)
    
    if text in ["❌ අවලංගු කරන්න", "❌ Cancel"]:
        await update.message.reply_text("ගණනය කිරීම අවලංගු කරන ලදී.", reply_markup=keyboards.get_calculator_menu(lang))
        return ConversationHandler.END
        
    try:
        years = int(text)
        if years < 0:
            raise ValueError
    except ValueError:
        msg = "අවලංගු අගයක්. කරුණාකර සම්පූර්ණ කරන ලද වසර ගණන නිවැරදිව ඇතුළත් කරන්න:" if lang == "si" else "Invalid service years. Please enter a valid integer:"
        await update.message.reply_text(msg)
        return STATE_GRATUITY_YEARS
        
    basic = context.user_data.pop("temp_basic")
    res = calculators.calculate_gratuity(basic, years)
    
    # Save to history DB
    user = update.effective_user
    database.save_calculation(
        user_id=user.id,
        username=user.username or str(user.id),
        calc_type="Gratuity",
        inputs_dict={"basic": basic, "years": years},
        results_dict={"gratuity_amount": res["gratuity_amount"], "eligible": res["eligible"]}
    )
    
    if lang == "si":
        elig_status = "✅ " + res["message_si"] if res["eligible"] else "❌ " + res["message_si"]
        result_msg = (
            "📊 *පාරිතෝෂික ගණනය කිරීමේ වාර්තාව (Gratuity Report):*\n\n"
            f"💵 අවසන් මූලික වැටුප: රු. {basic:,.2f}\n"
            f"📅 සේවා කාලය: වසර {years}\n"
            f"สถานะ සුදුසුකම: *{elig_status}*\n\n"
            f"🎁 හිමිවන පාරිතෝෂික මුදල: *රු. {res['gratuity_amount']:,.2f}*\n\n"
            "ℹ️ *සටහන:* පාරිතෝෂික ගෙවීම් පනත අනුව පාරිතෝෂිකය හිමිවීමට සේවකයා වසර 5ක් සේවය කර තිබීම සහ ආයතනය තුළ පෙර මාස 12 තුළ සේවකයින් 15ක් හෝ ඊට වැඩි ගණනක් සේවය කර තිබීම අනිවාර්ය වේ."
        )
    else:
        elig_status = "✅ " + res["message_en"] if res["eligible"] else "❌ " + res["message_en"]
        result_msg = (
            "📊 *Gratuity Calculation Report:*\n\n"
            f"💵 Last Drawn Basic: LKR {basic:,.2f}\n"
            f"📅 Service Period: {years} Years\n"
            f"Eligibility Status: *{elig_status}*\n\n"
            f"🎁 Gratuity Amount Due: *LKR {res['gratuity_amount']:,.2f}*\n\n"
            "ℹ️ *Note:* Under Gratuity Act, the benefit is statutory for employees with >= 5 years of service in workplaces employing 15 or more workers at any time in the past year."
        )
        
    await update.message.reply_text(result_msg, parse_mode="Markdown", reply_markup=keyboards.get_calculator_menu(lang))
    return ConversationHandler.END


# 3. Overtime Conversational Flow
async def calc_ot_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_user_lang(context.user_data)
    msg = (
        "⏱️ *අතිකාල (Overtime) ගණනය කිරීම:*\n\nකරුණාකර සේවකයාගේ *මූලික වැටුප (Basic Salary)* රුපියල් වලින් ඇතුළත් කරන්න:" if lang == "si"
        else "⏱️ *Overtime Calculator:*\n\nPlease enter the employee's *Basic Salary* in LKR:"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=keyboards.get_cancel_keyboard(lang))
    return STATE_OT_BASIC

async def calc_ot_basic_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    lang = get_user_lang(context.user_data)
    
    if text in ["❌ අවලංගු කරන්න", "❌ Cancel"]:
        await update.message.reply_text("ගණනය කිරීම අවලංගු කරන ලදී.", reply_markup=keyboards.get_calculator_menu(lang))
        return ConversationHandler.END
        
    try:
        basic = float(text)
        if basic <= 0:
            raise ValueError
        context.user_data["temp_basic"] = basic
    except ValueError:
        msg = "අවලංගු අගයක්. කරුණාකර නිවැරදි මූලික වැටුප ඇතුළත් කරන්න:" if lang == "si" else "Invalid salary. Please enter a valid number:"
        await update.message.reply_text(msg)
        return STATE_OT_BASIC
        
    msg = (
        "කරුණාකර සිදුකළ *අතිකාල පැය ගණන (OT Hours)* ඇතුළත් කරන්න:" if lang == "si"
        else "Please enter the number of *Overtime Hours* worked:"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")
    return STATE_OT_HOURS

async def calc_ot_hours_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    lang = get_user_lang(context.user_data)
    
    if text in ["❌ අවලංගු කරන්න", "❌ Cancel"]:
        await update.message.reply_text("ගණනය කිරීම අවලංගු කරන ලදී.", reply_markup=keyboards.get_calculator_menu(lang))
        return ConversationHandler.END
        
    try:
        hours = float(text)
        if hours < 0:
            raise ValueError
        context.user_data["temp_hours"] = hours
    except ValueError:
        msg = "අවලංගු අගයක්. කරුණාකර අතිකාල පැය ගණන නිවැරදිව ඇතුළත් කරන්න:" if lang == "si" else "Invalid hours. Please enter a valid number:"
        await update.message.reply_text(msg)
        return STATE_OT_HOURS
        
    msg = (
        "කරුණාකර සාමාන්‍ය මාසික වැඩ කරන පැය ප්‍රමාණය (Divisor) තෝරන්න/ඇතුළත් කරන්න:\n"
        "(කඩසාප්පු සහ කාර්යාල සේවකයින් සඳහා සම්මත බෙදුම්කරු *240* වේ. වෙනත් අගයක් නම් එම අගය ලියා එවන්න)" if lang == "si"
        else "Please enter the monthly working hours divisor (standard for Shop & Office employees is *240*. If different, type the custom divisor):"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")
    return STATE_OT_DIVISOR

async def calc_ot_divisor_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    lang = get_user_lang(context.user_data)
    
    if text in ["❌ අවලංගු කරන්න", "❌ Cancel"]:
        await update.message.reply_text("ගණනය කිරීම අවලංගු කරන ලදී.", reply_markup=keyboards.get_calculator_menu(lang))
        return ConversationHandler.END
        
    try:
        divisor = float(text)
        if divisor <= 0:
            raise ValueError
    except ValueError:
        msg = "අවලංගු අගයක්. කරුණාකර නිවැරදි බෙදුම්කරුවක් ඇතුළත් කරන්න (උදා: 240):" if lang == "si" else "Invalid divisor. Please enter a valid number (e.g. 240):"
        await update.message.reply_text(msg)
        return STATE_OT_DIVISOR
        
    basic = context.user_data.pop("temp_basic")
    hours = context.user_data.pop("temp_hours")
    
    res = calculators.calculate_overtime(basic, hours, divisor)
    
    # Save to history DB
    user = update.effective_user
    database.save_calculation(
        user_id=user.id,
        username=user.username or str(user.id),
        calc_type="Overtime",
        inputs_dict={"basic": basic, "hours": hours, "divisor": divisor},
        results_dict=res
    )
    
    if lang == "si":
        result_msg = (
            "📊 *අතිකාල ගණනය කිරීම් වාර්තාව (OT Report):*\n\n"
            f"💵 මූලික වැටුප: රු. {basic:,.2f}\n"
            f"⏱️ අතිකාල පැය ගණන: {hours} hrs\n"
            f"🔢 මාසික බෙදුම්කරු: {divisor} hours\n\n"
            f"💸 සාමාන්‍ය පැයක වේතනය: රු. {res['hourly_rate']:,.2f}/hr\n"
            f"⚡ OT පැයක වේතනය (1.5x): රු. {res['ot_hourly_rate']:,.2f}/hr\n\n"
            f"💰 *මුළු අතිකාල ගෙවීම: රු. {res['ot_pay']:,.2f}*\n"
            f"💵 මුළු එකතුව (වැටුප + OT): *රු. {res['total_pay']:,.2f}*\n\n"
            "ℹ️ *සටහන:* සාමාන්‍යයෙන් කඩසාප්පු සහ කාර්යාල සේවක පනත යටතේ සේවය කරන්නෙකුගේ දෛනික OT වේලාව පැයක වේතනය මෙන් 1.5 ගුණයක් වේ."
        )
    else:
        result_msg = (
            "📊 *Overtime Calculation Report:*\n\n"
            f"💵 Basic Salary: LKR {basic:,.2f}\n"
            f"⏱️ OT Hours Worked: {hours} hrs\n"
            f"🔢 Monthly Hours Divisor: {divisor} hours\n\n"
            f"💸 Ordinary Hourly Rate: LKR {res['hourly_rate']:,.2f}/hr\n"
            f"⚡ OT Hourly Rate (1.5x): LKR {res['ot_hourly_rate']:,.2f}/hr\n\n"
            f"💰 *Total OT Payment: LKR {res['ot_pay']:,.2f}*\n"
            f"💵 Total (Salary + OT): *LKR {res['total_pay']:,.2f}*\n\n"
            "ℹ️ *Note:* Shop & Office Act mandates standard overtime rate of 1.5x of the normal hourly wage (Basic Salary / 240)."
        )
        
    await update.message.reply_text(result_msg, parse_mode="Markdown", reply_markup=keyboards.get_calculator_menu(lang))
    return ConversationHandler.END


# Cancel Handler for Conversations
async def cancel_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_user_lang(context.user_data)
    msg = "ගණනය කිරීම අවලංගු කරන ලදී." if lang == "si" else "Calculation cancelled."
    await update.message.reply_text(msg, reply_markup=keyboards.get_calculator_menu(lang))
    return ConversationHandler.END


# Main Loop runner
def main():
    token = config.TELEGRAM_BOT_TOKEN
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("[ERROR] Please configure your TELEGRAM_BOT_TOKEN in the .env file.")
        return
        
    # Setup database
    database.init_db()
    
    app = ApplicationBuilder().token(token).build()
    
    # Language Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("language", change_language))
    app.add_handler(CallbackQueryHandler(handle_language_selection, pattern="^lang_"))
    
    # Wages Board & FAQ inline click handlers
    app.add_handler(CallbackQueryHandler(handle_wages_board_click, pattern="^wb_"))
    app.add_handler(CallbackQueryHandler(handle_faq_category_click, pattern="^faqcat_"))
    
    # 1. EPF/ETF Conversation Handler
    epf_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(💰 EPF & ETF)$"), calc_epf_start),
            MessageHandler(filters.Regex("^(💰 EPF & ETF)$"), calc_epf_start)
        ],
        states={
            STATE_EPF_BASIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_epf_basic_received)],
            STATE_EPF_ALLOWANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_epf_allowance_received)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_conv),
            MessageHandler(filters.Regex("^(❌ Cancel|❌ අවලංගු කරන්න)$"), cancel_conv)
        ]
    )
    app.add_handler(epf_conv)
    
    # 2. Gratuity Conversation Handler
    gratuity_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(🎁 Gratuity|🎁 පාරිතෝෂිකය \\(Gratuity\\))$"), calc_gratuity_start)
        ],
        states={
            STATE_GRATUITY_BASIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_gratuity_basic_received)],
            STATE_GRATUITY_YEARS: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_gratuity_years_received)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_conv),
            MessageHandler(filters.Regex("^(❌ Cancel|❌ අවලංගු කරන්න)$"), cancel_conv)
        ]
    )
    app.add_handler(gratuity_conv)
    
    # 3. Overtime Conversation Handler
    ot_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(⏱️ Overtime|⏱️ අතිකාල \\(Overtime\\))$"), calc_ot_start)
        ],
        states={
            STATE_OT_BASIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_ot_basic_received)],
            STATE_OT_HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_ot_hours_received)],
            STATE_OT_DIVISOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_ot_divisor_received)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_conv),
            MessageHandler(filters.Regex("^(❌ Cancel|❌ අවලංගු කරන්න)$"), cancel_conv)
        ]
    )
    app.add_handler(ot_conv)
    
    # General Menu and Button Handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_navigation))
    
    print("Bot is starting polling. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()

import sqlite3
import json
from datetime import datetime
from config import DB_FILE

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Create Wages Boards table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wages_boards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trade_name_en TEXT UNIQUE,
        trade_name_si TEXT UNIQUE,
        minimum_wage REAL,
        overtime_rate_multiplier REAL DEFAULT 1.5,
        normal_working_hours_daily REAL DEFAULT 8.0,
        weekly_holidays_en TEXT,
        weekly_holidays_si TEXT,
        notes_en TEXT,
        notes_si TEXT
    )
    """)
    
    # 2. Create Calculation History table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calculation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        calc_type TEXT,
        inputs TEXT,
        results TEXT,
        calculated_at TEXT
    )
    """)
    
    # 3. Create Labor Offices table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS labor_offices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_en TEXT UNIQUE,
        name_si TEXT UNIQUE,
        address_en TEXT,
        address_si TEXT,
        phone TEXT
    )
    """)
    
    # 4. Create FAQ table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faq (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_en TEXT,
        question_si TEXT,
        answer_en TEXT,
        answer_si TEXT,
        category TEXT
    )
    """)
    
    conn.commit()
    seed_data(conn)
    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    
    # Seed Wages Boards if empty
    cursor.execute("SELECT COUNT(*) FROM wages_boards")
    if cursor.fetchone()[0] == 0:
        wages_boards_data = [
            (
                "Security Services Trade",
                "ආරක්ෂක සේවා කර්මාන්තය",
                35000.0,
                1.5,
                8.0,
                "Sunday (1.5x OT if worked)",
                "ඉරිදා (වැඩ කළහොත් 1.5x අතිකාල)",
                "Minimum monthly wage is around LKR 35,000 for standard security guards. Shift hours normally 8, but 12-hour shifts include 4 hours OT.",
                "සම්මත ආරක්ෂක නිලධාරියෙකු සඳහා අවම මාසික වැටුප රු. 35,000ක් පමණ වේ. සාමාන්‍ය වැඩ මුරය පැය 8කි. පැය 12 වැඩ මුර සඳහා පැය 4ක අතිකාල හිමිවේ."
            ),
            (
                "Tea Growing and Manufacturing Trade",
                "තේ වගාව සහ නිෂ්පාදන කර්මාන්තය",
                1700.0, # Daily wage rate (LKR 1000/1700 recent standards)
                1.5,
                8.0,
                "Sunday",
                "ඉරිදා",
                "Daily wage system. Currently, LKR 1,700 per day (including allowances). Overtime paid at 1.5 times the hourly rate for work beyond 8 hours.",
                "දෛනික වැටුප් ක්‍රමය. දැනට දිනකට රු. 1,700 (දීමනා ඇතුළුව). පැය 8 ඉක්මවා වැඩ කරන කාලය සඳහා පැය එකකට සාමාන්‍ය වේතනය මෙන් 1.5 ගුණයක් අතිකාල ගෙවිය යුතුය."
            ),
            (
                "Engineering Trade",
                "ඉංජිනේරු කර්මාන්තය",
                42000.0,
                1.5,
                8.0,
                "Sunday",
                "ඉරිදා",
                "Covers mechanics, welders, lathe operators, electricians, etc. Divided into unskilled, semi-skilled, and skilled. Minimum monthly wage for skilled is higher.",
                "මිකැනික්, වෑල්ඩින්, ලේත් ක්‍රියාකරුවන්, විදුලි කාර්මිකයන් ආදී සේවකයින් අයත් වේ. නුපුහුණු, අර්ධ පුහුණු සහ පුහුණු ලෙස වර්ග කර ඇත. පුහුණු සේවකයෙකුගේ අවම වැටුප වැඩිය."
            ),
            (
                "Motor Transport Trade",
                "මෝටර් රථ ප්‍රවාහන කර්මාන්තය",
                38000.0,
                1.5,
                8.0,
                "Weekly holiday varies (1 day off per 6 days worked)",
                "සතිපතා නිවාඩු දිනය වෙනස් වේ (වැඩ කරන දින 6කට දින 1ක නිවාඩුවක්)",
                "Covers drivers, conductors, cleaners, and mechanics. Minimum wage is based on the class of vehicle driven.",
                "රියදුරන්, කොන්දොස්තරවරුන්, ක්ලීනර්වරුන් සහ කාර්මිකයන් අයත් වේ. අවම වැටුප ධාවනය කරන වාහන පන්තිය අනුව තීරණය වේ."
            ),
            (
                "Shop and Office Employees Sector",
                "කඩසාප්පු සහ කාර්යාල සේවක අංශය",
                25000.0,
                1.5,
                8.0,
                "1.5 days per week (normally Saturday afternoon and Sunday)",
                "සතියකට දින 1.5ක් (සාමාන්‍යයෙන් සෙනසුරාදා සවස සහ ඉරිදා)",
                "Governed by Shop and Office Employees Act. Standard OT divisor is 240. Weekly hours limit is 45. OT limit is 12 hours per week.",
                "කඩසාප්පු සහ කාර්යාල සේවක පනත මගින් පාලනය වේ. අතිකාල සඳහා බෙදුම්කරු 240 වේ. සතියක උපරිම වැඩ කරන පැය ගණන 45කි. උපරිම අතිකාල පැය ගණන සතියකට 12කි."
            )
        ]
        cursor.executemany("""
        INSERT INTO wages_boards (trade_name_en, trade_name_si, minimum_wage, overtime_rate_multiplier, normal_working_hours_daily, weekly_holidays_en, weekly_holidays_si, notes_en, notes_si)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, wages_boards_data)
        
    # Seed Labor Offices if empty
    cursor.execute("SELECT COUNT(*) FROM labor_offices")
    if cursor.fetchone()[0] == 0:
        labor_offices_data = [
            (
                "Department of Labour (Head Office)",
                "කම්කරු දෙපාර්තමේන්තුව (ප්‍රධාන කාර්යාලය)",
                "Labour Secretariat, Narahenpita, Colombo 05",
                "කම්කරු මහ ලේකම් කාර්යාලය, නාරාහේන්පිට, කොළඹ 05",
                "+94 11 258 5780"
            ),
            (
                "District Labour Office - Colombo North",
                "දිස්ත්‍රික් කම්කරු කාර්යාලය - කොළඹ උතුර",
                "No. 120, Grandpass Road, Colombo 14",
                "නො. 120, ග්‍රෑන්ඩ්පාස් පාර, කොළඹ 14",
                "+94 11 243 4514"
            ),
            (
                "District Labour Office - Colombo South",
                "දිස්ත්‍රික් කම්කරු කාර්යාලය - කොළඹ දකුණ",
                "No. 94, Kirulapone Avenue, Colombo 05",
                "නො. 94, කිරුළපන මාවත, කොළඹ 05",
                "+94 11 251 3241"
            ),
            (
                "District Labour Office - Gampaha",
                "දිස්ත්‍රික් කම්කරු කාර්යාලය - ගම්පහ",
                "No. 14, Ja-Ela Road, Gampaha",
                "නො. 14, ජා-ඇල පාර, ගම්පහ",
                "+94 33 222 2271"
            ),
            (
                "District Labour Office - Kandy",
                "දිස්ත්‍රික් කම්කරු කාර්යාලය - මහනුවර",
                "No. 22, Getambe, Kandy",
                "නො. 22, ගැටඹේ, මහනුවර",
                "+94 81 222 2280"
            ),
            (
                "District Labour Office - Galle",
                "දිස්ත්‍රික් කම්කරු කාර්යාලය - ගාල්ල",
                "C.M.O. Building, Galle",
                "C.M.O. ගොඩනැගිල්ල, ගාල්ල",
                "+94 91 223 4293"
            )
        ]
        cursor.executemany("""
        INSERT INTO labor_offices (name_en, name_si, address_en, address_si, phone)
        VALUES (?, ?, ?, ?, ?)
        """, labor_offices_data)
        
    # Seed FAQ if empty
    cursor.execute("SELECT COUNT(*) FROM faq")
    if cursor.fetchone()[0] == 0:
        faq_data = [
            (
                "What is EPF? What are the contribution percentages?",
                "EPF යනු කුමක්ද? දායකත්ව ප්‍රතිශතයන් කොපමණද?",
                "The Employees' Provident Fund (EPF) is a retirement benefit scheme. The employee contributes 8% of total earnings, and the employer contributes 12% of total earnings.",
                "සේවක අර්ථසාධක අරමුදල (EPF) යනු විශ්‍රාම ප්‍රතිලාභ ක්‍රමයකි. සේවකයා තම මුළු ඉපැයීමෙන් 8%ක් ද, සේවායෝජකයා 12%ක් ද දායකත්වයක් ලබා දිය යුතුය.",
                "EPF/ETF"
            ),
            (
                "What is ETF? What is the contribution percentage?",
                "ETF යනු කුමක්ද? දායකත්ව ප්‍රතිශතය කොපමණද?",
                "The Employees' Trust Fund (ETF) is another social security scheme. The employer contributes 3% of the employee's total monthly earnings. No deduction is made from the employee's salary.",
                "සේවක භාරකාර අරමුදල (ETF) යනු තවත් සමාජ ආරක්ෂණ ක්‍රමයකි. සේවායෝජකයා සේවකයාගේ මුළු මාසික ඉපැයීමෙන් 3%ක දායකත්වයක් දිය යුතුය. සේවකයාගේ වැටුපෙන් කිසිවක් අඩු නොකෙරේ.",
                "EPF/ETF"
            ),
            (
                "When is an employee eligible for Gratuity?",
                "සේවකයෙකුට පාරිතෝෂික (Gratuity) හිමිවීමට සුදුසුකම් මොනවාද?",
                "An employee who has completed 5 years of continuous service with an employer who has 15 or more employees at any time in the preceding 12 months is entitled to Gratuity.",
                "යම් සේවායෝජකයෙකු යටතේ වසර 5ක අඛණ්ඩ සේවා කාලයක් සම්පූර්ණ කර ඇති, සහ එම සේවායෝජකයා යටතේ පෙර මාස 12 තුළ සේවකයින් 15 දෙනෙකු හෝ වැඩි ගණනක් සේවය කර තිබේ නම් පාරිතෝෂික (Gratuity) හිමිවේ.",
                "Gratuity"
            ),
            (
                "How is Gratuity calculated for shop and office employees?",
                "කඩසාප්පු සහ කාර්යාල සේවකයින්ගේ පාරිතෝෂිකය ගණනය කරන්නේ කෙසේද?",
                "For each completed year of service, the employee is entitled to half a month's basic salary, based on the last drawn basic salary.\nFormula: (Last drawn Basic Salary / 2) * Completed Years of Service.",
                "සම්පූර්ණ කරන ලද සෑම සේවා වසරක් සඳහාම, අවසන් වරට ලබාගත් මූලික වැටුප මත පදනම්ව මාස භාගයක මූලික වැටුපක් හිමිවේ.\nසූත්‍රය: (අවසන් මූලික වැටුප / 2) * සම්පූර්ණ කරන ලද සේවා වර්ෂ.",
                "Gratuity"
            ),
            (
                "What are the leave entitlements under the Shop & Office Employees Act?",
                "කඩසාප්පු සහ කාර්යාල සේවක පනත යටතේ හිමිවන නිවාඩු මොනවාද?",
                "In the first year of employment: 1 day for every 2 completed months (max 14 days annual leave). Second year onwards: 14 days annual leave and 7 days casual/sick leave.",
                "පළමු සේවා වසරේදී: සම්පූර්ණ කරන ලද සෑම මාස 2කටම දින 1 බැගින් (උපරිම දින 14 වාර්ෂික නිවාඩු). දෙවන වසරේ සිට: දින 14ක වාර්ෂික නිවාඩු සහ දින 7ක අනියම්/ලෙඩ නිවාඩු හිමිවේ.",
                "Leave & Holidays"
            ),
            (
                "What is the daily working hours limit under the Shop & Office Act?",
                "කඩසාප්පු සහ කාර්යාල සේවක පනත යටතේ දිනකට උපරිම වැඩ කළ හැකි පැය ගණන කීයද?",
                "The normal working hours limit is 8 hours per day, excluding 1 hour for meals/rest (total 9 hours on-site). Total weekly hours must not exceed 45 hours.",
                "සාමාන්‍ය වැඩ කරන පැය ගණන දිනකට පැය 8කි. කෑම සහ විවේකය සඳහා පැය 1ක් හැර (මුළු පැය 9ක් සේවා ස්ථානයේ). සතියක උපරිම වැඩ කරන පැය ගණන 45 නොඉක්මවිය යුතුය.",
                "Working Hours"
            ),
            (
                "How is Overtime calculated for Shop & Office employees?",
                "කඩසාප්පු සහ කාර්යාල සේවකයින්ගේ අතිකාල ගණනය කරන්නේ කෙසේද?",
                "Hourly Rate = Basic Salary / 240.\nOvertime Pay = Hourly Rate * 1.5 * Overtime Hours worked.",
                "පැයක සාමාන්‍ය වේතනය = මූලික වැටුප / 240.\nඅතිකාල ගෙවීම = පැයක වේතනය * 1.5 * අතිකාල පැය ගණන.",
                "Overtime"
            ),
            (
                "What are the Maternity Benefits entitlements?",
                "ප්‍රසූතිකාධාර (Maternity Benefits) හිමිකම් මොනවාද?",
                "Under recent amendments, a female employee is entitled to 84 working days of paid maternity leave for all live births, regardless of whether it is the first, second, or subsequent child.",
                "මෑතකාලීන සංශෝධන යටතේ, සේවිකාවකට පළමු, දෙවන හෝ ඕනෑම දරු ප්‍රසූතියක් සඳහා දින 84ක වැටුප් සහිත ප්‍රසූතිකාධාර නිවාඩු හිමිවේ.",
                "Maternity"
            )
        ]
        cursor.executemany("""
        INSERT INTO faq (question_en, question_si, answer_en, answer_si, category)
        VALUES (?, ?, ?, ?, ?)
        """, faq_data)
        
    conn.commit()

# Save a calculation to history
def save_calculation(user_id, username, calc_type, inputs_dict, results_dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    calculated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inputs_json = json.dumps(inputs_dict)
    results_json = json.dumps(results_dict)
    
    cursor.execute("""
    INSERT INTO calculation_history (user_id, username, calc_type, inputs, results, calculated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, username, calc_type, inputs_json, results_json, calculated_at))
    conn.commit()
    conn.close()

# Retrieve past calculations for a user
def get_user_history(user_id, limit=5):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, calc_type, inputs, results, calculated_at 
    FROM calculation_history 
    WHERE user_id = ? 
    ORDER BY id DESC 
    LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "id": row["id"],
            "calc_type": row["calc_type"],
            "inputs": json.loads(row["inputs"]),
            "results": json.loads(row["results"]),
            "calculated_at": row["calculated_at"]
        })
    return history

# Get all Wages Boards
def get_all_wages_boards():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wages_boards")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Get specific Wages Board by ID
def get_wages_board_by_id(wb_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wages_boards WHERE id = ?", (wb_id,))
    row = cursor.fetchone()
    conn.close()
    return row

# Get all Labor Offices
def get_all_labor_offices():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM labor_offices")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Search FAQ
def search_faqs(query):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Search in both English and Sinhala questions/answers
    cursor.execute("""
    SELECT * FROM faq 
    WHERE question_en LIKE ? OR question_si LIKE ? OR answer_en LIKE ? OR answer_si LIKE ?
    """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Get FAQs by Category
def get_faqs_by_category(category):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faq WHERE category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Get all FAQ categories
def get_faq_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM faq")
    rows = cursor.fetchall()
    conn.close()
    return [r["category"] for r in rows]

if __name__ == "__main__":
    # Test initialization
    init_db()
    print("Database initialized successfully.")

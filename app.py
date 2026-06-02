from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import database
import calculators
import ai_assistant

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Initialize DB on server start
database.init_db()

@app.route('/')
def home():
    return render_template('index.html')

# Endpoint: PWA Manifest & Service Worker
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

# Endpoint: EPF/ETF Calculator
@app.route('/api/calculate/epf', methods=['POST'])
def api_calc_epf():
    data = request.get_json() or {}
    try:
        basic = float(data.get('basic', 0))
        allowances = float(data.get('allowances', 0))
        if basic <= 0 or allowances < 0:
            return jsonify({"error": "Invalid basic salary or allowances value"}), 400
        
        result = calculators.calculate_epf_etf(basic, allowances)
        
        # Save calculation to DB (default user ID 0 for web portal)
        database.save_calculation(
            user_id=0,
            username="Web_User",
            calc_type="EPF/ETF",
            inputs_dict={"basic": basic, "allowances": allowances},
            results_dict=result
        )
        return jsonify(result)
    except ValueError:
        return jsonify({"error": "Invalid salary numbers"}), 400

# Endpoint: Gratuity Calculator
@app.route('/api/calculate/gratuity', methods=['POST'])
def api_calc_gratuity():
    data = request.get_json() or {}
    try:
        basic = float(data.get('basic', 0))
        years = int(data.get('years', 0))
        if basic <= 0 or years < 0:
            return jsonify({"error": "Invalid basic salary or years of service"}), 400
        
        result = calculators.calculate_gratuity(basic, years)
        
        # Save to DB
        database.save_calculation(
            user_id=0,
            username="Web_User",
            calc_type="Gratuity",
            inputs_dict={"basic": basic, "years": years},
            results_dict={"gratuity_amount": result["gratuity_amount"], "eligible": result["eligible"]}
        )
        return jsonify(result)
    except ValueError:
        return jsonify({"error": "Invalid input numbers"}), 400

# Endpoint: Overtime Calculator
@app.route('/api/calculate/ot', methods=['POST'])
def api_calc_ot():
    data = request.get_json() or {}
    try:
        basic = float(data.get('basic', 0))
        hours = float(data.get('hours', 0))
        divisor = float(data.get('divisor', 240))
        if basic <= 0 or hours < 0 or divisor <= 0:
            return jsonify({"error": "Invalid basic, hours, or divisor value"}), 400
        
        result = calculators.calculate_overtime(basic, hours, divisor)
        
        # Save to DB
        database.save_calculation(
            user_id=0,
            username="Web_User",
            calc_type="Overtime",
            inputs_dict={"basic": basic, "hours": hours, "divisor": divisor},
            results_dict=result
        )
        return jsonify(result)
    except ValueError:
        return jsonify({"error": "Invalid overtime numbers"}), 400

# Endpoint: AI Assistant Chat
@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()

    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "error": "Message is empty"
        }), 400

    response = ai_assistant.ask_ai_assistant(user_message)

    return jsonify({
        "response": response
    })

# Endpoint: Fetch Wages Boards
@app.route('/api/wages_boards', methods=['GET'])
def api_wages_boards():
    boards = database.get_all_wages_boards()
    result = []
    for b in boards:
        result.append({
            "id": b["id"],
            "trade_name_en": b["trade_name_en"],
            "trade_name_si": b["trade_name_si"],
            "minimum_wage": b["minimum_wage"],
            "overtime_rate_multiplier": b["overtime_rate_multiplier"],
            "normal_working_hours_daily": b["normal_working_hours_daily"],
            "weekly_holidays_en": b["weekly_holidays_en"],
            "weekly_holidays_si": b["weekly_holidays_si"],
            "notes_en": b["notes_en"],
            "notes_si": b["notes_si"]
        })
    return jsonify(result)

# Endpoint: Fetch Labor Offices
@app.route('/api/labor_offices', methods=['GET'])
def api_labor_offices():
    offices = database.get_all_labor_offices()
    result = []
    for o in offices:
        result.append({
            "id": o["id"],
            "name_en": o["name_en"],
            "name_si": o["name_si"],
            "address_en": o["address_en"],
            "address_si": o["address_si"],
            "phone": o["phone"]
        })
    return jsonify(result)

# Endpoint: Fetch FAQs
@app.route('/api/faq', methods=['GET'])
def api_faq():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faq")
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "question_en": r["question_en"],
            "question_si": r["question_si"],
            "answer_en": r["answer_en"],
            "answer_si": r["answer_si"],
            "category": r["category"]
        })
    return jsonify(result)

# Endpoint: Fetch Web user history
@app.route('/api/history', methods=['GET'])
def api_history():
    history = database.get_user_history(user_id=0, limit=10)
    return jsonify(history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

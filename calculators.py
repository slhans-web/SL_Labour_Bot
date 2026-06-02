def calculate_epf_etf(basic_salary, allowances=0.0):
    """
    Calculates EPF and ETF.
    EPF is calculated on basic salary + standard allowances.
    Employee contributes 8%.
    Employer contributes 12% to EPF and 3% to ETF.
    """
    total_earnings = float(basic_salary) + float(allowances)
    
    epf_employee = round(total_earnings * 0.08, 2)
    epf_employer = round(total_earnings * 0.12, 2)
    epf_total = round(epf_employee + epf_employer, 2)
    etf_employer = round(total_earnings * 0.03, 2)
    
    # Net salary after 8% EPF deduction (only basic + allowance considered here)
    net_salary_base = round(total_earnings - epf_employee, 2)
    
    return {
        "total_earnings": total_earnings,
        "epf_employee": epf_employee,
        "epf_employer": epf_employer,
        "epf_total": epf_total,
        "etf_employer": etf_employer,
        "net_salary_base": net_salary_base
    }

def calculate_gratuity(last_drawn_basic, completed_years):
    """
    Calculates Gratuity.
    Requires at least 5 years of service.
    Formula: 1/2 of last drawn monthly basic salary for each completed year.
    Note: Standard applies to companies with 15 or more employees.
    """
    years = int(completed_years)
    salary = float(last_drawn_basic)
    
    if years < 5:
        return {
            "eligible": False,
            "gratuity_amount": 0.0,
            "message_en": "Not eligible (Requires minimum 5 years of service).",
            "message_si": "පාරිතෝෂික ලබා ගැනීමට සුදුසුකම් නොලබයි (අවම වශයෙන් වසර 5ක සේවා කාලයක් අවශ්‍ය වේ)."
        }
    
    gratuity_amount = round((salary / 2.0) * years, 2)
    return {
        "eligible": True,
        "gratuity_amount": gratuity_amount,
        "message_en": "Eligible for Gratuity.",
        "message_si": "පාරිතෝෂික ලබා ගැනීමට සුදුසුකම් ලබයි."
    }

def calculate_overtime(basic_salary, ot_hours, custom_divisor=240.0, multiplier=1.5):
    """
    Calculates Overtime.
    Formula: (Basic Salary / 240) * 1.5 * Overtime Hours.
    240 is the standard hourly divisor for shop & office employees.
    """
    salary = float(basic_salary)
    hours = float(ot_hours)
    divisor = float(custom_divisor)
    
    hourly_rate = round(salary / divisor, 2)
    ot_hourly_rate = round(hourly_rate * multiplier, 2)
    ot_pay = round(ot_hourly_rate * hours, 2)
    total_pay = round(salary + ot_pay, 2)
    
    return {
        "hourly_rate": hourly_rate,
        "ot_hourly_rate": ot_hourly_rate,
        "ot_pay": ot_pay,
        "total_pay": total_pay
    }

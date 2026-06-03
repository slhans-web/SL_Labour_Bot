/* ==========================================================================
   Labor Officer Assistant - Frontend JavaScript Logic
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    
    // ----------------- State Configuration -----------------
    let currentLang = 'en'; // Default language: English
    let wagesBoardsData = [];
    let officesData = [];
    let faqsData = [];
    
    // Translation dictionary
    const translations = {
        si: {
            menu_dashboard: "ප්‍රධාන පුවරුව",
            menu_calculators: "කැල්කියුලේටර්",
            menu_wages: "පඩිපාලක සභා",
            menu_ai: "AI සහායකයා",
            menu_laws: "නීති සහ FAQs",
            menu_directory: "කම්කරු කාර්යාල",
            menu_dashboard_short: "පුවරුව",
            menu_calculators_short: "කැල්ක්",
            menu_wages_short: "පඩිපාලක",
            menu_ai_short: "AI සහකරු",
            menu_laws_short: "FAQs",
            app_title: "කම්කරු නිලධාරී සහායක",
            welcome_back: "ආයුබෝවන්, කම්කරු නිලධාරිතුමනි",
            welcome_sub: "කැල්කියුලේටර්, පඩිපාලක සභා තීරණ සහ AI ලිපි කෙටුම්පත් කිරීම් සියල්ල එකම තැනකින්.",
            dash_calc_desc: "EPF, ETF, පාරිතෝෂිකය (Gratuity) සහ අතිකාල (OT) වේගයෙන් ගණනය කරන්න.",
            dash_wages_desc: "ආරක්ෂක, තේ වගාව, ප්‍රවාහන සහ ඉංජිනේරු අංශවල අවම වැටුප් නීති මෙතැනින් බලන්න.",
            dash_ai_desc: "සේවායෝජකයන්ට යවන අනතුරු ඇඟවීමේ ලිපි, පැමිණිලි සාරාංශ සහ චෙක්ලිස්ට් AI එකෙන් විනාඩියෙන් හදන්න.",
            recent_calcs: "මෑතකාලීන ගණනය කිරීම්",
            calc_hub_sub: "ශ්‍රී ලංකා කම්කරු රෙගුලාසි මත පදනම්ව statutory ගණනය කිරීම් පහසුවෙන් සිදු කරන්න.",
            epf_calc_title: "EPF/ETF දත්ත ඇතුලත් කරන්න",
            label_basic: "මාසික මූලික වැටුප (රු.)",
            label_allowance: "ස්ථාවර දීමනා (රු.)",
            btn_calculate: "ගණනය කරන්න",
            calc_results: "ප්‍රතිඵල වාර්තාව",
            results_placeholder: "ගණනය කිරීම් බැලීමට ඉහත විස්තර ඇතුළත් කරන්න.",
            res_total_earnings: "ලැබෙන මුළු වැටුප (Earnings)",
            res_employee_epf: "සේවක EPF දායකත්වය (8%)",
            res_employer_epf: "සේවායෝජක EPF දායකත්වය (12%)",
            res_total_epf: "මුළු EPF එකතුව (20%)",
            res_employer_etf: "සේවායෝජක ETF දායකත්වය (3%)",
            res_net_salary: "EPF අඩු කිරීමෙන් පසු ශේෂය",
            epf_notes: "සේවායෝජකයා 12% EPF සහ 3% ETF දායකත්වය සම්පූර්ණයෙන්ම තමාගේ වියදමෙන් ගෙවිය යුතු අතර, සේවකයාගේ වැටුපෙන් අඩු කළ හැක්කේ 8% පමණි.",
            gratuity_calc_title: "පාරිතෝෂික (Gratuity) දත්ත ඇතුලත් කරන්න",
            label_last_basic: "අවසන් වරට ලබාගත් මූලික වැටුප (රු.)",
            label_service: "අඛණ්ඩ සේවා කාලය (සම්පූර්ණ කළ වසර ගණන)",
            res_gratuity_eligible: "හිමිකම් සුදුසුකම",
            res_gratuity_due: "හිමිවන පාරිතෝෂික මුදල",
            gratuity_notes: "සේවකයින් 15ක් හෝ ඊට වැඩි ආයතනයක වසර 5ක් අඛණ්ඩව සේවය කළ අයෙකුට අවසන් මූලික වැටුප මත පදනම්ව සෑම සේවා වසරකටම මාස භාගයක වැටුප බැගින් පාරිතෝෂිකය හිමිවේ.",
            ot_calc_title: "අතිකාල (OT) දත්ත ඇතුලත් කරන්න",
            label_ot_hours: "සිදු කළ අතිකාල පැය ගණන",
            label_divisor: "මාසික පැය බෙදුම්කරු (සම්මත 240)",
            res_hourly_rate: "සාමාන්‍ය පැයක වේතනය",
            res_ot_hourly: "OT පැයක වේතනය (1.5x)",
            res_ot_pay: "මුළු අතිකාල ගෙවීම",
            res_total_salary: "මුළු වැටුප (මූලික + OT)",
            ot_notes: "කඩසාප්පු සහ කාර්යාල සේවකයින්ගේ අතිකාල ගණනයට සම්මත බෙදුම්කරු 240 වන අතර 1.5 ගුණයක අනුපාතයකට OT ගෙවිය යුතුය. සතියකට උපරිම OT පැය 12කි.",
            wages_boards_title: "පඩිපාලක සභා තීරණ",
            wages_boards_sub: "විවිධ කර්මාන්ත සඳහා නියමිත අවම වැටුප්, සතිපතා නිවාඩු සහ අතිකාල කොන්දේසි.",
            ai_assistant_title: "AI කම්කරු සහකරු",
            ai_intro: "කම්කරු නඩු සාරාංශ, ලිපි කෙටුම්පත් කිරීම්, කර්මාන්තශාලා පරීක්ෂණ චෙක්ලිස්ට් ආදී ඕනෑම ප්‍රශ්නයක් සිංහලෙන් හෝ ඉංග්‍රීසියෙන් විමසන්න.",
            try_asking: "මෙසේ අසා බලන්න:",
            ai_name: "AI කම්කරු සහකරු",
            ai_welcome: "ආයුබෝවන්! මම ඔබගේ AI කම්කරු නීති සහායකයා වෙමි. සේවායෝජකයන්ට අනතුරු ඇඟවීමේ ලිපි ලිවීම, පරීක්ෂණ වාර්තා සකස් කිරීම හෝ සේවක අයිතිවාසිකම් පිළිබඳ ගැටලු ඕනෑම දෙයක් මෙතැනින් කෙලින්ම විමසන්න. මම විනාඩියක් ඇතුළත පිළිතුරු සකස් කර දෙන්නෙමි!",
            ai_thinking: "AI පිළිතුර සකස් කරමින් පවතී...",
            faq_subtitle: "EPF/ETF, නිවාඩු හිමිකම් සහ ප්‍රසූතිකාධාර පිළිබඳ මූලික නීතිමය මාර්ගෝපදේශ.",
            directory_sub: "කම්කරු දෙපාර්තමේන්තු ප්‍රධාන කාර්යාලය සහ දිස්ත්‍රික් කාර්යාලවල දුරකථන අංක සහ ලිපින.",
            eligible_yes: "සුදුසුකම් ලබයි",
            eligible_no: "සුදුසුකම් නොලබයි (අවම වසර 5ක් අවශ්‍ය වේ)"
        },
        en: {
            menu_dashboard: "Dashboard",
            menu_calculators: "Calculators",
            menu_wages: "Wages Boards",
            menu_ai: "AI Assistant",
            menu_laws: "Laws & FAQs",
            menu_directory: "Labor Offices",
            menu_dashboard_short: "Dashboard",
            menu_calculators_short: "Calcs",
            menu_wages_short: "Wages",
            menu_ai_short: "AI Chat",
            menu_laws_short: "FAQs",
            app_title: "Labor Officer Assistant",
            welcome_back: "Welcome, Labor Officer",
            welcome_sub: "Access calculators, Wages Board summaries, and AI drafting tools on the go.",
            dash_calc_desc: "Calculate EPF, ETF, Gratuity, and Overtime instantly.",
            dash_wages_desc: "Access standard rates for Security, Tea, Transport, and Engineering trades.",
            dash_ai_desc: "Draft formal notice letters, warning letters, and compile inspection reports instantly.",
            recent_calcs: "Recent Web Calculations",
            calc_hub_sub: "Perform statutory calculations based on Sri Lankan Labor regulations.",
            epf_calc_title: "EPF/ETF Input",
            label_basic: "Monthly Basic Salary (LKR)",
            label_allowance: "Fixed Allowances (LKR)",
            btn_calculate: "Calculate",
            calc_results: "Results",
            results_placeholder: "Enter details to see calculations.",
            res_total_earnings: "Total Earnings",
            res_employee_epf: "Employee EPF (8%)",
            res_employer_epf: "Employer EPF (12%)",
            res_total_epf: "Total EPF (20%)",
            res_employer_etf: "Employer ETF (3%)",
            res_net_salary: "Net Salary Base",
            epf_notes: "The employer must bear the 12% EPF and 3% ETF entirely, and only 8% can be deducted from the employee's salary.",
            gratuity_calc_title: "Gratuity Input",
            label_last_basic: "Last Drawn Basic Salary (LKR)",
            label_service: "Completed Years of Service",
            res_gratuity_eligible: "Eligibility",
            res_gratuity_due: "Gratuity Amount Due",
            gratuity_notes: "Under the Gratuity Act, employees with 5 or more years of service in firms with 15 or more workmen are entitled to a lump-sum payment equivalent to half-month basic salary for each completed year of service.",
            ot_calc_title: "Overtime Input",
            label_ot_hours: "Overtime Hours Worked",
            label_divisor: "Hours Divisor (Default 240)",
            res_hourly_rate: "Ordinary Hourly Rate",
            res_ot_hourly: "OT Hourly Rate (1.5x)",
            res_ot_pay: "Total Overtime Pay",
            res_total_salary: "Total (Basic + OT)",
            ot_notes: "For Shop and Office employees, standard OT is calculated using a 240 divisor at a 1.5x multiplier. Weekly overtime limit is 12 hours.",
            wages_boards_title: "Wages Board Determinations",
            wages_boards_sub: "Statutory minimum salaries, weekly holidays, and working conditions for key Sri Lankan industries.",
            ai_assistant_title: "AI Labor Expert",
            ai_intro: "Draft letters, warnings, memos, checklists, or get instant legally-grounded answers to any complex dispute scenario.",
            try_asking: "Try asking:",
            ai_name: "AI Labor Assistant",
            ai_welcome: "Hello! I am your AI Labor Assistant. Type any question, dispute case, or request for letter drafting/inspection checklists. I will generate professional, legally-grounded compliance answers based on Sri Lankan laws in Sinhala or English!",
            ai_thinking: "AI is thinking...",
            faq_subtitle: "Quick reference on standard labor law topics including EPF/ETF, leave policies, and maternity benefits.",
            directory_sub: "Find phone numbers and addresses for the Department of Labour Head Office and District branches.",
            eligible_yes: "Eligible for Gratuity",
            eligible_no: "Not eligible (Requires minimum 5 years of service)"
        }
    };

    // Translate all elements on page
    function applyTranslations() {
        const elements = document.querySelectorAll('[data-trans]');
        elements.forEach(el => {
            const key = el.getAttribute('data-trans');
            if (translations[currentLang][key]) {
                el.textContent = translations[currentLang][key];
            }
        });
        
        // Translate placeholders
        const epfBasicInput = document.getElementById('epf-basic');
        const epfAllowanceInput = document.getElementById('epf-allowance');
        const gratuityBasicInput = document.getElementById('gratuity-basic');
        const gratuityYearsInput = document.getElementById('gratuity-years');
        const otBasicInput = document.getElementById('ot-basic');
        const otHoursInput = document.getElementById('ot-hours');
        const chatInput = document.getElementById('chat-input');
        
        if (currentLang === 'si') {
            epfBasicInput.placeholder = "උදා: 50000";
            epfAllowanceInput.placeholder = "උදා: 10000";
            gratuityBasicInput.placeholder = "උදා: 60000";
            gratuityYearsInput.placeholder = "උදා: 7";
            otBasicInput.placeholder = "උදා: 48000";
            otHoursInput.placeholder = "උදා: 15";
            chatInput.placeholder = "ඔබට අවශ්‍ය ප්‍රශ්නය මෙහි ලියා එවන්න...";
            document.getElementById('lang-label').textContent = "English";
            document.getElementById('mobile-lang-toggle').textContent = "EN";
        } else {
            epfBasicInput.placeholder = "e.g. 50000";
            epfAllowanceInput.placeholder = "e.g. 10000";
            gratuityBasicInput.placeholder = "e.g. 60000";
            gratuityYearsInput.placeholder = "e.g. 7";
            otBasicInput.placeholder = "e.g. 48000";
            otHoursInput.placeholder = "e.g. 15";
            chatInput.placeholder = "Type your query here...";
            document.getElementById('lang-label').textContent = "සිංහල";
            document.getElementById('mobile-lang-toggle').textContent = "SI";
        }

        // Re-render components with translated static strings
        renderWagesBoards();
        renderLaborOffices();
        renderFAQs();
    }

    // Language Toggle Click Event
    document.getElementById('lang-toggle-btn').addEventListener('click', toggleLanguage);
    document.getElementById('mobile-lang-toggle').addEventListener('click', toggleLanguage);

    function toggleLanguage() {
        currentLang = (currentLang === 'si') ? 'en' : 'si';
        applyTranslations();
    }

    // ----------------- Tab Switcher System -----------------
    const menuItems = document.querySelectorAll('.menu-item, .mobile-nav-item');
    const tabPanes = document.querySelectorAll('.tab-pane');

    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });

    // Handle dashboard action cards clicks to change tab
    const actionCards = document.querySelectorAll('.action-card');
    actionCards.forEach(card => {
        card.addEventListener('click', () => {
            const targetTab = card.getAttribute('data-tab-link');
            switchTab(targetTab);
        });
    });

    function switchTab(tabId) {
        // Update active tab buttons
        menuItems.forEach(btn => {
            if (btn.getAttribute('data-tab') === tabId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Show/hide tab contents
        tabPanes.forEach(pane => {
            if (pane.id === `tab-${tabId}`) {
                pane.classList.add('active');
            } else {
                pane.classList.remove('active');
            }
        });
        
        // Scroll to top
        document.querySelector('.main-content').scrollTop = 0;

        // Custom action triggers on tab entering
        if (tabId === 'dashboard') {
            loadCalculationHistory();
        }
    }

    // Mobile menu drawer toggle
    document.getElementById('mobile-menu-toggle').addEventListener('click', () => {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar.style.display === 'flex') {
            sidebar.style.display = 'none';
        } else {
            sidebar.style.display = 'flex';
            sidebar.style.position = 'absolute';
            sidebar.style.height = '100%';
            sidebar.style.width = '240px';
        }
    });

    // ----------------- Calculators Switching -----------------
    const calcTabs = document.querySelectorAll('.calc-tab');
    const calcContainers = document.querySelectorAll('.calc-form-container');

    calcTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            calcTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const targetCalc = tab.getAttribute('data-calc');
            calcContainers.forEach(c => {
                if (c.id === `calc-${targetCalc}`) {
                    c.classList.add('active');
                } else {
                    c.classList.remove('active');
                }
            });
        });
    });

    // ----------------- Calculation API Requests -----------------

    // 1. EPF/ETF Submit
    document.getElementById('epf-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const basic = parseFloat(document.getElementById('epf-basic').value);
        const allowances = parseFloat(document.getElementById('epf-allowance').value);

        try {
            const res = await fetch('/api/calculate/epf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ basic, allowances })
            });
            const data = await res.json();
            
            if (data.error) {
                alert(data.error);
                return;
            }

            document.getElementById('epf-results-placeholder').style.display = 'none';
            document.getElementById('epf-results-display').style.display = 'flex';

            document.getElementById('res-epf-earnings').textContent = `LKR ${data.total_earnings.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('res-epf-employee').textContent = `LKR ${data.epf_employee.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('res-epf-employer').textContent = `LKR ${data.epf_employer.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('res-epf-total').textContent = `LKR ${data.epf_total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('res-etf-employer').textContent = `LKR ${data.etf_employer.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('res-epf-net').textContent = `LKR ${data.net_salary_base.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        } catch (err) {
            console.error(err);
            alert("Calculation failed.");
        }
    });

    // 2. Gratuity Submit
    document.getElementById('gratuity-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const basic = parseFloat(document.getElementById('gratuity-basic').value);
        const years = parseInt(document.getElementById('gratuity-years').value);

        try {
            const res = await fetch('/api/calculate/gratuity', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ basic, years })
            });
            const data = await res.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            document.getElementById('gratuity-results-placeholder').style.display = 'none';
            document.getElementById('gratuity-results-display').style.display = 'flex';

            const eligLabel = document.getElementById('res-gratuity-eligibility');
            if (data.eligible) {
                eligLabel.textContent = translations[currentLang].eligible_yes;
                eligLabel.className = "res-val font-accent";
            } else {
                eligLabel.textContent = translations[currentLang].eligible_no;
                eligLabel.className = "res-val text-red-500";
            }

            document.getElementById('res-gratuity-amount').textContent = `LKR ${data.gratuity_amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        } catch (err) {
            console.error(err);
            alert("Calculation failed.");
        }
    });

    // 3. Overtime Submit
    document.getElementById('ot-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const basic = parseFloat(document.getElementById('ot-basic').value);
        const hours = parseFloat(document.getElementById('ot-hours').value);
        const divisor = parseFloat(document.getElementById('ot-divisor').value);

        try {
            const res = await fetch('/api/calculate/ot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ basic, hours, divisor })
            });
            const data = await res.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            document.getElementById('ot-results-placeholder').style.display = 'none';
            document.getElementById('ot-results-display').style.display = 'flex';

            document.getElementById('res-ot-hourly').textContent = `LKR ${data.hourly_rate.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('res-ot-hourly-rate').textContent = `LKR ${data.ot_hourly_rate.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('res-ot-pay').textContent = `LKR ${data.ot_pay.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('res-ot-total').textContent = `LKR ${data.total_pay.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        } catch (err) {
            console.error(err);
            alert("Calculation failed.");
        }
    });

    // ----------------- AI Chat Assistant Interface -----------------
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages-container');
    const thinkingIndicator = document.getElementById('chat-thinking-indicator');

    // Trigger AI Chat Submit
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text) return;

        chatInput.value = '';
        
        // Append user bubble
        appendChatBubble(text, 'user');
        
        // Show thinking indicator
        thinkingIndicator.style.display = 'flex';
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();

            // Hide thinking indicator
            thinkingIndicator.style.display = 'none';

            if (data.error) {
                appendChatBubble(`❌ Error: ${data.error}`, 'system');
            } else {
                appendChatBubble(data.response, 'system');
            }
        } catch (err) {
            thinkingIndicator.style.display = 'none';
            console.error(err);
            appendChatBubble("❌ Connection failure with AI server.", 'system');
        }
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });

    function appendChatBubble(text, sender) {
        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${sender}`;
        
        const header = document.createElement('div');
        header.className = 'bubble-header';
        
        if (sender === 'user') {
            header.innerHTML = `Officer <i class="fa-solid fa-user"></i>`;
        } else {
            header.innerHTML = `<i class="fa-solid fa-robot"></i> ${translations[currentLang].ai_name}`;
        }
        
        const content = document.createElement('div');
        content.className = 'bubble-content';
        content.textContent = text;
        
        bubble.appendChild(header);
        bubble.appendChild(content);
        
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Example Prompt Chips triggers
    const chips = document.querySelectorAll('.example-chip');
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            chatInput.value = chip.textContent;
            chatInput.focus();
        });
    });

    // ----------------- DB List Loading & Search filters -----------------

    // A. Wages Boards Fetch & Rendering
    async function loadWagesBoards() {
        try {
            const res = await fetch('/api/wages_boards');
            wagesBoardsData = await res.json();
            renderWagesBoards();
        } catch (err) {
            console.error("Failed to load Wages Boards data: ", err);
        }
    }

    function renderWagesBoards(filter = '') {
        const container = document.getElementById('wages-boards-list');
        if (!container) return;
        
        container.innerHTML = '';
        
        const filtered = wagesBoardsData.filter(b => {
            const name = (currentLang === 'si') ? b.trade_name_si : b.trade_name_en;
            return name.toLowerCase().includes(filter.toLowerCase());
        });

        if (filtered.length === 0) {
            container.innerHTML = `<div class="loading-placeholder">No Wages Boards found matching search criteria.</div>`;
            return;
        }

        filtered.forEach(b => {
            const name = (currentLang === 'si') ? b.trade_name_si : b.trade_name_en;
            const holidays = (currentLang === 'si') ? b.weekly_holidays_si : b.weekly_holidays_en;
            const notes = (currentLang === 'si') ? b.notes_si : b.notes_en;
            
            const card = document.createElement('div');
            card.className = 'wages-card';
            
            card.innerHTML = `
                <h3 class="wages-title">${name}</h3>
                <div class="wages-detail-row">
                    <span class="label">Minimum Wage/Rate</span>
                    <span class="val">LKR ${b.minimum_wage.toLocaleString('en-US')}</span>
                </div>
                <div class="wages-detail-row">
                    <span class="label">Overtime Rate</span>
                    <span class="val">${b.overtime_rate_multiplier}x</span>
                </div>
                <div class="wages-detail-row">
                    <span class="label">Working Hours</span>
                    <span class="val">${b.normal_working_hours_daily} hrs/day</span>
                </div>
                <div class="wages-detail-row">
                    <span class="label">Weekly Holidays</span>
                    <span class="val">${holidays}</span>
                </div>
                <div class="wages-notes">${notes}</div>
            `;
            container.appendChild(card);
        });
    }

    // Filter Wages Boards by Input
    document.getElementById('wages-search-input').addEventListener('input', (e) => {
        renderWagesBoards(e.target.value);
    });

    // B. Labor Offices Directory Fetch & Rendering
    async function loadLaborOffices() {
        try {
            const res = await fetch('/api/labor_offices');
            officesData = await res.json();
            renderLaborOffices();
        } catch (err) {
            console.error("Failed to load Labor Offices directory: ", err);
        }
    }

    function renderLaborOffices(filter = '') {
        const container = document.getElementById('offices-list');
        if (!container) return;
        
        container.innerHTML = '';
        
        const filtered = officesData.filter(o => {
            const name = (currentLang === 'si') ? o.name_si : o.name_en;
            return name.toLowerCase().includes(filter.toLowerCase());
        });

        if (filtered.length === 0) {
            container.innerHTML = `<div class="loading-placeholder">No offices found matching search criteria.</div>`;
            return;
        }

        filtered.forEach(o => {
            const name = (currentLang === 'si') ? o.name_si : o.name_en;
            const address = (currentLang === 'si') ? o.address_si : o.address_en;
            
            const card = document.createElement('div');
            card.className = 'office-card';
            
            card.innerHTML = `
                <h3>${name}</h3>
                <div class="office-info">
                    <i class="fa-solid fa-location-dot"></i>
                    <span>${address}</span>
                </div>
                <div class="office-info">
                    <i class="fa-solid fa-phone"></i>
                    <span>${o.phone}</span>
                </div>
            `;
            container.appendChild(card);
        });
    }

    // Filter offices by input
    document.getElementById('offices-search-input').addEventListener('input', (e) => {
        renderLaborOffices(e.target.value);
    });

    // C. FAQs Fetch & Rendering
    async function loadFAQs() {
        try {
            const res = await fetch('/api/faq');
            faqsData = await res.json();
            renderFAQs();
        } catch (err) {
            console.error("Failed to load FAQs: ", err);
        }
    }

    function renderFAQs() {
        const container = document.getElementById('faq-list');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (faqsData.length === 0) {
            container.innerHTML = `<div class="loading-placeholder">No FAQ entries available.</div>`;
            return;
        }

        faqsData.forEach(f => {
            const question = (currentLang === 'si') ? f.question_si : f.question_en;
            const answer = (currentLang === 'si') ? f.answer_si : f.answer_en;
            
            const item = document.createElement('div');
            item.className = 'faq-item';
            
            item.innerHTML = `
                <button class="faq-question">
                    <span>${question}</span>
                    <i class="fa-solid fa-chevron-down"></i>
                </button>
                <div class="faq-answer">${answer}</div>
            `;
            
            // Accordion click toggle
            item.querySelector('.faq-question').addEventListener('click', () => {
                item.classList.toggle('active');
            });

            container.appendChild(item);
        });
    }

    // D. Calculation History Loader
    async function loadCalculationHistory() {
        const container = document.getElementById('recent-calculations-list');
        if (!container) return;

        try {
            const res = await fetch('/api/history');
            const data = await res.json();

            container.innerHTML = '';

            if (data.length === 0) {
                container.innerHTML = `<div class="loading-placeholder">No recent calculations found on this browser.</div>`;
                return;
            }

            data.forEach(item => {
                const div = document.createElement('div');
                div.className = 'history-item';

                let desc = '';
                let resultText = '';

                if (item.calc_type === 'EPF/ETF') {
                    desc = `Basic: LKR ${item.inputs.basic.toLocaleString()} | Allowance: LKR ${item.inputs.allowances.toLocaleString()}`;
                    resultText = `EPF (Total): LKR ${item.results.epf_total.toLocaleString()}`;
                } else if (item.calc_type === 'Gratuity') {
                    desc = `Last Basic: LKR ${item.inputs.basic.toLocaleString()} | Service: ${item.inputs.years} Yrs`;
                    resultText = `Gratuity: LKR ${item.results.gratuity_amount.toLocaleString()}`;
                } else if (item.calc_type === 'Overtime') {
                    desc = `Basic: LKR ${item.inputs.basic.toLocaleString()} | OT: ${item.inputs.hours} hrs`;
                    resultText = `OT Pay: LKR ${item.results.ot_pay.toLocaleString()}`;
                }

                div.innerHTML = `
                    <div class="history-info">
                        <span class="history-type">${item.calc_type}</span>
                        <span class="history-time">${desc}</span>
                        <span class="history-time">${item.calculated_at}</span>
                    </div>
                    <span class="history-result">${resultText}</span>
                `;
                container.appendChild(div);
            });
        } catch (err) {
            console.error("Failed to load calculation history: ", err);
            container.innerHTML = `<div class="loading-placeholder">Error loading calculations history.</div>`;
        }
    }

    // ----------------- Initializations -----------------
    applyTranslations();
    loadWagesBoards();
    loadLaborOffices();
    loadFAQs();
    loadCalculationHistory();

});

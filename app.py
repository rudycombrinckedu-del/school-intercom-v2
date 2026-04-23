from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3
from twilio.rest import Client

app = Flask(__name__)

# 🔐 Twilio credentials (REPLACE THESE)
import os

account_sid = os.environ.get('TWILIO_SID')
auth_token = os.environ.get('TWILIO_TOKEN')
client = Client(account_sid, auth_token)


# 📲 WhatsApp function
def send_whatsapp(name, phone, person, reason):
    client.messages.create(
        from_='whatsapp:+14155238886',
        body=f"""🏫 SCHOOL VISITOR ALERT

👤 Name: {name}
📞 Phone: {phone}
🎯 Visiting: {person}
📝 Reason: {reason}

⏰ Please respond or open gate.""",
        to='whatsapp:+27789203474'
    )
# 🗄️ Create database
def init_db():
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            person TEXT,
            reason TEXT,
            time TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 🏠 Home page
@app.route('/')
def index():
    return render_template('index.html')

# 📩 Handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    phone = request.form['phone']
    person = request.form['person']
    reason = request.form['reason']
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to database
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    c.execute("INSERT INTO visitors (name, phone, person, reason, time) VALUES (?, ?, ?, ?, ?)",
              (name, phone, person, reason, time))
    conn.commit()
    conn.close()

    # Send WhatsApp notification
    send_whatsapp(name, phone, person, reason)

    return redirect('/success')

# ✅ Success page
@app.route('/success')
def success():
    return render_template('success.html')

# 📊 Admin view (see visitors)
@app.route('/admin')
def admin():
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    c.execute("SELECT * FROM visitors ORDER BY id DESC")
    data = c.fetchall()
    conn.close()

    return {"visitors": data}

# ▶️ Run app
if __name__ == '__main__':
   import os

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
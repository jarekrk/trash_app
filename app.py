from flask import Flask, jsonify, request, redirect, render_template
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Trash schedules
trash_mix={"Jan":[9,23],
           "Feb":[6,20],
           "Mar":[6,20],
           "Apr":[3,17],
           "May":[2,16,30],
           "Jun":[13,27],
           "Jul":[11,25],
           "Aug":[8,22],
           "Sep":[5,19],
           "Oct":[3,17,31],
           "Nov":[17,28],
           "Dec":[12,29]
           }

trash_seg={"Jan":[10],
           "Feb":[10],
           "Mar":[10],
           "Apr":[8],
           "May":[12],
           "Jun":[9],
           "Jul":[8],
           "Aug":[8],
           "Sep":[8],
           "Oct":[8],
           "Nov":[12],
           "Dec":[8]
           }
trash_bio={"Jan":[9],
           "Feb":[7],
           "Mar":[7],
           "Apr":[7,22],
           "May":[6,20],
           "Jun":[3,17],
           "Jul":[1,15,29],
           "Aug":[12,26],
           "Sep":[9,23],
           "Oct":[7,21],
           "Nov":[4],
           "Dec":[4]
           }

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Email credentials
sender_email = "janekbez@yahoo.com"
receiver_emails = os.getenv("RECEIVER_EMAILS", "").split(",")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Flask app
app = Flask(__name__)

def send_email(subject, body):
    """Send email using Yahoo SMTP."""
    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_emails)  # Dodanie wszystkich odbiorców
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        # Połączenie z serwerem SMTP
        with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as server:
            server.login(sender_email, EMAIL_PASSWORD)
            server.sendmail(sender_email, receiver_emails, message.as_string())
        print(f"E-mail sent to {', '.join(receiver_emails)}: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_trash_schedule(trash_dict, name):
    """Check trash schedule and send notifications."""
    today = datetime.today()
    hour = today.replace().hour
    mon = today.strftime("%b")
    day = today.day
    if mon in trash_dict:
        for trash_day in trash_dict[mon]:
            if hour == 20:
                if day == trash_day - 1:
                    send_email(f"Jutro wywóz śmieci: {name}", f"Jutro ({mon} {trash_day}) będzie wywóz śmieci: {name}.")
            if hour == 13:
                if day == trash_day:
                    send_email(f"Dzisiaj wywóz śmieci: {name}", f"Dzisiaj ({mon} {trash_day}) jest wywóz śmieci: {name}.")

@app.route("/")
def run_check():
    check_trash_schedule(trash_mix, "Mieszane")
    check_trash_schedule(trash_seg, "Segregowane")
    check_trash_schedule(trash_bio, "Bio!!")
    return "Trash check completed!"


@app.route("/check")
def current_month_trash():
    today = datetime.today()
    mon = today.strftime("%b")
    result = {
        "month": mon,
        "bio": trash_bio[mon],
        "mix": trash_mix[mon],
        "seg": trash_seg[mon]
    }

    return render_template("check.html", result=result)

@app.route('/other', methods=['GET', 'POST'])
def other():
    if request.method == 'POST':
        user_input = request.form.get('month')

        if user_input == "NO":
            return render_template("other.html", message="Dziękuję! Do zobaczenia.", result=None, months=months)

        try:
            check = int(user_input)
            if 1 <= check <= 12:
                month_name = months[check - 1]
                result = {
                    "month": month_name,
                    "bio": trash_bio[month_name],
                    "mix": trash_mix[month_name],
                    "seg": trash_seg[month_name]
                }
                return render_template("other.html", message=None, result=result, months=months)
            else:
                return render_template("other.html", message="Błędny numer miesiąca.", result=None, months=months)
        except ValueError:
            return render_template("other.html", message="Błąd! Wybierz poprawny miesiąc.", result=None, months=months)

    # GET request
    return render_template("other.html", message=None, result=None, months=months)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


import smtplib
from email.mime.text import MIMEText

def send_violation_email(receiver_email, rider_data, plate_number):
    sender_email = "gangadhararahul20@gmail.com"
    sender_password = "kwguaqcghjyueser"

    subject = "🚨 Helmet Violation Detected"

    body = f"""
    Traffic Violation Alert 🚨

    A rider has been detected without wearing a helmet.

    🚗 Vehicle Number: {plate_number}
    👤 Name: {rider_data['name']}
    📱 Mobile: {rider_data['mobile']}
    🎂 Age: {rider_data['age']}
    🏠 Address: {rider_data['address']}

    Please follow traffic rules and wear a helmet.

    Regards,
    Smart Traffic System
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        print(f"📧 Email sent for {plate_number}")

    except Exception as e:
        print("❌ Email Error:", e)
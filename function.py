import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def private(Query):
    # Email configuration
    sender_email = "bamideleprecious85@gmail.com"
    receiver_email = "j.mcelligott@embracingdisruption.com"
    password = "fhdr vwep reuq laxg"
    # Email content
    subject = "Query"
    body = Query

    # Constructing the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Sending the email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())



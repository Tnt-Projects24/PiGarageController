import os
import smtplib
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()


def sendemail(subject, message):
    # Read configuration from .env
    from_addr = os.getenv("EMAIL_FROM")

    to_addr_list = [
        email.strip()
        for email in os.getenv("EMAIL_TO", "").split(",")
        if email.strip()
    ]

    cc_addr_list = [
        email.strip()
        for email in os.getenv("EMAIL_CC", "").split(",")
        if email.strip()
    ]

    smtpserver = os.getenv("SMTP_SERVER")
    smtpport = int(os.getenv("SMTP_PORT", "587"))
    login = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")

    # Build email header
    header = f"From: {from_addr}\n"
    header += f"To: {', '.join(to_addr_list)}\n"

    if cc_addr_list:
        header += f"Cc: {', '.join(cc_addr_list)}\n"

    header += f"Subject: {subject}\n\n"

    email_message = header + message

    # Connect and send email
    server = smtplib.SMTP(smtpserver, smtpport)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(login, password)

    # Include both To and CC recipients
    recipients = to_addr_list + cc_addr_list

    problems = server.sendmail(
        from_addr,
        recipients,
        email_message
    )

    server.quit()

    return problems


if __name__ == "__main__":
    sendemail("subject", "Body")

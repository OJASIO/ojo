import os
import smtplib
import ssl

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

def send_selection_email(candidate_username, password, link):
    """
    Sends an invitation email to a candidate using a secure SSL connection.
    """
    recipient_email = "lassosrhpythonproject@gmail.com"
    subject = "Invitation to Coding Challenge"
    body = f"""
    Hello {candidate_username},

    Congratulations! We were impressed with your profile and would like to invite you to a coding challenge.

    Please use the secure link below to access the platform.

    Coding Platform Link: {link}

    Your login credentials are:
    Username: {candidate_username}
    Password: {password}

    We look forward to your submission. Wish you All the Best.

    Best regards,
    The Hiring Team
    """

    message = f"Subject: {subject}\n\n{body}"
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient_email, message.encode('utf-8'))
            print(f"Email successfully sent to {candidate_username}")
            
    except smtplib.SMTPAuthenticationError:
        print(f"Failed to send email: Authentication failed. Check your email/password or app password.")
    except Exception as e:
        print(f"Failed to send email to {candidate_username}: {e}")


def send_rejection_email(candidate_username,candidate_email):

    recipient_email = "lassosrhpythonproject@gmail.com"
    subject = "Rejection Mail"
    body = f"""
    Hello {candidate_username},

    You are not selected. thankyou for your application.

    Regards,
    Lasso Recruiter
    """
    message = f"Subject: {subject}\n\n{body}"
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient_email, message.encode('utf-8'))
            print(f"Email successfully sent to {candidate_username}")
            
    except smtplib.SMTPAuthenticationError:
        print(f"Failed to send email: Authentication failed. Check your email/password or app password.")
    except Exception as e:
        print(f"Failed to send email to {candidate_username}: {e}")



def send_acceptance_email(candidate_username,candidate_email):
    print("Acceptance Email starts")
    recipient_email = "lassosrhpythonproject@gmail.com"
    subject = "Congratulations!!!! You are Selected"
    print("Subject is:",subject)
    body = f"""
    Hello {candidate_username},

    Congratulations,You are selected for the role of Python Developer. We look forward for your onboarding process.
    
    Within Next 2 to 3 days you will receive an email containing the joining process details.

    Regards,
    Lasso Recruiter
    """
    message = f"Subject: {subject}\n\n{body}"
    
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient_email, message.encode('utf-8'))
            print(f"Email successfully sent to {candidate_username}")
            
    except smtplib.SMTPAuthenticationError:
        print(f"Failed to send email: Authentication failed. Check your email/password or app password.")
    except Exception as e:
        print(f"Failed to send email to {candidate_username}: {e}")


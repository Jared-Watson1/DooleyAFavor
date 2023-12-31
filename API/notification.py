from twilio.rest import Client
from dotenv import load_dotenv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from user_database import get_user_info
from task_database import get_task_info

load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
EMAIL_APP_PASS = os.getenv("EMAIL_APP_PASS")
print(EMAIL_APP_PASS)


def send_email(
    recipient_email, subject, html_message, sender_email="emorydooleyafavor@gmail.com"
):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["To"] = recipient_email
        msg["From"] = sender_email

        # Attach HTML content
        part = MIMEText(html_message, "html")
        msg.attach(part)

        smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp_server.login("emorydooleyafavor", EMAIL_APP_PASS)
        smtp_server.sendmail(msg["From"], recipient_email, msg.as_string())
        smtp_server.quit()
        return "Email sent successfully"
    except Exception as e:
        return f"Error sending email: {e}"


def send_sms_notification(to_number, body, from_number=TWILIO_FROM_NUMBER):
    try:
        message = twilio_client.messages.create(
            body=body, from_=from_number, to=to_number
        )
        print(f"SMS sent successfully: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS: {e}")


def send_accept_notification(task_owner_id, task_acceptor_id, task_id):
    # Fetch user information
    task_owner_info, _ = get_user_info(task_owner_id)
    task_acceptor_info, _ = get_user_info(task_acceptor_id)
    task_details = get_task_info(task_id)

    if not task_owner_info or not task_acceptor_info or not task_details:
        return "User or Task information not found"

    # Format the task details into HTML
    task_details_html = format_task_details_html(task_details)

    # Email content for the task owner
    email_body_owner = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
    <h1 style="color: #4CAF50;">Your task '{task_details['task_name']}' has been accepted</h1>
    <p><strong>Accepted by:</strong> {task_acceptor_info['username']}</p>
    <p><strong>Contact Email:</strong> <a href="mailto:{task_acceptor_info['email']}">{task_acceptor_info['email']}</a></p>
    <p><strong>Contact Phone:</strong> <a href="tel:{task_acceptor_info['phone_number']}">{task_acceptor_info['phone_number']}</a></p>
    {task_details_html}
    <p><a href="https://dooley-8c253088e812.herokuapp.com/templates/posted.html">View your posted tasks</a></p>
    </body>
    </html>
    """

    # Email content for the task acceptor
    email_body_acceptor = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
    <h1 style="color: #4CAF50;">You have successfully accepted the task '{task_details['task_name']}'</h1>
    <p><strong>Task Owner:</strong> {task_owner_info['username']}</p>
    <p><strong>Contact Email:</strong> <a href="mailto:{task_owner_info['email']}">{task_owner_info['email']}</a></p>
    <p><strong>Contact Phone:</strong> <a href="tel:{task_owner_info['phone_number']}">{task_owner_info['phone_number']}</a></p>
    {task_details_html}
    <p><a href="https://dooley-8c253088e812.herokuapp.com/templates/accepted.html">View your accepted tasks</a></p>
    </body>
    </html>
    """

    # Send emails using the modified send_email function to handle HTML content
    send_result_owner = send_email(
        task_owner_info["email"], "Your Task Has Been Accepted", email_body_owner
    )
    send_result_acceptor = send_email(
        task_acceptor_info["email"], "You Accepted a Task", email_body_acceptor
    )

    return f"Notifications sent: {send_result_owner}, {send_result_acceptor}"


def format_task_details_html(task_details):
    """Format task details into HTML for email content."""
    html_content = "<h2>Task Details</h2>"
    html_content += f"<p><strong>Name:</strong> {task_details['task_name']}</p>"
    html_content += f"<p><strong>Category:</strong> {task_details['category']}</p>"
    html_content += (
        f"<p><strong>Date Posted:</strong> {task_details['date_posted']}</p>"
    )

    # Add additional information based on task category
    if task_details["category"] == "Food":
        food_info = task_details["additional_info"]["food"]
        html_content += "<h3>Food Task Details</h3>"
        html_content += (
            f"<p><strong>Start Location:</strong> {food_info['start_loc']}</p>"
        )
        html_content += f"<p><strong>End Location:</strong> {food_info['end_loc']}</p>"
        html_content += f"<p><strong>Price:</strong> ${food_info['price']}</p>"
        html_content += f"<p><strong>Restaurant:</strong> {food_info['restaurant']}</p>"
        html_content += (
            f"<p><strong>Description:</strong> {food_info['description']}</p>"
        )
    elif task_details["category"] == "Service":
        service_info = task_details["additional_info"]["service"]
        html_content += "<h3>Service Task Details</h3>"
        html_content += f"<p><strong>Location:</strong> {service_info['location']}</p>"
        html_content += (
            f"<p><strong>Description:</strong> {service_info['description']}</p>"
        )
        html_content += f"<p><strong>Price:</strong> ${service_info['price']}</p>"

    return html_content


def send_auth_email(recipient_email, auth_code):
    # Email subject
    subject = "Your DooleyAFavor Email Verification Code"

    # Enhanced styling for the email
    header_color = "#0056b3"  # Blue color for header
    body_color = "#f8f9fa"  # Light grey for the email body
    accent_color = "#ffc107"  # Yellow for accent
    font_family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"

    # HTML content of the email
    html_message = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: {font_family};
                background-color: {body_color};
                color: #333;
                line-height: 1.6;
            }}
            .header {{
                background-color: {header_color};
                color: #fff;
                padding: 10px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .code {{
                font-size: 24px;
                color: {accent_color};
            }}
            .footer {{
                background-color: {header_color};
                color: #fff;
                padding: 10px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Email Verification</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>Please use the following code to verify your email address:</p>
            <p class="code">{auth_code}</p>
            <p>If you did not request this code, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>Thank you for using DooleyAFavor!</p>
        </div>
    </body>
    </html>
    """

    # Send the email
    return send_email(recipient_email, subject, html_message)

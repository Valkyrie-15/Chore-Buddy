from celery import shared_task
import time
from backend.model import Customer, Professional, ServiceRequest, User, db, Payment
import datetime
import csv
import os
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

@shared_task(ignore_results=False, name="download_csv")
def download_csv():
    # Ensure the 'static' directory exists
    os.makedirs('static', exist_ok=True)
    
    # Query all payments
    payments = Payment.query.all()
    
    # Generate a unique CSV filename with timestamp
    csv_file_name = f"payment_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.csv"
    full_path = os.path.join('static', csv_file_name)
    
    try:
        with open(full_path, 'w', newline='') as csvfile:
            sr_no = 1
            pay_csv = csv.writer(csvfile, delimiter=',')
            
            # Write header row
            pay_csv.writerow(['Sr No.', 'Payment ID', 'Service Request ID', 'Amount', 'Payment Date', 'Payment Status', 'Payment Method'])
            
            # Write payment data
            for payment in payments:
                pay_csv.writerow([
                    sr_no, 
                    payment.id, 
                    payment.service_request_id, 
                    payment.amount, 
                    payment.payment_date, 
                    payment.payment_status, 
                    payment.payment_method
                ])
                sr_no += 1
        
        return csv_file_name
    
    except Exception as e:
        # Log the error or handle it appropriately
        print(f"Error creating CSV: {e}")
        raise

def generate_user_transactions_csv(user):
    """
    Generate a CSV for a user's transactions
    """
    # Create an in-memory text stream for CSV
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    
    # Write CSV headers
    csv_writer.writerow([
        'Transaction ID', 
        'Amount', 
        'Date', 
        'Payment Status', 
        'Payment Method'
    ])
    
    # Write user's transactions
    for payment in user.pay:
        csv_writer.writerow([
            payment.id,
            payment.amount,
            payment.payment_date,
            payment.payment_status,
            payment.payment_method
        ])
    
    # Reset buffer position
    csv_buffer.seek(0)
    return csv_buffer

import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import shared_task
#from models import Customer, ServiceRequest, Payment, User

@shared_task(ignore_results=False, name="monthly_report")
def monthly_report():
    now = datetime.datetime.now()
    first_day_of_current_month = now.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

    customers = Customer.query.all()

    for customer in customers:
        # Get user's email from associated User model
        user = User.query.get(customer.user_id)
        if not user or not user.email:
            continue  # Skip if no email is found

        # HTML Email Template
        report_content = f"""
        <html>
        <body>
            <h2>Hello {customer.fullname},</h2>
            <p>Here is your monthly service report for <b>{first_day_of_previous_month.date()} to {last_day_of_previous_month.date()}</b>.</p>
            <table border="1" cellspacing="0" cellpadding="8" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <th>Service Request ID</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Payments</th>
                </tr>
        """

        service_requests = ServiceRequest.query.filter(
            ServiceRequest.customer_id == customer.id
        ).all()

        if not service_requests:
            report_content += """
                <tr>
                    <td colspan="4" style="text-align: center;">No service requests found for this period.</td>
                </tr>
            """
        else:
            for req in service_requests:
                # Fetch payments
                payments = Payment.query.filter(Payment.service_request_id == req.id).all()
                payment_details = "<br>".join(
                    [f"Amount: ${p.amount}, Date: {p.payment_date.date()}, Status: {p.payment_status}" for p in payments]
                ) if payments else "No payments"

                report_content += f"""
                <tr>
                    <td>{req.id}</td>
                    <td>{req.request_date.date()}</td>
                    <td>{req.status}</td>
                    <td>{payment_details}</td>
                </tr>
                """

        report_content += """
            </table>
            <p>Thank you for using our services!</p>
        </body>
        </html>
        """

        # Send email via MailHog SMTP
        sender_email = "noreply@example.com"
        recipient_email = user.email
        subject = "Your Monthly Service Report"

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(report_content, "html"))  # Send as HTML email

        try:
            with smtplib.SMTP("localhost", 1025) as server:  # MailHog SMTP
                server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Email sent to {recipient_email}")
        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {str(e)}")

    return "Monthly report emails sent successfully!"




@shared_task(ignore_results=False, name="daily_professional_reminder")
def daily_professional_reminder():
    now = datetime.datetime.now()
    today = now.date()

    professionals = Professional.query.all()

    for professional in professionals:
        # Get professional's email
        user = User.query.get(professional.user_id)
        if not user or not user.email:
            continue  # Skip if no email is found

        # Fetch pending service requests
        pending_requests = ServiceRequest.query.filter(
            ServiceRequest.professional_id == professional.id,
            ServiceRequest.status.in_(["open", "pending"])  # Adjust status names if needed
        ).all()

        if not pending_requests:
            continue  # Skip if no pending requests

        # Format email content
        report_content = f"""
        <html>
        <body>
            <h2>Hello {professional.fullname},</h2>
            <p>You have pending service requests that require your attention. Please review and take action:</p>
            <table border="1" cellspacing="0" cellpadding="8" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <th>Request ID</th>
                    <th>Customer</th>
                    <th>Requested Service</th>
                    <th>Date</th>
                    <th>Status</th>
                </tr>
        """

        for req in pending_requests:
            report_content += f"""
                <tr>
                    <td>{req.id}</td>
                    <td>{req.customer.fullname}</td>
                    <td>{req.service.service_name}</td>
                    <td>{req.request_date.date()}</td>
                    <td>{req.status}</td>
                </tr>
            """

        report_content += """
            </table>
            <p>Please log in to your dashboard to update the status of these requests.</p>
        </body>
        </html>
        """

        # Send email via MailHog SMTP
        sender_email = "noreply@example.com"
        recipient_email = user.email
        subject = "Reminder: Pending Service Requests"

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(report_content, "html"))  # Send as HTML email

        try:
            with smtplib.SMTP("localhost", 1025) as server:  # MailHog SMTP
                server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Reminder email sent to {recipient_email}")
        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {str(e)}")

    return "Daily reminder emails sent successfully!"
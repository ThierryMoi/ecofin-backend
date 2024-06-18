import random
import smtplib
import threading
from configuration.share import SMTP_USERNAME,SMTP_PASSWORD,SMTP_SERVER,SMTP_PORT
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from template.auth_email import generate_html


class EmailService:
    
    def __init__(self):
        self.sender_email = SMTP_USERNAME
        self.sender_password = SMTP_PASSWORD
        
    def send_email(self, recipient_email, subject, html_content):
            # Création du message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg_html = MIMEText(html_content, 'html')
        msg.attach(msg_html)
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(self.sender_email, self.sender_password)

                server.sendmail(self.sender_email, recipient_email, msg.as_string())

        except Exception as e:
            print(f"Une erreur s'est produite lors de l'envoi de l'e-mail : {str(e)}")

class CodeController:
    
    def __init__(self, email_service):
        self.email_service = email_service

    def send_code(self, recipient_email,nom,prenom,code_validation,lien):
        sujet = "Code de validation"
        #message = f"Votre code de validation est : {code}"
        html = generate_html(nom, prenom, code_validation,lien)

        self.email_service.send_email(recipient_email, sujet, html)



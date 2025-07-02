
import os
import json
import imaplib
import smtplib
import email
from email.message import EmailMessage
from email.header import decode_header
from datetime import datetime
from core.digiman_core import log_action, update_task_queue
from core.memory_store import load_memory
from core.metrics import increment_metric
from gpt.gpt_router import interpret_command
from dotenv import load_dotenv

load_dotenv()

class EmailAgent:
    def __init__(self, client_id=None):
        self.client_id = client_id
        self.memory = load_memory(client_id)
        self.imap_server = os.getenv("IMAP_SERVER")
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.email_account = os.getenv("EMAIL_ACCOUNT")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.imap_port = int(os.getenv("IMAP_PORT", 993))
        self.smtp_port = int(os.getenv("SMTP_PORT", 465))

    def run_task(self, task):
        log_action("Email Agent", f"Running task: {task['task']}", self.client_id)
        self.process_inbox()

    def process_inbox(self):
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_account, self.email_password)
            mail.select("inbox")
            _, messages = mail.search(None, 'UNSEEN')

            for num in messages[0].split():
                _, data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])

                subject = decode_header(msg["Subject"])[0][0]
                subject = subject.decode() if isinstance(subject, bytes) else subject
                sender = msg.get("From", "")
                body = ""

                for part in msg.walk():
                    if part.get_content_type() == "text/plain" and part.get_payload(decode=True):
                        body += part.get_payload(decode=True).decode(errors="ignore")

                attachments = []
                for part in msg.walk():
                    if part.get_content_disposition() == "attachment":
                        attachments.append(part.get_filename())

                full_context = "\\n".join([m["content"] for m in self.memory[-5:] if "content" in m])
                prompt = f"You are DigiMan, an AI email agent. User memory:\\n{full_context}\\n\\nEmail received:\\nSubject: {subject}\\nFrom: {sender}\\nBody: {body}\\n\\nClassify the sender (lead, support, spam, client), assign priority (1-3), summarize content, and suggest a reply."

                response = interpret_command(prompt, self.client_id)

                reply_text = response.get("task", "Thanks for contacting DigiMan.")
                category = response.get("intent", "unknown")
                priority = response.get("priority", 2)
                summary = response.get("summary", "General inquiry")

                lead_score = 1
                if "demo" in body.lower() or "pricing" in body.lower():
                    lead_score += 2
                if "urgent" in subject.lower():
                    lead_score += 1

                if category == "lead":
                    update_task_queue("CRM Agent", {
                        "task": f"Add lead: {sender}",
                        "email": sender,
                        "note": summary,
                        "score": lead_score,
                        "priority": priority
                    }, self.client_id)

                elif category == "support":
                    update_task_queue("Support Agent", {
                        "task": f"Support needed: {summary}",
                        "email": sender,
                        "attachments": attachments,
                        "priority": priority
                    }, self.client_id)

                    support_tickets = sum(1 for m in self.memory if "support" in m.get("content", "").lower())
                    if support_tickets > 3:
                        update_task_queue("Manager Agent", {
                            "task": "High support volume detected — investigate workflow bottlenecks.",
                            "priority": 3
                        }, self.client_id)

                if category != "spam":
                    self.send_reply(sender, subject, reply_text)

                log_action("Email Agent", f"Handled {category} from {sender} | Priority: {priority}", self.client_id)
                increment_metric("tasks_processed")

            mail.logout()

        except Exception as e:
            log_action("Email Agent", f"Processing error: {e}", self.client_id)

    def send_reply(self, to_email, subject, reply):
        try:
            smtp = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            smtp.login(self.email_account, self.email_password)
            msg = EmailMessage()
            msg["Subject"] = f"Re: {subject}"
            msg["From"] = self.email_account
            msg["To"] = to_email
            msg.set_content(reply)
            smtp.send_message(msg)
            smtp.quit()
        except Exception as e:
            log_action("Email Agent", f"Failed to reply to {to_email}: {e}", self.client_id)

import imaplib
import email
from email.header import decode_header
import getpass
from datetime import datetime

class EmailCleaner:
    def __init__(self, username, password, imap_server="imap.gmail.com"):
        """Initialize the email cleaner with credentials."""
        self.username = username
        self.password = password
        self.imap_server = imap_server
        self.imap = None
        
    def connect(self):
        """Connect to the IMAP server and login."""
        try:
            print(f"Connecting to {self.imap_server}...")
            self.imap = imaplib.IMAP4_SSL(self.imap_server)
            self.imap.login(self.username, self.password)
            print("✓ Successfully connected and logged in!")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def select_mailbox(self, mailbox="INBOX"):
        """Select the mailbox to work with."""
        try:
            status, messages = self.imap.select(mailbox)
            print(f"✓ Selected mailbox: {mailbox}")
            return True
        except Exception as e:
            print(f"✗ Failed to select mailbox: {e}")
            return False
    
    def search_emails(self, criteria):
        """Search for emails based on criteria."""
        try:
            status, messages = self.imap.search(None, criteria)
            if status == "OK":
                messages = messages[0].split(b' ')
                # Filter out empty strings
                messages = [m for m in messages if m]
                print(f"✓ Found {len(messages)} email(s) matching criteria")
                return messages
            return []
        except Exception as e:
            print(f"✗ Search failed: {e}")
            return []
    
    def preview_emails(self, email_ids, max_preview=10):
        """Preview the emails that will be deleted."""
        print(f"\n--- Preview (showing up to {max_preview} emails) ---")
        preview_count = min(len(email_ids), max_preview)
        
        for i, mail_id in enumerate(email_ids[:preview_count]):
            try:
                _, msg = self.imap.fetch(mail_id, "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        msg_obj = email.message_from_bytes(response[1])
                        
                        # Get subject
                        subject = decode_header(msg_obj["Subject"])[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode()
                        
                        # Get sender
                        sender = msg_obj.get("From", "Unknown")
                        
                        # Get date
                        date = msg_obj.get("Date", "Unknown")
                        
                        print(f"{i+1}. From: {sender}")
                        print(f"   Subject: {subject}")
                        print(f"   Date: {date}\n")
            except Exception as e:
                print(f"   Error previewing email {i+1}: {e}")
        
        if len(email_ids) > max_preview:
            print(f"... and {len(email_ids) - max_preview} more emails")
    
    def delete_emails(self, email_ids, preview=True):
        """Delete the specified emails."""
        if not email_ids:
            print("No emails to delete!")
            return 0
        
        # Preview emails before deletion
        if preview:
            self.preview_emails(email_ids)
            confirm = input(f"\nDo you want to delete these {len(email_ids)} email(s)? (yes/no): ")
            if confirm.lower() not in ['yes', 'y']:
                print("Deletion cancelled.")
                return 0
        
        deleted_count = 0
        print("\nDeleting emails...")
        
        for mail_id in email_ids:
            try:
                # Mark the mail as deleted
                self.imap.store(mail_id, "+FLAGS", "\\Deleted")
                deleted_count += 1
            except Exception as e:
                print(f"✗ Error deleting email: {e}")
        
        # Permanently remove emails marked as deleted
        self.imap.expunge()
        print(f"✓ Successfully deleted {deleted_count} email(s)!")
        return deleted_count
    
    def cleanup(self):
        """Close connection and logout."""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
                print("✓ Disconnected successfully")
            except:
                pass


def main():
    print("=" * 60)
    print("EMAIL CLEANER")
    print("=" * 60)
    
    # Get credentials
    username = input("Enter your email address: ")
    password = getpass.getpass("Enter your password: ")
    
    # Optional: specify IMAP server (default is Gmail)
    use_custom_server = input("Using Gmail? (yes/no, default=yes): ").lower()
    imap_server = "imap.gmail.com"
    
    if use_custom_server in ['no', 'n']:
        imap_server = input("Enter IMAP server (e.g., imap.outlook.com): ")
    
    # Create cleaner instance
    cleaner = EmailCleaner(username, password, imap_server)
    
    # Connect
    if not cleaner.connect():
        print("\nNote: If using Gmail, make sure to:")
        print("1. Use an App Password instead of your regular password")
        print("2. Enable 2-factor authentication")
        return
    
    # Select mailbox
    mailbox = input("\nEnter mailbox name (default=INBOX): ") or "INBOX"
    if not cleaner.select_mailbox(mailbox):
        return
    
    # Choose search criteria
    print("\n--- Search Options ---")
    print("1. Delete by sender")
    print("2. Delete by subject")
    print("3. Delete by date (before)")
    print("4. Delete by date (after)")
    print("5. Delete all emails (DANGEROUS!)")
    print("6. Custom search criteria")
    
    choice = input("\nEnter your choice (1-6): ")
    
    criteria = None
    if choice == "1":
        sender = input("Enter sender email: ")
        criteria = f'FROM "{sender}"'
    elif choice == "2":
        subject = input("Enter subject: ")
        criteria = f'SUBJECT "{subject}"'
    elif choice == "3":
        date = input("Enter date (DD-MMM-YYYY, e.g., 01-JAN-2020): ")
        criteria = f'BEFORE "{date}"'
    elif choice == "4":
        date = input("Enter date (DD-MMM-YYYY, e.g., 01-JAN-2020): ")
        criteria = f'SINCE "{date}"'
    elif choice == "5":
        confirm = input("Are you SURE you want to delete ALL emails? (type 'DELETE ALL'): ")
        if confirm == "DELETE ALL":
            criteria = "ALL"
        else:
            print("Cancelled.")
            cleaner.cleanup()
            return
    elif choice == "6":
        criteria = input("Enter custom IMAP search criteria: ")
    else:
        print("Invalid choice!")
        cleaner.cleanup()
        return
    
    # Search for emails
    email_ids = cleaner.search_emails(criteria)
    
    if email_ids:
        # Delete emails with preview
        cleaner.delete_emails(email_ids, preview=True)
    
    # Cleanup
    cleaner.cleanup()
    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()

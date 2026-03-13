import os
import time
import re
from datetime import datetime
from playwright.sync_api import sync_playwright, Playwright, BrowserContext

from base_watcher import Watcher

class WhatsAppWatcher(Watcher):
    def __init__(self, output_dir="../../Needs_Action", session_path='./whatsapp_session', interval=30, headless=False):
        super().__init__(interval)
        self.output_dir = output_dir
        self.session_path = session_path
        self.headless = headless
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help']
        self.playwright = None
        self.browser_context = None
        self.page = None
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(session_path, exist_ok=True)

    def _initialize_browser(self):
        print("Initializing Playwright browser...")
        self.playwright = sync_playwright().start()
        self.browser_context = self.playwright.chromium.launch_persistent_context(
            self.session_path,
            headless=self.headless,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            viewport={'width': 1366, 'height': 768},
            ignore_https_errors=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-infobars',
                '--window-size=1366,768'
            ]
        )
        self.page = self.browser_context.new_page()

        print("Navigating to WhatsApp Web...")
        self.page.goto("https://web.whatsapp.com/", timeout=300000, wait_until="domcontentloaded")  # 5 min

        print("Page loaded. Debug:")
        print("URL:", self.page.url)
        print("Title:", self.page.title())

        # Screenshot 1
        self.page.screenshot(path="debug_1_load.png")
        print("Screenshot 1: debug_1_load.png saved – open karo!")

        # Force click "Link a Device" or "Scan QR" button if present
        try:
            print("Looking for 'Link a Device' or QR trigger button...")
            link_button = self.page.locator(
                'button:has-text("Link a device"), [aria-label*="Link a device"], div[role="button"][aria-label*="scan"], button:has-text("Link with phone number")'
            )
            if link_button.count() > 0:
                print("Found link button – clicking to trigger QR...")
                link_button.first.click()
                time.sleep(8)  # Wait for QR animation
            else:
                print("No button found – QR should be visible.")
        except Exception as e:
            print("Button click failed:", str(e))

        # Screenshot 2 after click
        self.page.screenshot(path="debug_2_after_click.png")
        print("Screenshot 2: debug_2_after_click.png saved – open karo! QR dikhta hai?")

        # Wait for QR canvas or chat list
        try:
            self.page.wait_for_selector('canvas', timeout=90000)  # QR canvas
            print("QR canvas detected!")
        except:
            try:
                self.page.wait_for_selector('[data-testid="chat-list"]', timeout=45000)
                print("Already logged in – chats visible!")
            except:
                print("Neither QR nor chats detected. Check screenshots.")

        print("\n*** ABHI SCREENSHOTS KHOLO (debug_1_load.png aur debug_2_after_click.png) ***")
        print("Agar QR code dikhta hai (browser ya screenshot mein):")
        print("1. Phone se WhatsApp kholo → Settings → Linked Devices → Link a Device")
        print("2. QR scan karo")
        print("QR scan karne ke baad chats load hone do")
        print("Phir terminal mein Enter press karo...")
        input()

        print("Login complete. Starting monitoring.")
    def _close_browser(self):
        if self.browser_context:
            self.browser_context.close()
        if self.playwright:
            self.playwright.stop()
        print("Playwright browser closed.")

    def check_for_new_items(self):
        if not self.page or self.page.is_closed():
            self._initialize_browser()

        try:
            print("Checking for unread WhatsApp messages...")
            # Selector for unread chat indicators
            unread_chats = self.page.locator('span[aria-label*="unread"], span[data-testid*="unread"], div[aria-label*="unread message"], span[data-icon="unread"]')
            count = unread_chats.count()

            if count == 0:
                print("No new unread messages found.")
                return

            print(f"Found {count} unread chats. Processing...")
            for i in range(count):
                # Re-locate unread chats as the list might change after interaction
                chat_item = self.page.locator('div[role="listitem"] [data-testid="icon-unread-count"]').first.locator('..').locator('..').locator('..') # Navigate up to the parent chat item
                chat_item.click()
                self.page.wait_for_selector('div[data-testid="conversation-panel-header"]') # Wait for chat to open

                sender_name = self.page.locator('span[data-testid="conversation-info-header-chat-title"]').text_content()

                # Get the last few messages in the chat
                messages = self.page.locator('div.message-in, div.message-out').all_text_contents()
                last_message = messages[-1] if messages else ""

                if self._process_message(sender_name, last_message):
                    print(f"Processed chat from {sender_name}.")
                else:
                    print(f"No keywords found in the last message from {sender_name}.")

                # Mark as read by going back to chat list (this usually marks as read)
                self.page.go_back()
                self.page.wait_for_selector('div[data-testid="chat-list"]')

        except Exception as e:
            print(f"Error checking WhatsApp messages: {e}")
            # In case of error, try to close and re-initialize browser on next run
            self._close_browser()
            self.page = None

    def _process_message(self, sender, message_content):
        found_keywords = []
        for keyword in self.keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', message_content, re.IGNORECASE):
                found_keywords.append(keyword)

        if not found_keywords:
            return False

        filename_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_sender = "".join(c for c in sender if c.isalnum() or c in (' ', '_')).replace(' ', '_')
        output_filepath = os.path.join(self.output_dir, f"whatsapp_{filename_timestamp}_{filename_sender}.md")

        priority = "medium"
        if any(k in ['urgent', 'asap', 'invoice', 'payment'] for k in found_keywords):
            priority = "high"

        suggested_actions = ""
        if 'invoice' in found_keywords or 'payment' in found_keywords:
            suggested_actions += "- [ ] Check amount, flag for approval if >$500\n"
            suggested_actions += "- [ ] Draft polite reply confirming receipt\n"
        if 'urgent' in found_keywords or 'asap' in found_keywords or 'help' in found_keywords:
            suggested_actions += "- [ ] Prioritize this task\n"
            suggested_actions += "- [ ] Assess the nature of assistance required\n"

        content = f"---\n"
        content += f"type: whatsapp\n"
        content += f"from: {sender}\n"
        content += f"received: {datetime.now().isoformat()}\n"
        content += f"priority: {priority}\n"
        content += f"status: pending\n"
        content += f"keywords: {found_keywords}\n"
        content += f"---\n\n"
        content += f"# WhatsApp Message from {sender}\n\n"
        content += f"## Message Text:\n"
        content += f"> {message_content}\n\n"
        if suggested_actions:
            content += f"## Suggested Actions:\n"
            content += suggested_actions

        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created task file {output_filepath} for message from {sender}.")
        return True

if __name__ == "__main__":
    # Privacy Note: All session data (whatsapp_session folder) is stored locally and not sent externally.
    # For first run, set headless=False to allow QR scan. After successful login, you can set headless=True.
    # Example for first run with QR scan:
    # python AI_Employee_Vault/Watchers/whatsapp_watcher.py --headless=False
    # For background runs:
    # python AI_Employee_Vault/Watchers/whatsapp_watcher.py &

    import argparse
    parser = argparse.ArgumentParser(description="WhatsApp Watcher for unread messages.")
    parser.add_argument('--headless', type=str, default='True', help="Run browser in headless mode (True/False). Set to False for first run to scan QR code.")
    args = parser.parse_args()

    is_headless = args.headless.lower() == 'true'

    watcher = WhatsAppWatcher(output_dir="../../AI_Employee_Vault/Needs_Action", headless=is_headless)
    try:
        watcher.run()
    finally:
        watcher._close_browser()
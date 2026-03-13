import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, Playwright, BrowserContext

from base_watcher import Watcher

class LinkedInWatcher(Watcher):
    def __init__(self, output_dir="../../Needs_Action", session_path='./linkedin_session', interval=300, headless=True):
        super().__init__(interval)
        self.output_dir = output_dir
        self.session_path = session_path
        self.headless = headless
        self.processed_posts = set() # To keep track of posts processed in current run to avoid duplicates
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(session_path, exist_ok=True)

        self.playwright = None
        self.browser_context = None
        self.page = None

    def _initialize_browser(self):
        print("Initializing Playwright browser for LinkedIn...")
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
        print("Navigating to LinkedIn...")
        self.page.goto("https://www.linkedin.com/feed/", timeout=60000) # 1 minute timeout

        # Check if login is required
        if "login" in self.page.url or self.page.locator('#session_key').count() > 0:
            print("LinkedIn login required. Please log in manually in the browser window.")
            print("After successful login, close the browser window if running in headless=False mode.")
            self.page.wait_for_url("https://www.linkedin.com/feed/", timeout=300000) # Wait up to 5 minutes for login
            print("Logged into LinkedIn successfully.")
        else:
            print("Already logged into LinkedIn.")

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
            print("Checking for new LinkedIn posts...")
            self.page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
            self.page.wait_for_selector('div.feed-shared-update-v2', timeout=10000) # Wait for feed posts to load

            # Scroll down to load more posts (optional, but good for more content)
            self.page.mouse.wheel(0, 5000) # Scroll down 5000 pixels
            self.page.wait_for_timeout(2000) # Wait for content to load after scroll

            posts = self.page.locator('div.feed-shared-update-v2').all()
            new_posts_count = 0
            for post in posts:
                try:
                    post_id = post.get_attribute('data-urn')
                    if post_id in self.processed_posts:
                        continue # Skip already processed posts in this run

                    author_element = post.locator('span.update-components-actor__name').first
                    author = author_element.text_content().strip() if author_element else "Unknown Author"

                    content_element = post.locator('div.feed-shared-update-v2__description-wrapper').first.locator('span[dir="ltr"]').first
                    content_text = content_element.text_content().strip() if content_element else "No content found."

                    # Placeholder for more sophisticated filtering if needed, e.g., keywords for "business ideas"
                    # For now, we'll process all visible posts as potential items for review

                    filename_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename_author = "".join(c for c in author if c.isalnum() or c in (' ', '_')).replace(' ', '_')
                    output_filepath = os.path.join(self.output_dir, f"linkedin_post_{filename_timestamp}_{filename_author}.md")

                    md_content = f"---\n"
                    md_content += f"type: linkedin_post\n"
                    md_content += f"from: {author}\n"
                    md_content += f"received: {datetime.now().isoformat()}\n"
                    md_content += f"priority: medium\n"
                    md_content += f"status: pending\n"
                    md_content += f"---\n\n"
                    md_content += f"# LinkedIn Post from {author}\n\n"
                    md_content += f"## Content:\n"
                    md_content += f">>>\n{content_text}\n<<<\n\n"
                    md_content += f"## Suggested Actions:\n"
                    md_content += f"- [ ] Review post content for business ideas or scheduled posts\n"
                    md_content += f"- [ ] Determine if further action is required (e.g., drafting a response, scheduling a related post)\n"

                    with open(output_filepath, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    print(f"Created task file {output_filepath} for LinkedIn post from {author}.")
                    self.processed_posts.add(post_id)
                    new_posts_count += 1
                except Exception as post_e:
                    print(f"Error processing a LinkedIn post: {post_e}")

            if new_posts_count == 0:
                print("No new LinkedIn posts found to process.")
            else:
                print(f"Processed {new_posts_count} new LinkedIn posts.")

        except Exception as e:
            print(f"Error checking LinkedIn posts: {e}")
            self._close_browser()
            self.page = None

if __name__ == "__main__":
    # Privacy Note: All session data (linkedin_session folder) is stored locally and not sent externally.
    # For first run, set headless=False to allow manual login. After successful login, you can set headless=True.

    import argparse
    parser = argparse.ArgumentParser(description="LinkedIn Watcher for new posts.")
    parser.add_argument('--headless', type=str, default='True', help="Run browser in headless mode (True/False). Set to False for first run to login manually.")
    args = parser.parse_args()

    is_headless = args.headless.lower() == 'true'

    watcher = LinkedInWatcher(output_dir="../../AI_Employee_Vault/Needs_Action", headless=is_headless)
    try:
        watcher.run()
    finally:
        watcher._close_browser()

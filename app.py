import subprocess
import sys
from pathlib import Path
from typing import Optional, List
import questionary
from questionary import Style

# Custom style for the prompts
custom_style = Style([
    ('question', 'fg:#00ffff bold'),       # question text
    ('answer', 'fg:#00ff00 bold'),        # user answer
    ('pointer', 'fg:#ff00ff bold'),       # cursor pointer
    ('selected', 'fg:#ffff00 bold'),      # selected item
    ('separator', 'fg:#cc5454'),          # separator in lists
])

class InteractiveVideoDownloader:
    def __init__(self):
        self.check_ytdlp_installed()
        self.cookies_path = self.find_cookies_file()

    def check_ytdlp_installed(self):
        try:
            subprocess.run(["yt-dlp", "--version"], 
                          check=True, 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Error: yt-dlp not found. Please install it first.")
            print("Installation instructions: https://github.com/yt-dlp/yt-dlp#installation")
            sys.exit(1)

    def find_cookies_file(self) -> Optional[str]:
        """Search for common YouTube cookie files"""
        cookie_files = [
            "www.youtube.com_cookies.txt",
            "youtube.com_cookies.txt",
            "cookies.txt"
        ]
        for file in cookie_files:
            if Path(file).exists():
                return file
        return None

    def prompt_url(self) -> str:
        """Prompt user for video URL"""
        return questionary.text(
            "📹 Enter video URL(s), separate multiple URLs with spaces:",
            validate=lambda text: len(text.strip()) > 0,
            style=custom_style
        ).ask()

    def prompt_download_type(self):
        """Prompt user for download type"""
        return questionary.select(
            "🔽 What would you like to download?",
            choices=[
                {"name": "Video (best quality)", "value": "video"},
                {"name": "Audio only (MP3)", "value": "audio"},
                {"name": "Custom format selection", "value": "custom"},
                {"name": "List available formats first", "value": "list"}
            ],
            style=custom_style
        ).ask()

    def prompt_output_template(self):
        """Prompt user for output filename template"""
        return questionary.text(
            "💾 Output filename template (leave empty for default):",
            default="%(title)s.%(ext)s",
            style=custom_style
        ).ask()

    def prompt_extra_options(self):
        """Prompt for additional options"""
        return questionary.checkbox(
            "⚙️ Select additional options:",
            choices=[
                {"name": "Download subtitles", "value": "subtitles"},
                {"name": "Download entire playlist", "value": "playlist"},
                {"name": "Add metadata", "value": "metadata"},
                {"name": "Embed thumbnail", "value": "thumbnail"},
                {"name": "Remove sponsor segments (SponsorBlock)", "value": "sponsorblock"}
            ],
            style=custom_style
        ).ask()

    def prompt_subtitle_languages(self):
        """Prompt for subtitle languages"""
        return questionary.text(
            "🌍 Enter subtitle languages (comma separated, e.g., 'en,es'):",
            default="en",
            style=custom_style
        ).ask()

    def prompt_use_cookies(self):
        """Ask if user wants to use cookies"""
        if not self.cookies_path:
            return False
            
        return questionary.confirm(
            f"🔑 Found cookies file at '{self.cookies_path}'. Use it for authentication?",
            default=True,
            style=custom_style
        ).ask()

    def prompt_browser_cookies(self):
        """Prompt for browser to extract cookies from"""
        browsers = ["chrome", "firefox", "edge", "brave", "opera", "safari"]
        return questionary.select(
            "🌐 Select browser to extract cookies from:",
            choices=browsers,
            style=custom_style
        ).ask()

    def get_available_formats(self, url: str, use_cookies: bool = False):
        """List available formats for a video"""
        cmd = ["yt-dlp", "-F", url]
        if use_cookies and self.cookies_path:
            cmd.extend(["--cookies", self.cookies_path])
        
        print("\n📋 Available formats:")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error getting formats: {e}")

    def download(
        self,
        urls: List[str],
        download_type: str = "video",
        output_template: str = "%(title)s.%(ext)s",
        extra_options: List[str] = None,
        subtitle_langs: str = "en",
        use_cookies: bool = False,
        browser_cookies: Optional[str] = None
    ):
        """Download videos with interactive options"""
        cmd = ["yt-dlp"]
        
        # Authentication
        if use_cookies and self.cookies_path:
            cmd.extend(["--cookies", self.cookies_path])
        elif browser_cookies:
            cmd.extend(["--cookies-from-browser", browser_cookies])
        
        # Format selection
        if download_type == "video":
            cmd.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"])
        elif download_type == "audio":
            cmd.extend(["--extract-audio", "--audio-format", "mp3"])
        elif download_type == "custom":
            format_choice = questionary.text(
                "⌨️ Enter format code (e.g., 'bestvideo+bestaudio', '22+bestaudio'):",
                default="bestvideo+bestaudio",
                style=custom_style
            ).ask()
            cmd.extend(["-f", format_choice])
        
        # Output template
        if output_template:
            cmd.extend(["-o", output_template])
        
        # Extra options
        if extra_options:
            if "subtitles" in extra_options:
                cmd.extend(["--write-subs", "--sub-langs", subtitle_langs])
            if "playlist" not in extra_options:
                cmd.append("--no-playlist")
            if "metadata" in extra_options:
                cmd.append("--add-metadata")
            if "thumbnail" in extra_options:
                cmd.append("--embed-thumbnail")
            if "sponsorblock" in extra_options:
                cmd.append("--sponsorblock-remove")
        
        cmd.extend(urls)
        
        
        try:
            subprocess.run(cmd, check=True)
            print("\n✅ Download completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error downloading video: {e}")
            sys.exit(1)

    def run_interactive(self):
        """Run the interactive CLI"""
        print("\n" + "="*50)
        print("🎬 YouTube Video Downloader".center(50))
        print("Interactive CLI for downloading videos from YouTube".center(50))
        # credit
        print("by @VikumKarunathilake".center(50))
        #check website color magenta
        print("https://elixircraft.net/".center(50))
        print("="*50 + "\n")
        
        try:
            # Step 1: Get URLs
            urls = self.prompt_url().split()
            
            # Step 2: Choose download type
            download_type = self.prompt_download_type()
            if download_type == "list":
                self.get_available_formats(urls[0], self.prompt_use_cookies())
                download_type = self.prompt_download_type()
            
            # Step 3: Authentication
            use_cookies = self.prompt_use_cookies()
            browser_cookies = None
            if not use_cookies or not self.cookies_path:
                if questionary.confirm(
                    "🔐 Do you want to use browser cookies instead?",
                    default=False,
                    style=custom_style
                ).ask():
                    browser_cookies = self.prompt_browser_cookies()
            
            # Step 4: Output options
            output_template = self.prompt_output_template()
            
            # Step 5: Extra options
            extra_options = self.prompt_extra_options()
            subtitle_langs = "en"
            if "subtitles" in extra_options:
                subtitle_langs = self.prompt_subtitle_languages()
            
            # Confirm and download
            print("\n" + "="*50)
            if questionary.confirm(
                "🚀 Start download with these settings?",
                default=True,
                style=custom_style
            ).ask():
                self.download(
                    urls=urls,
                    download_type=download_type,
                    output_template=output_template,
                    extra_options=extra_options,
                    subtitle_langs=subtitle_langs,
                    use_cookies=use_cookies,
                    browser_cookies=browser_cookies
                )
            else:
                print("\n❌ Download canceled.")
                
        except KeyboardInterrupt:
            print("\n❌ Operation canceled by user.")
            sys.exit(0)

if __name__ == "__main__":
    # Check if questionary is installed
    try:
        import questionary
    except ImportError:
        print("Error: The 'questionary' package is required for this interactive CLI.")
        print("Please install it with: pip install questionary")
        sys.exit(1)
    
    downloader = InteractiveVideoDownloader()
    downloader.run_interactive()
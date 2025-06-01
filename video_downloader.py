import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional, List

class VideoDownloader:
    def __init__(self):
        self.check_ytdlp_installed()
    
    def check_ytdlp_installed(self):
        try:
            subprocess.run(["yt-dlp", "--version"], 
                         check=True, 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: yt-dlp not found. Please install it first.")
            print("Installation instructions: https://github.com/yt-dlp/yt-dlp#installation")
            sys.exit(1)
    
    def download(
        self,
        urls: List[str],
        format: Optional[str] = None,
        audio_only: bool = False,
        output_template: Optional[str] = None,
        subtitles: bool = False,
        subtitles_lang: str = "en",
        playlist: bool = False,
        metadata: bool = False,
        thumbnail: bool = False,
        sponsorblock: bool = False,
        cookies: Optional[str] = None,
        browser: Optional[str] = None
    ):
        """Download videos with various options"""
        cmd = ["yt-dlp"]
        
        # Cookie handling
        if cookies:
            if Path(cookies).exists():
                cmd.extend(["--cookies", cookies])
            else:
                print(f"Warning: Cookies file {cookies} not found. Proceeding without cookies.")
        elif browser:
            cmd.extend(["--cookies-from-browser", browser])
        
        # Format selection
        if format:
            cmd.extend(["-f", format])
        elif audio_only:
            cmd.extend(["--extract-audio", "--audio-format", "mp3"])
        
        # Output template
        if output_template:
            cmd.extend(["-o", output_template])
        
        # Subtitles
        if subtitles:
            cmd.extend(["--write-subs", "--sub-langs", subtitles_lang])
        
        # Playlist options
        if not playlist:
            cmd.append("--no-playlist")
        
        # Metadata
        if metadata:
            cmd.append("--add-metadata")
        if thumbnail:
            cmd.append("--embed-thumbnail")
        
        # SponsorBlock
        if sponsorblock:
            cmd.append("--sponsorblock-remove")
        
        cmd.extend(urls)
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading video: {e}")
            sys.exit(1)

    def get_available_formats(self, url: str, cookies: Optional[str] = None):
        """List available formats for a video"""
        cmd = ["yt-dlp", "-F", url]
        if cookies:
            cmd.extend(["--cookies", cookies])
    
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error getting formats: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Video Downloader CLI with Cookie Support",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        "urls",
        nargs="+",
        help="Video URL(s) to download"
    )
    
    # Download options
    parser.add_argument(
        "-f", "--format",
        help="Video format code or selector (e.g., 'bestvideo+bestaudio')"
    )
    parser.add_argument(
        "-a", "--audio-only",
        action="store_true",
        help="Download audio only (MP3)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output filename template (e.g., '%(title)s.%(ext)s')"
    )
    
    # Feature options
    parser.add_argument(
        "--subtitles",
        action="store_true",
        help="Download subtitles"
    )
    parser.add_argument(
        "--subtitles-lang",
        default="en",
        help="Subtitle languages (comma separated)"
    )
    parser.add_argument(
        "--playlist",
        action="store_true",
        help="Download entire playlist (if URL is a playlist)"
    )
    parser.add_argument(
        "--metadata",
        action="store_true",
        help="Add metadata to the file"
    )
    parser.add_argument(
        "--thumbnail",
        action="store_true",
        help="Embed thumbnail in audio files"
    )
    parser.add_argument(
        "--sponsorblock",
        action="store_true",
        help="Remove sponsor segments using SponsorBlock"
    )
    
    # Cookie options
    cookie_group = parser.add_argument_group("Authentication options")
    cookie_group.add_argument(
        "--cookies",
        help="Path to Netscape format cookies file (e.g., 'www.youtube.com_cookies.txt')"
    )
    cookie_group.add_argument(
        "--browser",
        help="Browser to extract cookies from (e.g., 'chrome', 'firefox')"
    )
    
    args = parser.parse_args()
    
    # Validate cookie options
    if args.cookies and args.browser:
        print("Error: Please specify either --cookies or --browser, not both")
        sys.exit(1)
    
    downloader = VideoDownloader()
    downloader.download(
        urls=args.urls,
        format=args.format,
        audio_only=args.audio_only,
        output_template=args.output,
        subtitles=args.subtitles,
        subtitles_lang=args.subtitles_lang,
        playlist=args.playlist,
        metadata=args.metadata,
        thumbnail=args.thumbnail,
        sponsorblock=args.sponsorblock,
        cookies=args.cookies,
        browser=args.browser
    )

if __name__ == "__main__":
    main()
# Meisengeige Bot - Project Context

## Project Goal
Monitor updates to multiple cinema programs (Meisengeige at Cinecitta and Kinderkino at Filmhaus Nürnberg) via GitHub Actions and send notifications to subscribers via Telegram bot.

## Current Status
- Multi-source cinema monitoring implemented ✓
- Independent per-source subscriptions ✓
- Interactive bot commands with inline keyboards ✓
- Development environment configured (Python 3.14.2 locally, 3.12 in CI) ✓
- GitHub repository connected (https://github.com/dorotynsky/meisengeige-bot) ✓
- GitHub Actions configured for multi-source monitoring ✓
- Backward compatibility with existing subscribers ✓
- **Status:** Fully automated multi-source monitoring! 🎉🎬

## Architecture
**Multi-Source Monitoring System**
- Base scraper abstraction with source registry pattern
- Two scrapers implemented:
  - **MeisengeigeScraper**: Parses Cinecitta Meisengeige program
  - **FilmhausScraper**: Parses Filmhaus Kinderkino program
- Per-source snapshot storage (separate JSON files)
- Per-source subscription management
- Independent subscriptions: users choose Meisengeige, Kinderkino, or both
- Source-specific notifications with poster images

## Page Structures

### Meisengeige (Cinecitta)
Each film on https://www.cinecitta.de/programm/meisengeige/ contains:
- **Title**: In `<h3 class="text-white">` tag
- **Genres**: Tags like "Arthouse", "Drama", "Komödie", "Thriller", "Dokumentation"
- **FSK Rating**: Age restriction (e.g., "FSK: 16")
- **Duration**: In minutes (e.g., "119min")
- **Description**: Brief plot summary in `<p>` tag
- **Poster**: Image URL in `<img>` tag
- **Showtimes**: Table with:
  - Dates (e.g., "Mo. 15.12", "Di. 16.12")
  - Cinema room (e.g., "Kino 2")
  - Language (e.g., "OV" = original version, "OmU" = with subtitles)
  - Times (e.g., "20:30")

### Kinderkino (Filmhaus)
Each event on https://www.kunstkulturquartier.de/filmhaus/programm/kinderkino contains:
- **Title**: In `<a class="detailLink">` tag
- **Date/Time**: Format "Mo / 22.12.2025 / 15:00 Uhr"
- **Venue**: "Filmhaus Nürnberg - kinoeins"
- **Category**: "Kinderkino"
- **Poster Image**: Scene stills from films
- **Description**: Brief plot summary
- **Schedule**: Typically Fridays-Sundays at 3 PM

## Technical Stack
- **Python**: 3.14.2
- **Package Manager**: Poetry
- **Version Manager**: mise
- **Dependencies**:
  - httpx - for HTTP requests
  - beautifulsoup4 & lxml - for HTML parsing
  - python-telegram-bot - for Telegram integration
  - pytest, black, ruff - for development and testing

## Bot Commands
- `/start [source_id]` - Subscribe to cinema source(s) with interactive menu
- `/stop [source_id]` - Unsubscribe from source(s) with interactive menu
- `/status` - View active subscriptions and subscriber counts
- `/sources` - List all available cinema sources with URLs

## Recent Changes
- Added multi-source cinema monitoring support
- Implemented FilmhausScraper for Kinderkino program
- Created base scraper abstraction and source registry
- Enhanced subscriber management for per-source subscriptions
- Updated bot commands with inline keyboards
- Maintained backward compatibility with existing subscribers

## Configuration Files
- `.mise.toml` - mise configuration (Python 3.14.2)
- `.python-version` - Python version file (3.14.2)
- `pyproject.toml` - Poetry configuration (Python ^3.14)

## Communication Guidelines
- Chat communication: Russian
- Code, commits, messages: English only
- Work step-by-step with user confirmation between steps
- **IMPORTANT**: Do NOT add Claude Code attribution or Co-Authored-By lines to commit messages

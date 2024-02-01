# Futebolscore Scraper

Script for scraping football statistics from Futebolscore

## Installation

`pip install -r requirements.txt`

## Running

`python main.py <start_id> <end_id> <file_path>`

- For help, run: `python main.py -h`

### Arguments:

1. `start_id` - lowest match ID to be scraped (read more in the IDs section)
2. `end_id` - highest match ID to be scraped (read more in the IDs section)
3. `-f` - file path where the output file will be saved (optional)
   - Make sure that all specified subdirectories in the file path exist.
4. `-t` - how many threads to use (optional)

### IDs:

IDs are 7-digit numbers where the first 2 digits represent in what year the match was played (with exceptions, early January and late December matches).

- Example: The match with ID 2321902 was played on 17-06-2023.

### _Note:_ The current implementation of the scraper supports only scraping finished matches. Attempting to scrape scheduled matches (for the future) will not result in an error, the scraper will just skip them, thanks to the error handling.

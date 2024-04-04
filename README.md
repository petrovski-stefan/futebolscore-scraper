# Futebolscore Scraper

Script for scraping football statistics from Futebolscore

## Installation

`pip install -r requirements.txt`

## Running

`python main.py <arguments>`

- For help, run: `python main.py -h`

### Arguments:

1. `-s` - lowest match ID to be scraped (read more in the IDs section)
2. `-e` - highest match ID to be scraped (read more in the IDs section)
3. `-f` - file path where the output file will be saved (default is `./data.csv`)
   - Make sure that all specified subdirectories in the file path exist
4. `-t` - how many threads to use
5. `-d` - scrape only today's matches without manually passing IDs (`flag`)

The arguments `-d` or both `-s` and `-e` are required.

### IDs:

IDs are 7-digit numbers where the first 2 digits represent in what year the match was played (with exceptions, early January and late December matches).

- Example: The match with ID 2321902 was played on 17-06-2023.

### Features

Here is a list of this project's features:

- web scraping daily or history matches
- using selenium web driver to interact with the page
- concurrency and synchronization using a lock
- saving scraped data to a csv file using pandas library
- command line argument parsing
- user agent rotation

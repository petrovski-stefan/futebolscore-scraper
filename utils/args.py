import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape football statistics")

    parser.add_argument("-s", type=int, help="Lowest match id to be scraped")
    parser.add_argument("-e", type=int, help="Highest match id to be scraped")
    parser.add_argument("-f", default="data.csv", help="Output file path")
    parser.add_argument("-t", type=int, default=4, help="How many threads to use")

    args = parser.parse_args()

    return args
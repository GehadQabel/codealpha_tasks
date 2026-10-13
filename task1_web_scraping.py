
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import time
import re

# CodeAlpha Internship - Task 1: Web Scraping
# Project: Books Data Collection

BASE_URL = "https://books.toscrape.com/"
books = []

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

print("=" * 50)
print("CODEALPHA - BOOKS WEB SCRAPING PROJECT")
print("=" * 50)

for page in range(1, 51):

    url = urljoin(
        BASE_URL,
        f"catalogue/page-{page}.html"
    )

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        # Fix website text encoding
        response.encoding = "utf-8"

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        items = soup.select("article.product_pod")

        if not items:
            print(f"No books found on page {page}")
            break

        for item in items:

            # Book title
            title = item.select_one("h3 a")["title"]

            # Book price
            price_text = item.select_one(
                ".price_color"
            ).get_text(strip=True)

            # Extract numeric price safely
            price_match = re.search(
                r"\d+(?:\.\d+)?",
                price_text
            )

            if not price_match:
                print(f"Invalid price for: {title}")
                continue

            price = float(price_match.group())

            # Availability
            availability = item.select_one(
                ".availability"
            ).get_text(" ", strip=True)

            # Rating
            rating_classes = item.select_one(
                "p.star-rating"
            ).get("class", [])

            rating = next(
                (
                    rating_map[name]
                    for name in rating_classes
                    if name in rating_map
                ),
                None
            )

            # Product link
            relative_link = item.select_one(
                "h3 a"
            )["href"]

            product_url = urljoin(
                url,
                relative_link
            )

            # Save book data
            books.append({
                "Title": title,
                "Price_GBP": price,
                "Rating": rating,
                "Availability": availability,
                "Product_URL": product_url
            })

        print(
            f"Page {page} completed | "
            f"Total books: {len(books)}"
        )

        # Respectful delay between requests
        time.sleep(0.5)

    except requests.RequestException as error:
        print(f"Error on page {page}: {error}")
        print("Stopping to avoid an incomplete dataset.")
        break

# Remove duplicate products
unique_books = {
    book["Product_URL"]: book
    for book in books
}

books = list(unique_books.values())

# Save dataset to CSV
file_name = "books_dataset.csv"

with open(
    file_name,
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    fieldnames = [
        "Title",
        "Price_GBP",
        "Rating",
        "Availability",
        "Product_URL"
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(books)

# Final report
print("\n" + "=" * 50)
print("WEB SCRAPING COMPLETED")
print("=" * 50)

print(f"Total unique books: {len(books)}")
print(f"Dataset saved as: {file_name}")

if books:
    prices = [book["Price_GBP"] for book in books]

    print(f"Minimum price: £{min(prices):.2f}")
    print(f"Maximum price: £{max(prices):.2f}")
    print(f"Average price: £{sum(prices)/len(prices):.2f}")

if len(books) != 1000:
    print(
        "WARNING: Expected 1000 books. "
        "Check whether all pages were collected."
    )

print("=" * 50)

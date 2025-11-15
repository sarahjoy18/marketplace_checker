import json
import os

# Define the file paths for all data sources
file_paths = ['Lazada - Products PH.json', 'Lazada - Products.json', 'Shopee - products.json']


def process_product_data(file_path):
    """
    Reads a JSON file containing product data, filters out items with initial_price of 0,
    and returns a list of product dictionaries or None if an error occurs.
    """

    # Check if the file exists before attempting to open it
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.")
        print("Please ensure the file is in the same directory as this script.")
        return None

    try:
        # Open the file and load the JSON data
        with open(file_path, 'r', encoding='utf-8') as read_file:
            data = json.load(read_file)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{file_path}'. Check if the file content is valid JSON.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while opening or reading the file: {e}")
        return None

    if not isinstance(data, list):
        data = [data]

    original_count = len(data)
    filtered_data = []

    for product in data:
        initial_price_value = product.get("initial_price")

        # Attempt to convert the price to a float for comparison
        try:
            if isinstance(initial_price_value, str):
                cleaned_price_str = ''.join(filter(lambda x: x.isdigit() or x == '.', initial_price_value))
                price = float(cleaned_price_str)
            else:
                price = float(initial_price_value)
        except (TypeError, ValueError):
            price = 0.0

        # Only include the product if the price is greater than 0
        if price > 0:
            filtered_data.append(product)

    data = filtered_data
    filtered_count = len(data)

    if original_count > 0 and filtered_count < original_count:
        print(f"--- Filtered: Excluded {original_count - filtered_count} products with initial_price <= 0. ---")

    # Print a summary of the loaded data
    print(f"--- Successfully loaded {filtered_count} products from '{file_path}' ---")

    return data


def search_product(search_item, all_products):
    """
    Searches for a product across the loaded data and prints a comparison table
    of matching results.
    """

    def safe_float(value, default_value=0.0):
        try:
            if isinstance(value, str):
                # Simple filter to keep digits and a single decimal point
                cleaned_str = ''.join(filter(lambda x: x.isdigit() or x == '.', value))
                return float(cleaned_str)
            return float(value)
        except (TypeError, ValueError):
            return default_value

    search_term = search_item.lower()

    found_products = []

    for product in all_products:
        title = str(product.get("title", "")).lower()
        if search_term in title:
            found_products.append(product)

    if not found_products:
        print(f"\nNo products found matching '{search_item}'. Please try a different query.")
        return

    found_products.sort(key=lambda p: (
        -safe_float(p.get("rating"), default_value=0.0),  # Primary Sort: Highest Rating first
        safe_float(p.get("final_price"), default_value=float('inf'))  # Secondary Sort: Lowest Price first
    ))

    # --- Product Recommendation ---
    best_deal = found_products[0]
    best_title = best_deal.get("title", "Unknown Product")
    best_price = str(best_deal.get("final_price", "N/A"))
    best_rating = str(best_deal.get("rating", "N/A"))
    best_seller = str(best_deal.get("seller_name", "N/A (Seller Missing)"))
    best_url = str(best_deal.get("url", "N/A (URL Missing)"))

    print("\n" + "#"*90)
    print(f"🌟 TOP PRODUCT RECOMMENDATION 🌟")
    print(f"Based on highest rating and lowest final price for '{search_item}':")
    print(f"   🏆 Recommended Product: {best_title}")
    print(f"   ⭐ Rating: {best_rating}")
    print(f"   💲 Final Price: {best_price}")
    print(f"      Seller: {best_seller}")
    print(f"      URL: {best_url}")
    print("#"*90)

    # --- Display Comparison Table ---

    print("\n" + "=" * 90)
    print(f"🔍 Price Comparison Results for: '{search_item}' ({len(found_products)} items found)")
    print("=" * 90)

    # Table Header
    print(f"{'Title':<50} | {'Initial Price':<15} | {'Final Price':<15} | {'Rating':<6} | Seller Name | URL")
    print("-" * 120)

    # Basic display logic:
    for product in found_products:
        # Use .get() to safely retrieve values and ensure they are strings for printing
        title = product.get("title", "N/A (Title Missing)")
        initial_price = str(product.get("initial_price", "N/A"))
        final_price = str(product.get("final_price", "N/A"))
        rating = str(product.get("rating", "N/A"))
        seller_name = product.get("seller_name", "N/A (Seller Missing)")
        url = product.get("url", "N/A (URL Missing)")

        # Truncate the title for clean table output
        display_title = (title[:47] + '...') if len(title) > 50 else title

        # Print the formatted output
        print(f"{display_title:<50} | {initial_price:<15} | {final_price:<15} | {rating:<6} | {seller_name}| {url}")

    print("\nTip: Look for the lowest 'Final Price' to find the best deal!")


if __name__ == "__main__":
    # Correct Initialization: Must define 'all_products' before using it
    all_products = []

    # 1. Load Data from all files
    for file_path in file_paths:
        data = process_product_data(file_path)

        # Check if data was successfully loaded
        if data:
            all_products.extend(data)

    if not all_products:
        print("\n--- FATAL: No products were loaded from any of the files. Search cancelled. ---")
    else:
        print(f"\nSuccessfully aggregated a total of {len(all_products)} products across all files.")

        # 2. Get Search Item and Perform Search
        search_item = input("\nEnter the product name to compare prices across all platforms: ")

        if search_item:
            search_product(search_item, all_products)
        else:
            print("\nSearch cancelled. Please run the script again to search for a product.")
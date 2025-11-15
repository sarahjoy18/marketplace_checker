import json
import os
from flask import Flask, render_template_string, request, url_for, redirect

# --- Configuration and Data Loading Setup ---

# Define the file paths for all data sources (REQUIRED: These files must exist next to this script)
FILE_PATHS = ['Lazada - Products PH.json', 'Lazada - Products.json', 'Shopee - products.json']

# Initialize Flask App
app = Flask(__name__)

# Constants for Pagination
PAGE_SIZE = 5

# Global variable to hold all loaded and filtered product data
ALL_PRODUCTS = []


# Helper function to safely convert string price/rating to float for sorting
def safe_float(value, default_value=0.0):
    """Safely converts price or rating string to float for comparison."""
    try:
        if isinstance(value, str):
            # Simple filter to keep digits and a single decimal point
            cleaned_str = ''.join(filter(lambda x: x.isdigit() or x == '.', value))
            if not cleaned_str:
                return default_value
            return float(cleaned_str)
        return float(value)
    except (TypeError, ValueError):
        return default_value


def process_product_data(file_path):
    """
    Reads a JSON file, filters out items with initial_price of 0,
    and returns a list of product dictionaries or None if an error occurs.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as read_file:
            data = json.load(read_file)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{file_path}'.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

    if not isinstance(data, list):
        data = [data]

    filtered_data = []

    # --- FILTERING LOGIC: Exclude products where initial_price is 0 ---
    for product in data:
        initial_price_value = product.get("initial_price")
        price = safe_float(initial_price_value, default_value=0.0)

        # Only include the product if the price is greater than 0
        if price > 0:
            filtered_data.append(product)

    return filtered_data


def load_all_products():
    """Aggregates and loads all product data from the defined file paths."""
    global ALL_PRODUCTS
    products = []
    for file_path in FILE_PATHS:
        data = process_product_data(file_path)
        if data:
            products.extend(data)

    # Store the loaded data globally once
    ALL_PRODUCTS = products
    print(f"Flask App Initialized: Loaded a total of {len(ALL_PRODUCTS)} products.")


def search_product(search_item, all_products):
    """
    Searches for a product, sorts the results, and returns the best deal and the full sorted list.

    Updated: Stores the full list of image URLs for the carousel.
    """
    search_term = search_item.lower()
    found_products = []

    for product in all_products:
        title = str(product.get("title", "")).lower()
        if search_term in title:
            found_products.append(product)

    if not found_products:
        return None, []

    # --- SORTING LOGIC ---
    # Primary Sort: Rating (Descending)
    # Secondary Sort: Final Price (Ascending)
    found_products.sort(key=lambda p: (
        -safe_float(p.get("rating"), default_value=0.0),  # Highest Rating first
        safe_float(p.get("final_price"), default_value=float('inf'))  # Lowest Price first
    ))

    # Clean up results for presentation (Mapping new JSON fields to template fields)
    cleaned_results = []
    for product in found_products:
        # Use 'url' field for product link
        product_url = product.get("url", "#")

        # --- NEW: Store the full list of image URLs for the carousel ---
        images_list = product.get("image", [])
        # Provide a placeholder array if images list is missing or invalid
        image_urls = images_list if isinstance(images_list, list) and images_list else [
            "https://placehold.co/300x300/f0f0f0/666666?text=No+Images"]

        cleaned_results.append({
            "title": product.get("title", "N/A"),
            "initial_price": str(product.get("initial_price", "N/A")),
            "final_price": str(product.get("final_price", "N/A")),
            "rating": str(product.get("rating", "N/A")),
            "seller_name": product.get("seller_name", "N/A"),

            # Map the JSON keys to the template's required keys
            "product_url": product_url,
            "image_urls": image_urls,  # <-- Stores a LIST of URLs for the carousel
        })

    best_deal = cleaned_results[0]

    # Return ALL sorted results for pagination logic in the route
    return best_deal, cleaned_results


# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    # Retrieve search item from form (POST) or URL parameters (GET for pagination)
    search_item = request.form.get('search_item') or request.args.get('search_item')
    page = request.args.get('page', 1, type=int)
    page_size = PAGE_SIZE  # Fixed page size

    best_deal = None
    all_results = []  # All results found (before pagination)
    paginated_results = []
    total_products = 0
    total_pages = 0

    # The search runs if a search term is present (initial search or pagination click)
    if search_item and ALL_PRODUCTS:
        best_deal, all_results = search_product(search_item, ALL_PRODUCTS)

        if all_results:
            total_products = len(all_results)
            total_pages = (total_products + page_size - 1) // page_size

            # Ensure page number is valid
            if page < 1: page = 1
            if page > total_pages and total_pages > 0: page = total_pages

            # Apply pagination slice
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            paginated_results = all_results[start_index:end_index]

    # Pass data to the template
    return render_template_string(
        HTML_TEMPLATE,
        search_item=search_item,
        best_deal=best_deal,
        results=paginated_results,
        total_products=total_products,
        total_pages=total_pages,
        current_page=page,
        page_size=page_size
    )


# --- HTML TEMPLATE (Tailwind CSS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-commerce Price Comparison & Finder</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f7f7f7; }
        .shadow-custom { box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); }
        .table-header { background-color: #1f2937; color: white; }
        .carousel-image { transition: opacity 0.3s ease-in-out; }
    </style>
</head>
<body class="p-4 sm:p-8">
    <div class="max-w-7xl mx-auto">

        <header class="text-center mb-10 p-6 bg-white rounded-xl shadow-custom">
            <h1 class="text-4xl font-extrabold text-indigo-700">🛒 Marketplace Checker</h1>
            <p class="mt-2 text-lg text-gray-600">Find the best deals across multiple platforms (Lazada and Shopee), sorted by Highest Rating and Lowest Price.</p>
        </header>

        <!-- Search Form -->
        <form method="POST" action="{{ url_for('index', page=1) }}" class="flex flex-col sm:flex-row gap-4 mb-10 p-6 bg-white rounded-xl shadow-custom">
            <input type="text" name="search_item" placeholder="e.g., Portable Bluetooth Speaker" 
                   value="{{ search_item if search_item else '' }}" required
                   class="flex-grow p-3 border-2 border-indigo-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 text-gray-800">
            <button type="submit" 
                    class="bg-indigo-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-indigo-700 transition duration-150 transform hover:scale-[1.02] shadow-md focus:outline-none focus:ring-4 focus:ring-indigo-500 focus:ring-opacity-50">
                🔍 Search Products
            </button>
        </form>

        <!-- Results Display -->
        {% if search_item %}
            <div class="mt-8">
                <h2 class="text-2xl font-bold text-gray-800 mb-4">Results for: <span class="text-indigo-600">"{{ search_item }}"</span> ({{ total_products }} found)</h2>

                {% if best_deal and total_products > 0 %}
                    <!-- Product Recommendation Card (Updated with Carousel) -->
                    <div class="mb-8 p-6 bg-yellow-50 border-4 border-yellow-400 rounded-xl shadow-lg">
                        <h3 class="text-2xl font-extrabold text-yellow-800 flex items-center mb-3">
                            <span class="mr-2 text-3xl">🌟</span> TOP RECOMMENDATION (Best Value)
                        </h3>

                        <div class="flex flex-col md:flex-row gap-6">
                            <!-- Image Carousel (Left Side - 1/3 width) -->
                            <div class="w-full md:w-1/3 relative" id="image-carousel">
                                {% if best_deal.image_urls %}
                                    <div class="relative w-full aspect-square overflow-hidden rounded-lg border border-yellow-200">
                                        {% for url in best_deal.image_urls %}
                                            <img src="{{ url }}" alt="Product Image {{ loop.index }}" 
                                                 class="carousel-image absolute top-0 left-0 w-full h-full object-contain bg-white"
                                                 data-index="{{ loop.index0 }}"
                                                 onerror="this.onerror=null; this.src='https://placehold.co/300x300/f0f0f0/666666?text=Image+Load+Failed';"
                                                 style="opacity: {% if loop.index0 == 0 %}1{% else %}0{% endif %};">
                                        {% endfor %}
                                    </div>
                                    {% if best_deal.image_urls | length > 1 %}
                                        <!-- Navigation Buttons -->
                                        <button onclick="prevImage()" class="absolute top-1/2 left-0 transform -translate-y-1/2 bg-yellow-600 text-white p-2 rounded-r-lg hover:bg-yellow-700 z-10 transition opacity-80">
                                            &lt;
                                        </button>
                                        <button onclick="nextImage()" class="absolute top-1/2 right-0 transform -translate-y-1/2 bg-yellow-600 text-white p-2 rounded-l-lg hover:bg-yellow-700 z-10 transition opacity-80">
                                            &gt;
                                        </button>
                                    {% endif %}
                                {% endif %}
                            </div>

                            <!-- Recommendation Details (Right Side - 2/3 width) -->
                            <div class="w-full md:w-2/3">
                                <p class="text-lg text-gray-700 mb-1"><span class="font-semibold text-gray-900">🏆 Product:</span> <a href="{{ best_deal.product_url }}" target="_blank" class="text-indigo-600 hover:underline">{{ best_deal.title }}</a></p>
                                <p class="text-lg text-gray-700 mb-1"><span class="font-semibold text-gray-900">⭐ Rating:</span> <span class="font-bold text-green-600">{{ best_deal.rating }}</span></p>
                                <p class="text-lg text-gray-700 mb-1"><span class="font-semibold text-gray-900">🧑 Seller:</span> <span class="font-bold text-gray-800">{{ best_deal.seller_name }}</span></p>
                                <p class="text-lg text-gray-700"><span class="font-semibold text-gray-900">💲 Final Price:</span> <span class="font-bold text-xl text-red-600">{{ best_deal.final_price }}</span></p>
                            </div>
                        </div>
                    </div>

                    <!-- Full Results Table -->
                    <div class="overflow-x-auto bg-white rounded-xl shadow-custom">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="table-header">
                                <tr>
                                    <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider">Title / Link</th>
                                    <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider w-32">Initial Price</th>
                                    <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider w-32">Final Price</th>
                                    <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider w-20">Rating</th>
                                    <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider w-32">Seller</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200 text-gray-800">
                                {% for product in results %}
                                <tr class="hover:bg-gray-50 transition duration-150 {% if (current_page - 1) * page_size + loop.index == 1 %} bg-indigo-50 font-semibold {% endif %}">
                                    <td class="px-4 py-3 text-sm max-w-xs">
                                        {% if (current_page - 1) * page_size + loop.index == 1 %} (Recommended) {% endif %}
                                        <a href="{{ product.product_url }}" target="_blank" class="text-indigo-600 hover:underline">
                                            {{ product.title }}
                                        </a>
                                    </td>
                                    <td class="px-4 py-3 text-sm">{{ product.initial_price }}</td>
                                    <td class="px-4 py-3 text-sm font-bold text-red-600">{{ product.final_price }}</td>
                                    <td class="px-4 py-3 text-sm text-green-700">{{ product.rating }}</td>
                                    <td class="px-4 py-3 text-sm">{{ product.seller_name }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>

                    <!-- Pagination Controls -->
                    {% if total_pages > 1 %}
                        <div class="flex justify-between items-center mt-6 p-4 bg-white rounded-xl shadow-custom">
                            <p class="text-sm text-gray-700">Page {{ current_page }} of {{ total_pages }}</p>
                            <nav class="flex space-x-2">
                                <!-- Previous Button -->
                                <a href="{{ url_for('index', search_item=search_item, page=current_page - 1) }}"
                                   class="px-4 py-2 border rounded-lg transition duration-150 
                                   {% if current_page == 1 %} bg-gray-200 text-gray-500 cursor-not-allowed pointer-events-none {% else %} bg-indigo-50 text-indigo-700 hover:bg-indigo-100 {% endif %}">
                                    Previous
                                </a>

                                <!-- Next Button -->
                                <a href="{{ url_for('index', search_item=search_item, page=current_page + 1) }}"
                                   class="px-4 py-2 border rounded-lg transition duration-150 
                                   {% if current_page == total_pages %} bg-gray-200 text-gray-500 cursor-not-allowed pointer-events-none {% else %} bg-indigo-50 text-indigo-700 hover:bg-indigo-100 {% endif %}">
                                    Next
                                </a>
                            </nav>
                        </div>
                    {% endif %}

                {% else %}
                    <!-- No Results Message -->
                    <div class="p-6 bg-red-100 border-l-4 border-red-500 text-red-700 rounded-lg">
                        <p class="font-semibold">No products found matching "{{ search_item }}".</p>
                        <p class="text-sm">Please ensure the product name is correct and the necessary JSON files are available.</p>
                    </div>
                {% endif %}
            </div>
        {% endif %}
    </div>

    <script>
        let currentImageIndex = 0;
        let images = [];

        function updateCarousel() {
            // Get all image elements inside the carousel
            images = document.querySelectorAll('#image-carousel .carousel-image');
            if (images.length === 0) return;

            // Hide all images
            images.forEach(img => {
                img.style.opacity = '0';
                img.style.zIndex = '10';
            });

            // Show the current image
            images[currentImageIndex].style.opacity = '1';
            images[currentImageIndex].style.zIndex = '20'; // Bring active image to front
        }

        function nextImage() {
            currentImageIndex = (currentImageIndex + 1) % images.length;
            updateCarousel();
        }

        function prevImage() {
            currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
            updateCarousel();
        }

        // Initialize carousel when the page loads
        window.onload = updateCarousel;
    </script>
</body>
</html>
"""

# Call load_all_products to populate the ALL_PRODUCTS list when the app starts
load_all_products()

# Entry point for running the Flask application
if __name__ == '__main__':
    # Use 127.0.0.1 (localhost) to ensure it's accessible locally, and debug=True for development.
    app.run(host='127.0.0.1', port=5000, debug=True)
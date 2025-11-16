# **🛒 Marketplace Checker**

This project is a full-stack web application designed to aggregate and compare product prices and ratings from multiple e-commerce marketplaces (simulated by local JSON data). It is built as a single-file application using **Flask** for the backend API and **Vanilla JavaScript** with **Tailwind CSS** for a responsive, modern frontend.

The primary goal is to provide users with the *best* possible deal by intelligently sorting results based on product rating and final price.

## **🌟 Key Features**

* **Intelligent Sorting:** Search results are automatically prioritized by **Highest Rating** and then by **Lowest Final Price** to ensure the best value is always shown first.  
* **Best Deal Highlight:** The top-ranked product is highlighted prominently on the results page.  
* **Responsive Interface:** A clean, mobile-friendly design built with Tailwind CSS.  
* **Asynchronous Search:** Uses a dedicated Flask API endpoint (/api/search) for fast, non-blocking searching and data retrieval.  
* **Client-Side Pagination:** Efficient display of large result sets with full pagination controls.  
* **Single-File Deployment:** The entire application logic—server, HTML template, CSS, and JavaScript—is contained within a single Python file (marketplace\_checker-flask.py).

## **🛠️ Setup and Installation**

### **Prerequisites**

You must have **Python 3.x** installed.

### **1\. Clone the Repository**

git clone \[https://github.com/sarahjoy18/marketplace\_checker.git\](https://github.com/sarahjoy18/marketplace\_checker.git)  
cd marketplace\_checker

### **2\. Set up the Environment**

It is highly recommended to use a Python virtual environment:

```console
python -m venv venv  
source venv/bin/activate  # On macOS/Linux  
# venv\\Scripts\\activate   \# On Windows
```

### **3\. Install Dependencies**

The application relies only on Flask and Flask-CORS:

```console
pip install Flask Flask-CORS
```
### **4\. Data Setup (Crucial)**

The application requires three JSON files in the root directory to simulate the data from different marketplaces.

**File Names Required:**

1. Lazada \- Products PH.json  
2. Lazada \- Products.json  
3. Shopee \- products.json

The server will look for these files on startup. To use the application, ensure these files are populated with arrays of product objects, where each object contains title, initial\_price, final\_price, rating, seller\_name, and images (an array of URLs).

## **▶️ How to Run**

1. Ensure your virtual environment is active and dependencies are installed.  
2. Run the main application file:  
   python marketplace\_checker-flask.py

3. Once the server starts, open your web browser and navigate to the local address:  
   **http://127.0.0.1:5000/**

## **📂 Project Structure**

The simplicity of this project is that all components are contained within one Python file:

.  
├── marketplace\_checker-flask.py  \<-- The single, complete Flask application file  
├── Lazada \- Products PH.json     \<-- Required data source 1  
├── Lazada \- Products.json        \<-- Required data source 2  
└── Shopee \- products.json        \<-- Required data source 3

### **Technical Breakdown in marketplace\_checker-flask.py**

| Component | Technology | Role |
| :---- | :---- | :---- |
| **Backend** | Python, Flask | Handles data loading, sorting logic, and serving the search API (/api/search). |
| **Frontend UI** | HTML5, Tailwind CSS | Defines the layout and styling, ensuring full responsiveness. |
| **Frontend Logic** | Vanilla JavaScript | Manages user input, makes API requests, renders results, handles pagination, and controls the image carousel. |


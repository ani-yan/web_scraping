import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options (optional: run headless)
chrome_options = Options()
# chrome_options.add_argument('--headless')  # Uncomment to run in headless mode if you don't need to see the browser

# Initialize the Chrome WebDriver
driver = webdriver.Chrome(options=chrome_options)

# List of URLs to process
# ADD PRE-COLLECTED URLs (BeatufulSoup works well for this)
# EXAMPLE DICTIONARY
url_dict = {
'hakabiotikner': 'https://www.med911.am/hy/ecommerce/%D0%B0%D0%BD%D1%82%D0%B8%D0%B1%D0%B8%D0%BE%D1%82%D0%B8%D0%BA%D0%B8-c28287759',
'vitaminner1': 'https://www.med911.am/hy/ecommerce/%D0%B2%D0%B8%D1%82%D0%B0%D0%BC%D0%B8%D0%BD%D1%8B-%D0%B4%D0%BB%D1%8F-%D0%B2%D0%B7%D1%80%D0%BE%D1%81%D0%BB%D1%8B%D1%85-c28287927',
'vitaminner2': 'https://www.med911.am/hy/ecommerce/%D0%B2%D0%B8%D1%82%D0%B0%D0%BC%D0%B8%D0%BD%D1%8B-%D0%B4%D0%BB%D1%8F-%D0%B4%D0%B5%D1%82%D0%B5%D0%B9-c28287924',

    # Add more URLs to this list as needed
}
urls = list(url_dict.values())

# Initialize an empty list to hold all product data
all_products = []

# Iterate over the URLs
for idx, url in enumerate(urls, start=1):
    print(f"Processing URL {idx}/{len(urls)}: {url}")
    driver.get(url)
    
    # Wait for the page to load
    wait = WebDriverWait(driver, 10)
    
    # Click the "More" button until all products are loaded
    while True:
        try:
            # Locate the "More" button using its aria-label attribute
            more_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@role='button' and @aria-label='Ավելին >']")
            ))
            more_button.click()
            # Wait for new products to load
            wait.until(EC.staleness_of(more_button))
            wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'div.filterable-item.show-title')
            ))
        except:
            # No more "More" buttons to click
            break
    
    # Find all product elements
    products = driver.find_elements(By.CSS_SELECTOR, 'div.filterable-item.show-title')
    
    # Loop through each product to extract the name and price
    for product in products:
        try:
            # Extract the product name and data-item-id
            name_div = product.find_element(By.CSS_SELECTOR, 'div.filterable-item-title-text')
            product_name = name_div.text.strip()
            data_item_id = name_div.get_attribute('data-item-id').strip()
            
            # Extract the product price
            price_span = product.find_element(By.CSS_SELECTOR, 'div.ecommerce-item-price span.price')
            product_price = price_span.text.strip()
            
            # Store the product information in a dictionary
            product_data = {
                'Iteration': idx,
                'Product ID': data_item_id,
                'Name': product_name,
                'Price': product_price,
                'URL': url
            }
            all_products.append(product_data)
        except Exception as e:
            print(f"Error processing product: {e}")

# Close the WebDriver
driver.quit()

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(all_products)

# Add a new column 'Price Numeric' which extracts numerical value from 'Price'
# Remove non-digit characters and convert to float
try:
    df['price_numeric'] = df['Price'].str.replace(r'[^\d.]', '', regex=True).str.replace(' ', '').astype(float)
except Exception as e:
    print(f"Error converting price to numeric: {e}")

df.to_csv('med911_products.csv', index=False)

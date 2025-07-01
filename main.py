import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# ========= CHROME SETUP ========= #
options = Options()
options.add_argument("--headless")  # Optional: comment this out to see browser
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ========= LOAD INPUT EXCEL ========= #
input_file = 'Try AI creatives.xlsx'
df = pd.read_excel(input_file)

# ========= PROMPT TEMPLATE ========= #
prompt_template = (
    "Take this {product_type} and do a creative {shoot_type} of this with {theme} theme.\n\n"
    "Creative size : 1:1 square ratio.\n"
    "This should have a Discount Led copy.\n\n"
    "Copy Instruction :\n\n"
    "Copy contains these three (Product detail + Discount + After discount price)\n\n"
    "Use each of the following text elements only once. Do not repeat, rephrase, or restyle the same message in different parts of the layout.\n\n"
    "Product Detail : {product_title} (It should be in small sans serif font below 12px)\n"
    "Discount : Flat {discount} % off (Should be prominent but elegant - not overpowering the product. Use refined font with medium weight, not bold.)\n"
    "After discount price : Only at ₹ {selling_price} (Small italic sans serif font, little bigger than 12px)\n\n"
    "Text placement rules:\n"
    "Do NOT place text over the model, product, or any visually detailed area.\n"
    "All text must be placed in empty or plain background area only, preferably in 25 to 40 percent of the frame.\n"
    "Maintain a minimum 20px padding from all edges and subject silhouette.\n"
    "Avoid placing any text on fabric folds, textures, or facial features.\n\n"
    "Typography Rules to follow:\n"
    "Make sure typography has max two colors and max two font types if needed.\n"
    "Make sure to follow alignment and layout rules properly.\n"
    "Apply a 3-column grid to match the visual rhythm and spacing.\n"
    "Add minimal design elements based on the given theme to guide the eye and separate content.\n"
    "Ensure text has high contrast against the background to improve readability.\n"
    "Good to have some small font sizes and empty clean space so that typography and entire visuals can breathe.\n\n"
    "DO NOT ADD ANY LOGO OR BRAND NAME WHICH IS NOT MENTIONED IN THE PROMPT.\n"
    "TYPOGRAPHY SHOULD BE DESIGN AS PER MOBILE SCREEN VIEW."
)

# ========= SCRAPER FUNCTION ========= #
def get_product_info(url):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # Wait for product title or fallback image
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))

        # ===== IMAGE SCRAPE (via soup) =====
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        image = soup.find('img', {'class': 'css-1scovo6'})
        product_image = image['src']

        # ===== TITLE SCRAPE =====
        try:
            more_span = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "css-19vzlot")))
            driver.execute_script("""
                arguments[0].scrollIntoView({behavior: "instant", block: "center"});
                arguments[0].click();
            """, more_span)
            time.sleep(1)  # Give time for title to expand
        except:
            pass  # Button might not exist, ignore

        title = driver.find_element(By.TAG_NAME, 'h1').text.strip()

        # ===== PRICE & DISCOUNT SCRAPE =====
        try:
            price = driver.find_element(By.CLASS_NAME, 'css-36xp6j').text.replace('₹', '').replace(',', '').strip()
        except:
            price = '0'

        try:
            discount = driver.find_element(By.CLASS_NAME, 'css-11yh7r7').text.replace('%', '').replace('OFF', '').strip()
        except:
            discount = '0'

        return product_image, title, price, discount

    except Exception as e:
        print(f"❌ Error fetching data from {url}: {e}")
        return '', 'Product Title', '0', '0'

# ========= PROCESS LOOP ========= #
output_rows = []

for idx, row in df.iterrows():
    print(f"Processing row {idx + 1} of {len(df)}")

    url = row['product_page_url']
    product_type = row['product_type']
    shoot_type = row['shoot_type']
    theme = row['theme']

    product_image, title, selling_price, discount = get_product_info(url)

    prompt = prompt_template.format(
        product_type=product_type,
        shoot_type=shoot_type,
        theme=theme,
        product_title=title,
        selling_price=selling_price,
        discount=discount
    )

    output_rows.append({
        'Product_image': product_image,
        'template_image': '',
        'prompt': prompt
    })

    time.sleep(2)  # polite pause to avoid hammering server

# ========= SAVE TO CSV ========= #
output_df = pd.DataFrame(output_rows)
output_df.to_csv("creative_output.csv", index=False)
print("✅ Done! Output saved to creative_output.csv")

# ========= CLOSE BROWSER ========= #
driver.quit()

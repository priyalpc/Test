from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


# --- Setup WebDriver ---
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()

# --- Step 1: Open Website ---
driver.get("https://opensource-demo.orangehrmlive.com/")

# --- Step 2: Login ---
wait = WebDriverWait(driver, 10)
username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
password = driver.find_element(By.NAME, "password")
login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

username.send_keys("Admin")
password.send_keys("admin123")
login_button.click()

# --- Step 3: Verify Dashboard ---
wait.until(EC.presence_of_element_located((By.XPATH, "//h6[text()='Dashboard']")))
print("✅ Logged in successfully and Dashboard loaded.")

# --- Step 4: Navigate to Admin tab ---
admin_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Admin']")))
admin_tab.click()

wait.until(EC.presence_of_element_located((By.XPATH, "//h6[text()='System Users']")))
print("✅ Navigated to Admin tab successfully.")

# --- Step 5: Search for an employee in Admin section ---
search_box = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='Username']/following::input[1]")))
search_box.send_keys("Admin")
search_button = driver.find_element(By.XPATH, "//button[normalize-space()='Search']")
search_button.click()
print("✅ Performed employee search.")

time.sleep(2)

# --- Step 6: Navigate to PIM and add a new employee ---
pim_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='PIM']")))
pim_tab.click()

add_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Add']")))
add_button.click()

# Fill Add Employee form
first_name = wait.until(EC.presence_of_element_located((By.NAME, "firstName")))
middle_name = driver.find_element(By.NAME, "middleName")
last_name = driver.find_element(By.NAME, "lastName")

first_name.send_keys("Priya")
middle_name.send_keys("R")
last_name.send_keys("Kumar")

save_button = driver.find_element(By.XPATH, "//button[normalize-space()='Save']")
save_button.click()
print("✅ Added new employee successfully.")

# --- Step 7: Navigate to My Info and verify ---
my_info_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='My Info']")))
my_info_tab.click()

wait.until(EC.presence_of_element_located((By.XPATH, "//h6[text()='Personal Details']")))
print("✅ Navigated to My Info successfully.")

# --- Step 8: Logout ---
user_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//p[@class='oxd-userdropdown-name']")))
user_dropdown.click()

logout_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Logout']")))
logout_button.click()

wait.until(EC.presence_of_element_located((By.NAME, "username")))
print("✅ Logged out successfully.")

# --- Close Browser ---
driver.quit()
print("🎯 Test Completed Successfully.")

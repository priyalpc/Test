# send_whatsapp_web.py
import webbrowser
import pyautogui
import time

pyautogui.FAILSAFE = True  # move mouse to top-left to abort

message = "hi guys have a good day"

# Open WhatsApp Web
webbrowser.open("https://web.whatsapp.com")
print("Opening WhatsApp Web... give the page time to load and (if needed) scan QR code.")
time.sleep(10)   # increase if your internet is slow or you need time to scan QR

# ====== IMPORTANT ======
# At this point: manually click the chat you want to send the message to.
# Alternatively, if the chat is already visible and selected, script will type directly.
# =======================

print("Please click the chat window now. Script will type message in 5 seconds...")
time.sleep(5)

# Type the message and send
pyautogui.typewrite(message)
time.sleep(0.2)
pyautogui.press('enter')

print("Message sent (if the chat was selected).")

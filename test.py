import dotenv
import os

from client import PastebinClient

dotenv.load_dotenv()
dev_key = os.environ.get('PASTEBIN_DEVELOPER_KEY')
username = os.environ.get('PASTEBIN_USERNAME')
password = os.environ.get('PASTEBIN_PASSWORD')

client = PastebinClient(dev_key)
client.login(username, password)
# user_details = client.list_user_details()

# print(user_details)

# pastes_details = client.list_pastes_details()
# pastes_raw = client.list_pastes_raw()

# for paste_details in pastes_details:
#     print(paste_details)

# for paste_raw in pastes_raw:
#     print(paste_raw)

new_paste = client.create_paste("Hello from my Python code", name="Paste from test.py",
                                visibility="unlisted", highlighting="python", lifespan='N')
new_key = new_paste.key

print("New paste key: " + new_key)

new_paste_text = client.fetch_paste_raw(new_key)
print("New paste text: " + new_paste_text)

new_paste_details = client.fetch_paste_details(new_key)
print("New paste details: " + str(new_paste_details))

user_pastes_details = client.list_pastes_details()
for paste in user_pastes_details:
    print(paste)

user_pastes_raw = client.list_pastes_raw()
for paste in user_pastes_raw:
    print(paste)

user_details = client.list_user_details()
print("User Details: " + str(user_details))

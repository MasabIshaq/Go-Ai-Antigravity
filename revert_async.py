import re

with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Endpoints that were changed to def
def_endpoints = [
    "def me(",
    "def api_signup(",
    "def api_login(",
    "def api_logout(",
    "def api_list_chats(",
    "def api_list_keys(",
    "def api_create_key(",
    "def api_revoke_key(",
    "def api_get_chat(",
    "def api_new_chat(",
    "def api_update_chat(",
    "def api_delete_chat(",
    "def api_admin_verify(",
    "def api_admin_stats(",
    "def api_admin_reports(",
    "def api_fix_report(",
    "def api_edit_report(",
    "def api_admin_chat_reply(",
    "def api_share_chat(",
    "def api_get_share(",
    "def api_continue_share(",
    "def api_get_file(",
    "def api_report(",
    "def api_health(",
    "def v1_list_chats("
]

for endpoint in def_endpoints:
    content = content.replace(endpoint, "async " + endpoint)

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Reverted endpoints to async def.")

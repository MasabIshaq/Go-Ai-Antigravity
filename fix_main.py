import re

with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace async def with def for all functions except the streaming ones and event generator
funcs_to_keep_async = ['v1_chat_stream', 'api_chat_stream', 'event_generator', 'api_upload', 'startup']
lines = content.split('\n')
for i, line in enumerate(lines):
    if line.strip().startswith('async def '):
        func_name = line.split('async def ')[1].split('(')[0]
        if func_name not in funcs_to_keep_async:
            lines[i] = line.replace('async def ', 'def ', 1)

content = '\n'.join(lines)

# Fix v1_chat_stream and api_chat_stream blocking sync calls
old_str = '''    sync_user_memory(user["id"], body.messages)
    api_messages = _with_system(_messages_for_api(body.messages), user)'''

new_str = '''    await asyncio.to_thread(sync_user_memory, user["id"], body.messages)
    api_messages = await asyncio.to_thread(_with_system, _messages_for_api(body.messages), user)'''

content = content.replace(old_str, new_str)

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')

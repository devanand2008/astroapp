import os

files_to_update = [
    "frontend/user-dashboard.html",
    "frontend/pending.html",
    "frontend/panjangam.js",
    "frontend/login.js",
    "frontend/login.html",
    "frontend/index.html",
    "frontend/chat.js",
    "frontend/astro-dashboard.html",
    "frontend/ai-chat.js",
    "frontend/ads.js",
    "frontend/admin.html",
    "START_APP.bat",
    "backend/main.py"
]

for filepath in files_to_update:
    path = os.path.join("d:/astro app 3.0 web", filepath)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = content.replace(":8000", ":8080")
        content = content.replace("port 8000", "port 8080")
        content = content.replace("port=8000", "port=8080")
        content = content.replace("|| 8000", "|| 8080")
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"Not found {filepath}")

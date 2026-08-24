import os
import re

templates_dir = r"C:\Users\HAROON TRADERS\Desktop\dbms\templates"
css_link = '<link rel="stylesheet" href="/static/style.css">'

for filename in os.listdir(templates_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove all existing link tags pointing to style.css to start fresh
        content = re.sub(r'<link rel=[\'\"]stylesheet[\'\"] href=[\'\"]/static/style\.css[\'\"]>', '', content)
        content = re.sub(r'<link rel=\\"stylesheet\\" href=\\"/static/style\.css\\">', '', content)
        
        # Inject correct tag
        content = content.replace('<head>', f'<head>{css_link}')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
print("Fixed CSS links in all templates.")

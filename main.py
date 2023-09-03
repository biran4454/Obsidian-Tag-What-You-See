import os
import re

if __name__ == '__main__':
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    elif os.path.exists('config'):
        with open('config') as f:
            root_dir = f.read().strip()
    else:
        root_dir = os.getcwd()
    
    with open('tags.txt', 'r') as f:
        tags_info = [l.strip() for l in f.read().splitlines() if l.strip()]
        tags = [{'tag': t.split('~')[0].strip(), 'regex': (t.split('~')[1].strip() if '~' in t else '')} for t in tags_info]

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md"):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                dash_count = 0
                tags_line = None
                in_tags = False
                frontmatter_end_line = None
                tags_to_add = []
                tags_to_ignore = []
                for i, line in enumerate(lines):
                    if line.startswith('---'):
                        dash_count += 1
                        if dash_count == 2:
                            frontmatter_end_line = i
                        continue
                    if dash_count == 1 and line.startswith('tags:'):
                        tags_line = i
                        in_tags = True
                        continue
                    if in_tags and dash_count == 1 and line.startswith('  - '):
                        if 'twys/' in line:
                            tags_to_ignore.append(line.split('  - twys/')[1].strip())
                    else:
                        in_tags = False
                    if dash_count > 1:
                        for tag in tags:
                            if tag['tag'] not in tags_to_add and tag['tag'] not in tags_to_ignore:
                                if tag['regex'] == '':
                                    if tag['tag'].lower() in line.lower():
                                        tags_to_add.append(tag['tag'])
                                elif re.search(tag['regex'], line.lower()):
                                    tags_to_add.append(tag['tag'])
                if tags_to_add:
                    if not tags_line:
                        lines.insert(frontmatter_end_line, 'tags: \n')
                        tags_line = frontmatter_end_line
                    for tag in tags_to_add:
                        print(f'Adding tag twys/{tag} to {file}')
                        lines.insert(tags_line + 1, f'  - twys/{tag}\n')
                    with open(os.path.join(root, file), 'w', encoding='utf-8') as f:
                        f.writelines(lines)
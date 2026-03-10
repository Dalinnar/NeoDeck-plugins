import os
import re
import zipfile
import sys

plugin_dir = sys.argv[1]

init_file = os.path.join(plugin_dir, "init.py")

text = open(init_file).read()

name = re.search(r"plugin_name\s*=\s*['\"](.+?)['\"]", text).group(1)
version = re.search(r"plugin_version\s*=\s*['\"](.+?)['\"]", text).group(1)

output = f"{name}-{version}.deck"

with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(plugin_dir):
        for f in files:
            path = os.path.join(root, f)
            arc = os.path.relpath(path, plugin_dir)
            z.write(path, arc)

print(output)

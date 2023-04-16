import os
import re

def print_grammars(filename):
    full_path = os.path.abspath("data")
    print(full_path)
    filenames = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]
    for f in filenames:
        if f == filename:
            filenames.pop(filenames.index(f))
            filenames.insert(0, f)
    indexes = {i:f for i,f in enumerate(filenames)}
    print('{} grammar{} found: '.format(len(indexes),'s' if len(indexes) > 1 or len(indexes) == 0 else ''))
    for key,value in indexes.items():
        if key == 0:
            print(f"{key}: '{value}' (current)")
        else:
            print(f"{key}: '{value}'")
    return indexes

def normalize(string):
    string = string.lower().strip()
    string = re.sub(r"[&#¿¡(...)\n{}())/-_\r'‘’,.]", '', string)
    string = re.sub(r"'", "", string)
    string = re.sub(r'"', '"', string)
    return(string)

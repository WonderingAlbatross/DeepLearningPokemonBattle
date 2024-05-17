#from https://github.com/hsahovic/poke-env/blob/master/scripts/data_script_utils.py

import re
import os



def fetch_and_clean_ps_data(file_path,filename_out):
    with open(file_path, 'r') as file:
        data = file.read()

    # Remove start and end of the file
    data = "{" + "= {".join(data.split("= {")[1:])[:-2]

    # Transform tabs into spaces
    data = data.replace("\t", " ")

    # Transform keys into correct json strings
    data = re.sub(r"([\w\d]+): ", r'"\1": ', data)

    # Transform single quoted text into double quoted text
    data = re.sub(r"'([\w\d ]+)'", r'"\1"', data)

    # Remove comments
    data = re.sub(r" +//.+", "", data)

    # Remove empty lines
    for _ in range(3):
        data = re.sub(r"\n\n", "\n", data)

    data = re.sub(r",\n( +)\]", r"\n\1]", data)

    # Correct double-quoted text inside double-quoted text
    data = re.sub(r': ""(.*)":(.*)",', r': "\1:\2",', data)

    # Correct isolated "undefined" values
    data = re.sub(r": undefined", r": null", data)

    # Callback and handlers
    for function_title_match in (r"(on\w+)", r"(\w+Callback)"):
        for n_space in range(10):
            spaces = " " * (n_space)
            pattern = (
                r"^"
                + spaces
                + function_title_match
                + r"\((\w+, )*(\w+)?\) \{\n(.+\n)+?"
                + spaces
                + r"\},"
            )
            sub = spaces + r'"\1": "\1",'
            data = re.sub(pattern, sub, data, flags=re.MULTILINE)
        pattern = function_title_match + r"\(\) \{\s*\}"
        sub = r'"\1": "\1"'
        data = re.sub(pattern, sub, data, flags=re.MULTILINE)

    # Remove incorrect commas
    data = re.sub(r",\n( *)\}", r"\n\1}", data)

    # Null arrow functions
    data = re.sub(r"\(\) => null", r"null", data)

    # Remove incorrect commas
    data = re.sub(r",\n( *)\}", r"\n\1}", data)
    data = re.sub(r",\n( +)\]", r"\n\1]", data)
    # Correct double-quoted text inside double-quoted text

    data = re.sub(r': "(.*)"(.*)":(.*)",', r': "\1\2:\3",', data)
    data = re.sub(r': ""(.*)":(.*)",', r': "\1:\2",', data)

    # Correct non-quoted number keys
    data = re.sub(r"(\d+):", r'"\1":', data)
    # Correct non-quoted H keys

    data = re.sub(r"H: ", r'"H": ', data)
    data = re.sub(r", moves:", r', "moves":', data)
    data = re.sub(r", nature:", r', "nature":', data)


    with open(filename_out, "w+") as f:
        f.write(data)



for filename in os.listdir('./'):
    if filename.endswith('.ts'):
        filename_out = './'+filename[:-3] + '.json'
        fetch_and_clean_ps_data(filename, filename_out)
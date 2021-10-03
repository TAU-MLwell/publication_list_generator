from pathlib import Path

# Your name (used in google scholar and dblp)
author_name = "Ran Gilad-Bachrach"

# The file name of the web-of-science citation report
wos_file_name = r"/mnt/c/temp/savedrecs.txt"

# The file name where the results will be stored
output_file = r"/mnt/c/temp/publications.txt"

# The impact factor and ranking file-name - Only change this if impact factors have been changed.
utils_path = Path(__file__).parent
if_file_name = utils_path / r"scimagojr 2020.csv"

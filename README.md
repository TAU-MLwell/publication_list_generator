# Publication List Generator

This repository automates the process of data collection from several sources to create a list of publication for an author, including citation counts and impact factor. This is an initial version and creates partial results so some manual editing is still needed.

## Usage Instructions:

1. Clone this repository:

(Copy and paste the following lines to the terminal)

```terminal
git clone https://github.com/TAU-MLwell/publication_list_generator.git
cd publication_list_generator
```

2. Download citations from WOS:

   1. Go to https://www.webofscience.com/wos/author/search.
   2. Search for your name.
   3. On the right pane click "view citation report".
   4. Click "Export Full Report".
   5. Save to file in text format.

3. Set the proper values in the [user_properties.py file](utils/user_properties.py).

4. Run the [publication_list_generator.py](publication_list_generator.py) file in the terminal:

```
python publication_list_generator.py
```

That's it. The publication list should appear at the location you specified as _output_file_ in [user_properties.py](utils/user_properties.py). (:

## prerequisits:

- jellyfish
- pandas
- scholarly

Copy and paste the following line to the terminal to install them:

```
pip install jellyfish pandas scholarly
```

or

```
pip install -r requirements.txt
```

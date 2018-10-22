# .att parser
This python script will create mapping between an existing 3D model in Cognite's data platform (CDP) and .att files produced from PDMS.

# Usage
You must set environment variables `COGNITE_API_KEY` and `COGNITE_PROJECT` in order to load node_id's from CDP.

Given a 3D model in CDP with known `model_id` and `revision_id` (hard-coded for simplicity in `parse_att_file.py`), and a folder of matching .att files, a map between Cognite 3D node id's and PDMS id's can be created by running
`python3 parse_att_files.py -i /path/to/folder/with/att/files`.

# Caching
Since requesting node id's and parsing .att files can be a bit slow, the results are cached using `pickle`. To force reloading node id's from CDP, run 

`python3 parse_att_files.py -i /path/to/folder/with/att/files -t` (`t` for threed).

Similarly, if you want to reload .att files, run with

`python3 parse_att_files.py -i /path/to/folder/with/att/files -a` (`a` for attribute).


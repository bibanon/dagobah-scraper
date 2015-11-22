# handy file interfacing utilities

import os
import requests
import json

def mkdirs(path):
	"""Make directory, if it doesn't exist."""
	if not os.path.exists(path):
		os.makedirs(path)

def download_file(local_filename, url, clobber=False):
	"""Download the given file. Clobber overwrites file if exists."""
	dir_name = os.path.dirname(local_filename)
	mkdirs(dir_name)

	if clobber or not os.path.exists(local_filename):
		i = requests.get(url)

		# if not exists
		if i.status_code == 404:
			print('Failed to download file:', local_filename, url)
			return False

		# write out in 1MB chunks
		chunk_size_in_bytes = 1024*1024  # 1MB
		with open(local_filename, 'wb') as local_file:
			for chunk in i.iter_content(chunk_size=chunk_size_in_bytes):
				local_file.write(chunk)

	return True

# obtain JSON object from folder
def json2object(path):
    with open(path, 'r') as outfile:
        return json.load(outfile)

# write gallery object to JSON file in folder
def object2json(gallery, path):
    with open(path, 'w') as outfile:
      json.dump(gallery, outfile, sort_keys=True, indent=4, separators=(',', ': '))

# write gallery object to JSON file in folder
def object2pickle(gallery, path):
    with open(path, 'w') as outfile:
      pickle.dump(gallery, outfile)
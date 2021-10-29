## Functions to read/write json files ##


import os
import json
from shutil import copyfile
import numpy as np

def write_to_file(pill_num, file_name, data):
	'''
	Saves a pill number and its encoding to a json file if the
	file does not already contain the number
	Args
		pill_num: pill number
		file_name: json file to write to 
		data: pill encoding
	Returns
		code: None if write occurs; pill code otherwise
	'''
	in_db = False
	file_contents = []
	code = None
	file_contents = prep_file(file_name)
	
	if len(file_contents) > 0:
		for pill in file_contents:
			if pill_num == pill["Pill Number"]:
				in_db = True
				code = pill["Code"]
				print("    Already in database")
	
	if not in_db:	
		#b = data.tolist()
		b = data.tolist()
		d = {"Pill Number" : pill_num, "Code" : b}
		f = open(file_name, "a")
		if os.stat(file_name).st_size == 0:
			f.write("[\n")
		else:
			f.write(",\n")
		f.writelines(json.dumps(d, indent=2))
		print("    wrote ", pill_num)
		f.close()
	return code

def get_data_from_file(file_name, pillID):
	'''
	Find the pill with a specific ID in a json database
	Args
		file_name: json file to search
		pillID: ID to search for
	Returns
		dic_code: code of found pill or "not found"
		num: pill number of found pill or "not found"
	'''
	data = prep_file(file_name)
	dic_code = "not found"
	num = "not found"
	
	for pill in data:
		dic_code = pill["Code"]
		if dic_code == pillID:
			num = str(pill["Pill Number"])
			print("Is this pill " + num)
			return dic_code, num
	return dic_code, num
	
def prep_file(src):
	'''
	Opens a json file and loads the data as a json object
	Args
		src: location of the json file
	Returns
		json file data as a numpy array
	'''
	
	if os.stat(src).st_size == 0:
		return []
	else:
		copyfile(src, "json/tmp.json")
		f = open("json/tmp.json", "a")
		f.write(']')
		f.close()
		with open("json/tmp.json") as jfile:
			data = json.load(jfile)
		os.remove("json/tmp.json")
	return np.array(data)

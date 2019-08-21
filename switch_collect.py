'''

Name: switch_collect.py
Description: This script collects all switches/ports and outputs them into a CSV file for manually defining the target ports on new switches

Usage:  python switch_collect.py <path_to_config_files> <output_file_name>

'''


import glob
import sys
import re


def list_configs(path):
	file_list = glob.glob(path + "/*.*")
	return(file_list)


def parse_interfaces(file_list):
	# Create our return dictionary
	interfaces = {}

	# Loop through configuration files to parse interface information
	for config_file in file_list:
		f = open(config_file,'r')
		config_raw = f.readlines()
		f.close()
		# We assume our filename matches the switch host name so we extract just the file name
		hostname = config_file.split("/")[len(config_file.split("/"))-1].split(".")[0]
		for line in config_raw:
    		# If the line begins with interface we need to save that for future use
			if re.match("^interface .*",line):
				if hostname in interfaces.keys():
					interfaces[hostname].append(line.split()[1].strip('\r\n'))
				else:
					interfaces[hostname] = []
					interfaces[hostname].append(line.split()[1].strip('\r\n'))
	return(interfaces)

def build_output_file(interface_list,output_file):
	f = open(output_file,'w')
	for k,v in interface_list.items():
		for item in v:
			f.write(k + "," + item + "\n")
	f.close()


def main():

	if len(sys.argv) < 3:
		print("\nScript Execution Halted - Not enough arguments provided\n\nUsage:  switch_collect.py <path_to_config_files> <output_file_name>\n\n")
	else:
		files = list_configs(sys.argv[1])
		interface_output = parse_interfaces(files)
		build_output_file(interface_output,sys.argv[2])


if __name__ == '__main__':
  main()





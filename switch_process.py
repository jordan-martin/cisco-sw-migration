'''

Name: switch_process.py
Description: This script imports the manually modified CSV of port mappings and converts that to the new configurations.

Usage:  python switch_process.py <path_to_config_files> <input_file_name> <output_directory> <template_file>

'''


import glob
import sys
import re
from ciscoconfparse import CiscoConfParse


def build_mapping(input_csv):
	switch_map = {}
	interface_map = {}
	f = open(input_csv,'r')
	lines = f.readlines()
	f.close()

	for line in lines:
		source_switch = line.split(',')[0]
		source_port = line.split(',')[1]
		dest_switch = line.split(',')[2]
		dest_port = line.strip('\r\n').split(',')[3]

		

		if source_port != "IGNORE" and dest_port !="IGNORE":
			if source_switch not in switch_map.keys():
				switch_map[source_switch] = dest_switch
			if source_switch not in interface_map.keys():
				interface_map[source_switch] = {}
			interface_map[source_switch][source_port] = dest_port
	return(switch_map,interface_map)


def build_output_files(switch_map,interface_map,input_dir,output_dir,template):
	all_vlans = {
		'1':'vlan-1-name',
		'2':'vlan-2-name',
		'3':'vlan-3-name',
		'4':'vlan-4-name',
		'6':'vlan-6-name',
		'8':'vlan-8-name',
		'10':'vlan-10-name',
		'12':'vlan-12-name',
		'14':'vlan-14-name',
		'16':'vlan-16-name',
		'18':'vlan-18-name',
		'20':'vlan-20-name',
		'22':'vlan-22-name',
		'23':'vlan-23-name',
		'24':'vlan-24-name',
		'25':'vlan-25-name',
		'26':'vlan-26-name',
		'28':'vlan-28-name',
		'30':'vlan-30-name',
		'32':'vlan-32-name',
		'34':'vlan-34-name',
		'36':'vlan-36-name',
		'38':'vlan-38-name',
		'40':'vlan-40-name',
		'44':'vlan-44-name',
		'50':'vlan-50-name',
		'52':'vlan-52-name',
		'54':'vlan-54-name',
		'58':'vlan-58-name',
		'60':'vlan-60-name',
		'62':'vlan-62-name',
		'64':'vlan-64-name',
		'66':'vlan-66-name',
		'70':'vlan-70-name',
		'74':'vlan-74-name',
		'76':'vlan-76-name',
		'80':'vlan-80-name',
		'90':'vlan-90-name',
		'96':'vlan-96-name',
		'100':'vlan-100-name',
		'102':'vlan-102-name',
		'103':'vlan-103-name',
		'104':'vlan-104-name',
		'106':'vlan-106-name',
		'108':'vlan-108-name',
		'110':'vlan-110-name',
		'198':'vlan-198-name',
		'201':'vlan-201-name',
		'202':'vlan-202-name',
		'203':'vlan-203-name',
		'204':'vlan-204-name',
		'205':'vlan-205-name',
		'208':'vlan-208-name',
		'214':'vlan-214-name',
		'221':'vlan-221-name',
		'224':'vlan-224-name',
		'250':'vlan-250-name',
		'305':'vlan-305-name',
		'307':'vlan-307-name',
		'317':'vlan-317-name',
		'330':'vlan-330-name',
		'342':'vlan-342-name',
		'502':'vlan-502-name',
		'505':'vlan-505-name',
		'506':'vlan-506-name',
		'666':'vlan-666-name',
		'990':'vlan-990-name',
		'996':'vlan-996-name',
		'997':'vlan-997-name',
		'998':'vlan-998-name',
		'999':'vlan-999-name',
		'1000':'vlan-1000-name',
		'1002':'vlan-1002-name',
		'1003':'vlan-1003-name',
		'1004':'vlan-1004-name',
		'1005':'vlan-1005-name',
		'2000':'vlan-2000-name',
		'2001':'vlan-2001-name',
		'2002':'vlan-2002-name'
	}

	switch_interface_map = {}
	switch_vlan_map = {}
	switch_stack_map = {}
	output_switches = []
	last_octet = 160
	for k,v in switch_map.items():
		# Make sure that our output switch exists in out output switches variable
		if v not in output_switches:
			output_switches.append(v)

		# Open our source configuration file and parse the configuration for future use
		s = open(input_dir + k + ".txt",'r')
		raw_config = s.readlines()
		parsed_config = CiscoConfParse(raw_config)
		s.close()

		# Build interface configuration for new switches and store in variable.

		# Loop for every source/destination port mapping in our source switch
		for source_port,dest_port in interface_map[k].items():
			# Pull the parsed configuration for the current specific source port
			config = parsed_config.find_children_w_parents("^interface " + source_port + "(\r|\n)*$",'.*')
			# Make sure our desination list exists for all output variables
			if v not in switch_interface_map.keys():
				switch_interface_map[v] = []
			if v not in switch_vlan_map.keys():
				switch_vlan_map[v] = []
			if v not in switch_stack_map.keys():
				switch_stack_map[v] = []
			if dest_port.split('/')[0][len(dest_port.split('/')[0])-1] not in switch_stack_map[v]:
				switch_stack_map[v].append(dest_port.split('/')[0][len(dest_port.split('/')[0])-1])
			# Add our interface line semi-manually
			switch_interface_map[v].append("interface " + dest_port + "\r\n")
			# Iterate through our parsed configuration and add relevant configurations to our list
			for line in config:
				if re.match("^ (switchport|speed|duplex|description|channel-group).*",line):
					switch_interface_map[v].append(line)
					match = re.match("^ switchport.*vlan ([0-9]*).*",line)
					if match:
						if match.group(1) not in switch_vlan_map[v]:
							switch_vlan_map[v].append(match.group(1))

	## We Start Building Here
	t = open(template,'r')
	template_config = t.readlines()
	t.close()

	for switch in output_switches:
		d = open(output_dir + switch + ".txt",'a')
		for template_line in template_config:
			if re.match("^<<< Hostname >>>",template_line):
				d.write("hostname " + switch + "\r\n")
			elif re.match("^<<< Provision Switches >>>",template_line):
				for member in sorted(switch_stack_map[switch]):
					d.write("switch " + member + " provision ws-c2960x-48lps-l\r\n")
			elif re.match("^<<< Required VLANS >>>",template_line):
				for vlan in sorted(switch_vlan_map[switch], key=int):
					d.write("Vlan " + vlan + "\r\n")
					if vlan in all_vlans.keys() and vlan != "1":
						d.write(" name " + all_vlans[vlan] + "\r\n")
			elif re.match("^<<< Interface Configurations >>>",template_line):
				for int_output in switch_interface_map[switch]:
					d.write(int_output)
			elif re.match("^<<< Management Interface >>>",template_line):
				d.write("interface Vlan1\r\n")
				d.write(" ip address 172.20.250." + str(last_octet) + " 255.255.255.0\r\n no shut\r\n")
				last_octet += 1
			elif re.match("^snmp-server chassis-id <<< Hostname >>>",template_line):
				d.write("snmp-server chassis-id " + switch + "\r\n")
			else:
				d.write(template_line)
		d.close()



def main():

	if len(sys.argv) < 4:
		print("\nScript Execution Halted - Not enough arguments provided\n\nUsage:  switch_process.py <path_to_config_files> <input_file_name> <output_directory>\n\n")
	else:
		if sys.argv[1].endswith('/'):
			input_path = sys.argv[1]
		else:
			input_path = sys.argv[1] + "/"
		if sys.argv[3].endswith('/'):
			output_path = sys.argv[3]
		else:
			output_path = sys.argv[3] + "/"

		switches,interfaces = build_mapping(sys.argv[2])
		build_output_files(switches,interfaces,input_path,output_path,sys.argv[4])


if __name__ == '__main__':
  main()

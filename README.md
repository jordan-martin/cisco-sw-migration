# cisco-sw-migration
A simple script I used to map old switches to new switches/switch stacks for a campus replacement. Not as efficient as it could be but it got the job done. 

***Name: switch_collect.py***
Description: This script collects all switches/ports and outputs them into a CSV file for manually defining the target ports on new switches

***Usage:  python switch_collect.py <path_to_config_files> <output_file_name>***

***Name: switch_process.py***
Description: This script imports the manually modified CSV of port mappings and converts that to the new configurations.

***Usage:  python switch_process.py <path_to_config_files> <input_file_name> <output_directory> <template_file>***

#!/usr/bin/python

import os
import subprocess
import sys
import argparse


def print_list(celllist, details, args):
	for cell in cells:
		for i in args.show:
			print_string = ""
			if not args.omit:
				print_string += details[i] + "\t"
				if i != "f":
					print_string += "\t"
			print(print_string + cell[details[i]])
		print("")


def print_table(celllist, details, args, maxlen):
	print_string = ""
	if not args.omit:
		celllist.insert(0, dict(Address="Address", ESSID="ESSID", Frequency="Frequency", Channel="Channel", Quality="Quality", Level="Level(dBm)"))

	for i in details.values():
		if maxlen[i] % 8 == 0:
			maxlen[i] += 1

	for cell in cells:
		for i in args.show:
			print_string += cell[details[i]]
			strlen = len(cell[details[i]])
			if strlen % 8 == 0:
				strlen += 1
			tabs = ((maxlen[details[i]] // 8 + 1) * 8 - strlen) // 8 + 1  # calculate the number of tabs for printing
			print_string += "\t" * tabs
		print_string += "\n"
	print(print_string)
	
def print_ssid(celllist, details, args):
	for cell in cells:
		print('<option>'+cell[details['e']]+'</option>')

def sorter(k):
	tuple = ()

	for i in args.sort_by:
		tuple += (k[details[i]],)

	return tuple

parser = argparse.ArgumentParser(description="Frontend for iwlist scan")
parser.add_argument("interface", help="Specify the interface (default: all)", metavar="iface", nargs='?', default='')
parser.add_argument("-s", "--show", help="Which details to show (default: all) and in which order", choices=['a', 'c', 'e', 'f', 'l', 'q'], nargs='+', default=['a', 'e', 'f', 'q', 'c', 'l'], metavar="details")
parser.add_argument("-b", "--sort-by", help="Sort by detail (default: none)", choices=['a', 'c', 'e', 'f', 'l', 'q'], nargs='+')
parser.add_argument("-f", "--find", help="Search for a detail", metavar=("detail", "search-string"), nargs=2)
parser.add_argument("-o", "--omit", help="Omit descriptions", action="store_true", default=False)
parser.add_argument("--output", help="Print output as list, table or ssid (ssid for ssid only for html option) (default: list)", choices=['list', 'table','ssid'], default="list")
parser.add_argument("--file", help="Interpret iface as file-input", action="store_true", default=False)
args = parser.parse_args()

if not args.file:
	cmd = ['iwlist']
	if args.interface:
		cmd.append(args.interface)
	cmd.append('scan')
else:
	cmd = ['cat', args.interface]
try:
	stream = subprocess.check_output(cmd, universal_newlines=True)
except subprocess.CalledProcessError as e:
	print("An error occured while calling %s" % (str(' ').join(cmd)))
	if e.output:
		print(e.output)
	sys.exit(e.returncode)
except Exception as e:
	print("An error occured while calling %s" % (str(' ').join(cmd)))
	print(e)
	sys.exit(1)
lines = stream.splitlines()
cells = list()
details = dict(a="Address", c="Channel", e="ESSID", f="Frequency", l="Level", q="Quality")
maxlen = dict(Address=17, Channel=3, ESSID=0, Frequency=9, Level=3, Quality=2)
sort = list()
address = ""

for line in lines:
	if line.find("Address") != -1:
		address = line.split()[-1]
		temp = dict()
		temp["Address"] = address
	elif line.find("Channel:") != -1:
		temp["Channel"] = line.split(":")[-1].rstrip()
	elif line.find("Frequency:") != -1:
		temp["Frequency"] = line.split()[0].split(":")[-1]
	elif line.find("Quality=") != -1:
		quallvl = line.split()
		temp["Quality"] = quallvl[0].split("=")[-1].split("/")[0]
		temp["Level"] = quallvl[2].split("=")[-1]
	elif line.find("ESSID") != -1:
		temp["ESSID"] = line.split(":")[-1].rstrip().strip("\"")
		if args.find:
			if temp[details[args.find[0]]].find(args.find[1]) == -1:
				continue
		if len(temp["ESSID"]) > maxlen["ESSID"]:
			maxlen["ESSID"] = len(temp["ESSID"])
		cells.append(temp)

if args.sort_by:
	cells = sorted(cells, key=sorter)

if len(cells) == 0:
	print("No cells found!")
else:
	if args.output == "list":
		print_list(cells, details, args)
	elif args.output == "table":
		print_table(cells, details, args, maxlen)
	elif args.output == "ssid":
		print_ssid(cells, details, args)

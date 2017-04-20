

def get_superlatives():
	f = open("lib/superlatives.txt", "r")
	sups_dict = {}
	line = f.readline()
	while line != "":
		sups = line.split(",")
		sups_dict[sups[0]] = sups[1].strip()
		line = f.readline()
	return sups_dict


def get_comparatives():
	f = open("lib/comparatives.txt", "r")
	comps_dict = {}
	line = f.readline()
	while line != "":
		comps = line.split(",")
		comps_dict[comps[0]] = comps[1].strip()
		line = f.readline()
	return comps_dict

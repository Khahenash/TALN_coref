#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import os
import glob
import codecs

"""
This program automatically find co-references between named entities previously annotated

example : python co-ref.py param
param : optional, 1 to only test equality, 2 to test equality and inclusion,
		3 to test equality, inclusion & acronyms (default)

Author : Carl Goubeau
"""

# co-references file generated
output_ref = "etudiant4.ref"
# threshold value for acronyms' length in equality test
sEq = 2
# threshold value for acronyms' length on inclusion test
sIn = 3
# data directory, this script will look for every .txt file in this directory
rep = "ne"



def getEnt(entity):
	"""
	get the entity name
	for "<EN>entity</EN>" returns "entity"
	"""
	# find out the value of <'EN'>
	regexp2 = re.search("</[A-Z]+>", entity)
	EN = regexp2.group(0)
	EN = EN.replace("</", "")
	EN = EN.replace(">", "")
	return EN

def getValue(entity):
	"""
	get the entity type
	for "<EN>entity</EN>" returns "EN"
	"""
	EN = getEnt(entity)
	# get the entity value
	newEntity = entity[len(EN)+2:len(entity)-len(EN)-3]
	#print newEntity + " (type: "+ EN +") "
	return newEntity

def sigles(e):
	"""
	get capital characters in e to build an acronym
	for "<EN>United States of America</EN>" returns "USA"
	"""
	sigle = ""
	regexp3 = re.compile("[A-Z]")
	for maj in regexp3.findall(getValue(e)):
		sigle = sigle + maj
	return sigle

def sigleTest(e1, e2):
	"""
	test if there is a match between the acronyms
	"""
	if((sigles(e1)==sigles(e2)) and (len(sigles(e1))>=sEq)):
		return True
	else:
		if( (len(sigles(e1))>=sIn and len(sigles(e2)) >=sIn) and ((sigles(e1) in sigles(e2)) or (sigles(e2) in sigles(e1))) ) :
			return True
	return False

def writeRef(d, f):
	"""
	write in 'output_ref' co-references found in the file 'f'
	"""
	output_file = codecs.open(output_ref, "a", "utf-8")
	output_file.write(os.path.basename(f)+"\t")
	firstV = True
	for v in d:
		if not firstV:
			output_file.write(";")
		else:
			firstV = False
		firstI = True
		for i in v:
			if not firstI:
				output_file.write(",")
			else:
				firstI = False
			output_file.write(str(i))
			
	output_file.write("\n")
	output_file.close()

def includeTest(w, e, v, i):
	test = False
	for ent in e:
		if (((getValue(w).lower() in ent.lower())or(getValue(ent).lower() in w.lower()))and (getEnt(ent)==getEnt(w))):
			v[e.index(ent)].append(i)
			test = True
			break
	if not test:
		e.append(w)
		v.append([i])

def include_sigle_Test(w, e, v, i):
	test = False
	for ent in e:
		if ((((getValue(w).lower() in ent.lower())or(getValue(ent).lower() in w.lower()))and (getEnt(ent)==getEnt(w))) or (sigleTest(ent, w))):
			v[e.index(ent)].append(i)
			test = True
			break
	if not test:
		e.append(w)
		v.append([i])


#############################################
#############################################


def baseline(f):
	"""
	this function combines entities if they are equal
	"""
	input_file = codecs.open(f, "r", "utf-8")
	text = input_file.read()
	input_file.close()

	entities = []
	values = []
	index = 1
	regexp = re.compile("<[A-Z]+>[\w\.\,\s\-/'()]+</[A-Z]+>")
	for entity in regexp.findall(text):
		# entity : <EN>text</EN>
		if (entity in entities):
			values[entities.index(entity)].append(index)
		else:
			entities.append(entity)
			values.append([index])
		index = index + 1

	writeRef(values, f)


def inclusion(txtfile):
	"""
	this funcion combines entities if :
		- they are equal
		- an entity is uncluded in another
	"""
	input_file = codecs.open(txtfile, "r", "utf-8")
	text = input_file.read()
	input_file.close()

	entities = []
	values = []
	index = 1
	regexp = re.compile("<[A-Z]+>[\w\.\,\s\-/'()]+</[A-Z]+>")
	for entity in regexp.findall(text):
		# entity : <EN>text</EN>
		if (entity in entities):
			values[entities.index(entity)].append(index)
		else:
			includeTest(entity, entities, values, index)
		index = index + 1

	writeRef(values, txtfile)


def acronyms(txtfile):
	"""
	this funcion combines entities if :
		- they are equal
		- an entity is uncluded in another
		- an entity is an acronym of another
	"""
	input_file = codecs.open(txtfile, "r", "utf-8")
	text = input_file.read()
	input_file.close()

	entities = []
	values = []
	index = 1
	regexp = re.compile("<[A-Z]+>[\w\.\,\s\-/'()]+</[A-Z]+>")
	for entity in regexp.findall(text):
		# entity : <EN>text</EN>
		if (entity in entities):
			values[entities.index(entity)].append(index)
		else:
			include_sigle_Test(entity, entities, values, index)
		index = index + 1

	writeRef(values, txtfile)


def numericalSort(value):
    numbers = re.compile(r'(\d+)')
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

#############################################
############# script python #################
#############################################

# ref file already exists ?
if os.path.isfile(output_ref):
	a = raw_input(output_ref + " already exists :\n\t1. choose another file name\n\t2. remplace existing file\n")
	if a == "1":
		output_ref = raw_input("new file name ? ")
		while(True):
			if os.path.isfile(output_ref):
				print "this file already exists"
				output_ref = raw_input("new file name ? ")
			else:
				break
	elif a == "2":
		os.remove(output_ref)
		print output_ref + " deleted"
	else:	
		sys.exit("script execution interrupted")

# data directory exists ?
if not os.path.isdir(rep):
	sys.exit("data directory '" + rep + "' not found\n-> set another name is this script l.26 or rename your data directory")

# function selection
print "================================================="
fi = glob.iglob(rep+'/*.txt')
fi = sorted(fi, key=numericalSort)
if(len(sys.argv)>=2):
	if(sys.argv[1]=="1"):
		print "co-references: equality"
		for f in fi:
			baseline(f)
	elif(sys.argv[1]=="2"):
		print "co-references: equality, inclusion"
		for f in fi:
			inclusion(f)
	else:
		print "co-references: equality, inclusion, acronyms"
		for f in fi:
			acronyms(f)
else:
	print "co-references: equality, inclusion, acronyms"
	for f in fi:
		acronyms(f)

print len(fi), "files processed"
print output_ref + " generated"



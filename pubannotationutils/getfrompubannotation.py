#####################################################
# getFromPubAnnotation file for Snorkel				#
# This program will allow a file to be passed  		#
# with PMIDs and PubAnnotation project(s) to be		#
# exported into a Snorkel compatible data tables	#
# to potentially (or in our case) to be treated as  #
# gold-labels (as they have been curated by others).#
# these tables can be then used for label generation#
# or any other usages 								#
#####################################################
import json
import sys
import string
import csv
from urllib2 import urlopen

def get_jsonparsed_data(url):
	response = urlopen(url)
	data = response.read() #.decode("utf-8")
	return json.loads(data)

def getCorpusPubAnnotation(fileWI):
	### Read CSV file with list of documents/annotation project to pull from PubAnnotation
	inputFile=fileWI
	outFileDeno = open(inputFile[:-4] + "_denotations.txt", "w")
	outFileRela = open(inputFile[:-4] + "_relations.txt", "w")
	outFileText = open(inputFile[:-4] + "_text.txt", "w")
	f = open(inputFile, 'rb') # opens the csv file
	try:
		reader = csv.reader(f)  # creates the reader object
		for row in reader:   # iterates the rows of the file in orders
			project = row[1] 
			PMID = str(row[0])
			url = ("http://pubannotation.org/projects/"+project+"/docs/sourcedb/PubMed/sourceid/"+PMID+"/annotations.json")
			annotation = get_jsonparsed_data(url)
			##print annotation
			## This part generates the denotations - they should be inserted as they appear
			## Pull text stuff
			textTO= annotation["text"].encode('utf-8')
			textTO = string.replace(textTO, '\r\n', '\\n')
			textTO = string.replace(textTO, '\n', '\\n')
			outFileText.write(PMID + "\t"  + textTO + "\n")
			##
			denoSpans = {} #this is a hacky version of getting the spans in a key,value pair for quick search
			for k in annotation["denotations"]:
				strID=k["id"]  #
				onto, code = k["obj"].split(":") #get me the annotation_source and the ID
				it=0
				spanV=[]
				for kp,v in k["span"].iteritems():
					spanV.append(v)
					beginSpan=spanV
					endSpan=spanV
				### This could be fully outputed into Snorkel, but that will come later
				#print(PMID + "\t" + strID + "\t" + onto + "\t" + code + "\t" + str(spanV[0]) + "\t" + str(spanV[1]))
				outFileDeno.write(PMID + "\t" + strID + "\t" + onto + "\t" + code + "\t" + str(spanV[0]) + "\t" + str(spanV[1])+"\n")
				denoSpans[strID]=str(spanV[0]) + "," + str(spanV[1])
			## This part gets the relations and formats them the proper way
			for kp in annotation["relations"]:
				for idV, spanVal  in denoSpans.items():
					if kp["subj"] == idV:
						sp1, sp2 = spanVal.split(",")
						outPtVal = PMID + "::span:" + sp1 + ":" + sp2 + "\t"
						for idV2, spanVal2  in denoSpans.items():
							if kp["obj"] == idV2:
								sp12, sp22 = spanVal2.split(",")
								outPtVal_F = outPtVal+ PMID + "::span:" + sp12 + ":" + sp22
				### This should be fully outputed into Snorkel, but that will come later
				outFileRela.write(outPtVal_F + "\t" + kp["subj"] + "\t" + kp["obj"] + "\n")
	finally:
		f.close()	#closing
		outFileDeno.close()
		outFileRela.close()
		outFileText.close()
	return 0
#sys.argv[1]
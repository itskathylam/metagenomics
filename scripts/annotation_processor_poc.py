#!/usr/bin/python
import time
import os.path
import os
from os import system
import datetime
import csv
import sys
from mainsite.models import Contig, ORF, Contig_ORF_Join


#read csv file into array of arrays
def read_csv(file_location):
    import csv
    with open(file_location, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter = ',')
        rows = []
        for row in reader:
            rows.append(row)
    csvfile.closed
    #system("rm %s" %file_location)
    return rows          


def run():

    objects = ORF.objects.all()
    print objects
    
    old_dir = os.getcwd()
    print old_dir

    #read the results from the Perl script to add/update new contig-orf joins into the database
    results = read_csv("annotations-kathy.csv")
    new_contigs = []
    for row in results:
        contig1 = Contig.objects.all()
        orf1 = ORF.objects.all()
        Contig_ORF_Join.objects.create(
                                    contig = contig1[0],
                                    orf = orf1[0],
                                    start = row[6],
                                    stop = row[7],
                                    complement =  1 if row[8] < 0 else 0,
                                    orf_accession = None,
                                    predicted = 1,
                                    prediction_score = row[9],
                                )
    
    #message containing success or failure message
    message = ""
    if new_contigs == None:
        message = """Your job has finished running on metagenomics.uwaterloo.ca.
                        The job was unsuccessful."""
    else:      
        message = """Your job has finished running on metagenomics.uwaterloo.ca.
                        The following contigs now have annotations:
                    """ 
    
    print message
    #call mail function and send message to input email
    system("(echo message;)")
 



  

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
    system("rm %s" %file_location)
    return rows          

def run():
    
    #the file is not initially there
    no_file = True
    while no_file:
        print 0
        #if the file is created; process it and write to db
        if os.path.isfile('annotations.csv'):
            
            #remove the logging file
            system("rm test.txt")
            
            ##save the annotation images for each contig, created by the script
            #save_images("tool")
            
            #read the results from the Perl script to add/update new contig-orf joins into the database
            results = read_csv("annotations.csv")
            new_contigs = []
            #for row in results:
            for i in range(0,10):    
                contigs = Contig.objects.all()
                orfs = ORF.objects.all()
                #contig = Contig.objects.filter(contig_name = row[0])
                #new_contigs.append(row[0])
                #for obj in ORF.objects.all():
                #    if row[2] == obj.orf_sequence:
                #        new_orf = obj
                #    else:
                #        new_orf = ORF.objects.create(orf_sequence = row[2], annotation = row[5])
                        
                Contig_ORF_Join.objects.create(
                                            contig = contigs[i],
                                            orf = orfs[i],
                                            start = 1,
                                            stop = 100,
                                            complement =  1,
                                            orf_accession = None,
                                            predicted = 1,
                                            prediction_score = 1,
                                        )
            
            #message containing success or failure message
            message = ""
            if new_contigs == None:
                message = """Your job has finished running on metagenomics.uwaterloo.ca.
                                The job was unsuccessful."""
            else:      
                message = """Your job has finished running on metagenomics.uwaterloo.ca.
                                The following contigs now have annotations:
                                    %s
                            """ #%(new_contigs)
            
            #call mail function and send message to input email
            system("(echo message;)") # | mail -s '[Metagenomics]Annotation Tool Processing Complete' " + email)
                        
            #file was made, exit while loop
            no_file = False
            
        #file is not there; write the time in a log
        else:
            with open("test.txt", "a") as myfile:
                dt = str(datetime.datetime.now()) + "\n"
                myfile.write(dt)
                time.sleep(1)
                

#experimenting with time.sleep
'''
def AnnoationProcessor():
    while True:
        if os.path.isfile('check_file'):
            print "yes"
            break
        else:
            print "no"
            time.sleep(1)

AnnoationProcessor()
'''






















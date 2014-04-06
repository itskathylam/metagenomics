#!/usr/bin/python
import time
import os.path
import os
import datetime
import csv
import sys
import re
import base64
from os import system, listdir
from re import match
from mainsite.models import Contig, ORF, Contig_ORF_Join

#gets all the pictures generated from the Perl script and saves them to the appropriate contigs in the database
def save_images(folder):
    re_contigname = re.compile('^(.+)-(ALIGN|CONTIG|GLIM|GENBANK|MANUAL)\.png$')
    for file in listdir('annotation_tool/%s/img/' %folder):
        with open("annotation_tool/%s/img/" %folder + file,  "rb") as img:
            imgbinary = base64.b64encode(img.read())
        
        filename = re_contigname.match(file)
        
        imgcontigname = filename.group(1)
        contig = Contig.objects.get(contig_name=imgcontigname)
          
        if filename.group(2) == 'ALIGN':
            contig.image_align = imgbinary
        elif filename.group(2) == 'CONTIG':
            contig.image_contig = imgbinary
        elif filename.group(2) == 'GLIM':
            contig.image_predicted = imgbinary
        elif filename.group(2) == 'GENBANK':
            contig.image_genbank = imgbinary
        elif filename.group(2) =='MANUAL':
            contig.image_manual = imgbinary
        else:
            #ERROR CATCHING THERE IS A PNG WITH NO MATCH???
            pass
        contig.save()


def run():
    
    #the file is not initially there
    no_file = True
    while no_file:
        
        #if the file is created; process it and write to db
        if os.path.isfile('annotation_tool/tool/out/annotations.csv'):
            
            
            #read the results from the Perl script to add/update new contig-orf joins into the database
            with open("annotation_tool/tool/out/annotations.csv", 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter = ',')
                rows = []
                for row in reader:
                    rows.append(row)
            csvfile.closed
            #system("rm annotation_tool/tool/out/annotations.csv")
            results = rows
            
            
            #save the annotation images for each contig, created by the script
            save_images("tool")
            
            new_contigs = []
            for row in results:
                #use get not filter to get an instance rather than a queryset of one instance
                contig = Contig.objects.get(contig_name = row[0])
                new_contigs.append(str(contig.contig_name))
                #check if orf_seq already present in orf table
                orf_db_check = 0
                orf_to_use = None 
                orfs = ORF.objects.all()
                for orf_object in orfs:
                    if orf_object.orf_sequence == row[4]:
                        orf_db_check = 1
                        orf_to_use = orf_object
                        
                #if an orf with same sequence found in the database, use that orf instance
                if orf_db_check == 1:    
                    new_orf = orf_to_use
               
                #otherwise, make a new orf instance to use
                else:
                    #new_orf.orf_sequence = orf_seq
                    new_orf = ORF.objects.create(orf_sequence = row[4], annotation = row[5])
                

                Contig_ORF_Join.objects.create(
                                            contig = contig,
                                            orf = new_orf,
                                            start = int(row[6]),
                                            stop = int(row[7]),
                                            complement =  1 if int(row[8]) < 0 else 0,
                                            orf_accession = None,
                                            predicted = 1,
                                            prediction_score = float(row[9]),            
                                            )
            #get input email from command line 
            email = sys.argv[3]
            new_contigs = set(new_contigs)
            new_contigs = list(new_contigs)
            #message containing success or failure message
            message = ""
            if len(new_contigs) == 0:
                message = "Your job has finished running on metagenomics.uwaterloo.ca.  The job was unsuccessful."
            else:      
                message = "Your job has finished running on metagenomics.uwaterloo.ca.  The following contigs now have annotations: %s." %(new_contigs)
            
            #call mail function and send message to input email
            system("(echo %s" %message + ";) | mail -s '[Metagenomics]Annotation Tool Processing Complete' " + email)
            
            #file was made, exit while loop
            no_file = False





















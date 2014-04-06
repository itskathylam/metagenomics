#!/usr/bin/python
import time
import os.path

#required for Python to know about mainsite settings (can make it permanent)
system("export DJANGO_SETTINGS_MODULE=metagenomics.settings")

def AnnoationProcessor():
    while True:
        if os.path.isfile('check_file'):
            print "yes"
            break
        else:
            with open("test.txt", "a") as myfile
            myfile.write("no\n")
            time.sleep(1)

AnnoationProcessor()












'''
from mainsite.models import Contig, ORF, Contig_ORF_Join

#save the annotation images for each contig, created by the script
save_images("tool")

#read the results from the Perl script to add/update new contig-orf joins into the database
results = read_csv("annotation_tool/tool/out/annotations.csv")
new_contigs
for row in results:
    contig = Contig.objects.filter(contig_name = row[0])
    new_contigs.append(row[0])
    for obj in ORF.objects.all():
        if row[2] == obj.orf_sequence:
            new_orf = obj
        else:
            new_orf = ORF.objects.create(orf_sequence = row[2], annotation = row[5])
            
    Contig_ORF_Join.objects.create(
                                contig = contig,
                                orf = new_orf,
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
                        %s
                """ %(new_contigs)

#call mail function and send message to input email
system("(echo message;) | mail -s '[Metagenomics]Annotation Tool Processing Complete' " + email)

'''







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



from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger
from django.core.files import File
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q

from mainsite.models import *
from mainsite.forms import *

from Bio.Blast.Applications import NcbiblastnCommandline
from Bio.Blast import NCBIXML
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Alphabet import generic_dna
from Bio.SeqRecord import SeqRecord

import types
import StringIO
import os
from os import system, listdir
import pdb
import base64
from operator import attrgetter
import operator
import re
import base64 #used to convert pngs to base64 for database storage
from re import match
import csv

#Main, About etc

@login_required
def MainPage(request):
    template_name = 'index.html'
    return (render(request, 'index.html'))

@login_required
def AboutPage(request):
    template_name = 'about.html'
    return (render(request, 'about.html'))

def Logout(request):
    logout(request)
    return HttpResponseRedirect('/login')

@login_required
def UserSettings(request):
    form_errors = {}
    
    if request.method == "POST":
        user_form = UserForm(request.POST, instance = request.user)
        if user_form.is_valid():
            user_form.save()
            return HttpResponseRedirect('/')
        else:
            form = UserForm(initial={'first_name': request.user.first_name, 'last_name': request.user.last_name, 'username': request.user.username, 'email': request.user.email})
            form_errors['invalid'] = "Error on form."
    else:
        form = UserForm(initial={'first_name': request.user.first_name, 'last_name': request.user.last_name, 'username': request.user.username, 'email': request.user.email})
    return render_to_response('usersettings.html', {'form': form, 'form_errors': form_errors}, context_instance=RequestContext(request))

@login_required
def Faq(request):
    return (render(request, 'faq.html'))

@login_required
def UserDoc(request):
    return (render(request, 'userdoc.html'))

#annotation form for contig-orf retrieval
@login_required
def AnnotationTool(request):
    
    #track errors with dict
    form_errors = {}
    
    email_form = EmailForm()
    all_contigs = Contig.objects.all()
    testpicture = ''
    #after submit collect email and contig selection
    if request.method == "POST":
        if 'submit' in request.POST:

            email = request.POST['email']
            con_name = request.POST.getlist('contig')
            contigs = Contig.objects.filter(contig_name__in = con_name).values('contig_name')
            
            #check the number of contigs selected
            length = len(con_name)
            max_length = 20 #set arbitrary number for now since we are not sure of what sharcnet is capcable of 
            if length > max_length:
                form_errors['error'] = "Error: " + str(length) + " contigs chosen. Please select " + str(max_length) + " or fewer."
            
            #process if number of contigs chosen is less than the max allowed 
            else:
                #retrieve data and write the library file for selected contigs 
                orf_data(contigs)
                contigs = Contig.objects.filter(contig_name__in = con_name)
                #redirect to success page 
                AnnotationToolResults(contigs, email)         
                
    return render_to_response('tool_annotation.html', {'email_form': email_form, 'all_contigs': all_contigs}, context_instance=RequestContext(request))
    
#annotation tool success page, displays the contigs selected and the email the results will send to
def AnnotationToolResults(contigs, email):
    #call the annotations Perl script, will utilize the library file created on annotation tool page
    system("touch kathy")
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
    
    return render_to_response('tool_annotation_submit_message.html', {'contigs': contigs, 'email':email})

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

#contig tool, retrieves new contigs for cosmids in the pool
@login_required
def ContigTool(request):
    context = {'pool':Pooled_Sequencing.objects.all()}
    #display details for the selected pool 
    if request.method == "POST":
        if 'detail' in request.POST:
            pool_id =  request.POST['pool']            
            pool = Pooled_Sequencing.objects.all()
            details = Pooled_Sequencing.objects.filter(id = pool_id)
            cosmids = Cosmid.objects.filter(pool = pool_id)
            filter_cos = []
            for contig in Contig.objects.all():
                for cosmid in contig.cosmid.all():
                    filter_cos.append(cosmid)
            
            joined = []
            notjoined = []
            for cosmid in cosmids:
                if cosmid in filter_cos:
                    joined.append(cosmid)
                else:
                    notjoined.append(cosmid)
            context = {'poolselect': int(pool_id), 'pool': pool, 'detail': details, 'joined': joined, 'notjoined': notjoined} #'cosmids': cosmids, 'filtered': filter_cos, - used to test this relationship in the template
        
        #contigs selected are sent through the pipeline to call perl script
        #returns list of list of the results of the script for display 
        if 'submit' in request.POST:
            pool = request.POST['poolhidden']
            cos = request.POST.getlist('cos')
            cos_selected = Cosmid.objects.filter(cosmid_name__in = cos).values("cosmid_name")
            results = contig_pipeline(pool, cos_selected)
            entries = []
            for row in results:
                #cosmid name, strand location, contig name
                entry = row[0:3]
                #percent identity
                entry.append(row[5])
                #end tag length
                entry.append(row[7])
                #contig length
                entry.append(row[12])
                #match type
                entry.append(row[13])
                entries.append(entry)
            #send to submit page for contig selection 
            var = RequestContext(request, {'results': entries})
            return render_to_response('tool_contig_submit.html', var)
                
    variables = RequestContext(request, context)
    return render_to_response('tool_contig.html', variables)

#displays results of contig retrieval for selection into the database
@login_required
def ContigToolResults(request):
    joins = {}
    if request.method == 'POST':
        if 'submit' in request.POST:
            cosmidcontigs = request.POST.getlist('select')
    
            pattern = re.compile(r'^(.+)<\$\$>(.+)$')
    
            for pair in cosmidcontigs:
                match = pattern.match(pair)
                joins[match.group(1)] = match.group(2)
            
            cosmids = []
            for cos, con in joins.items():
                cosmid = Cosmid.objects.get(cosmid_name=cos)
                contig = Contig.objects.get(contig_name=con.lstrip())
                
                contig.cosmid.add(cosmid)
                cosmids.append(cos)
            
            return HttpResponseRedirect('/results/basic/cosmid?query=' + ' '.join(cosmids))
    
    return render_to_response('tool_contig_submit.html', {'results': joins}, context_instance=RequestContext(request))

#this function is only called by other views, not directly associated with a URL
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

#this function is only called by other views, not directly associated with a URL
#creates fasta and csv files for the contig retrieval perl script to run
#returns the results of the script in array
def contig_pipeline(pool, cos_selected):
    contigs = Contig.objects.filter(pool = pool).values_list('contig_name', 'contig_sequence')
    c_id =  Cosmid.objects.filter(cosmid_name__in = cos_selected).values('id')
    seqs = End_Tag.objects.filter(cosmid = c_id).select_related('cosmid__primer')
    
    write_fasta(contigs)
    write_csv(seqs)
    system("perl contig_retrieval_tool/retrieval_pipeline.pl primers_1.csv primers_2.csv contigs.fa")
    return read_csv("contig_retrieval_tool/tmp/out/retrieval.csv")

#this function is only called by other views, not directly associated with a URL
#writes a csv file for the input sequences 
def write_csv(seqs):
    with open("contig_retrieval_tool/primers_1.csv" , 'w') as f1:
        csv1 = File(f1)
        for entry in seqs:
            cos = entry.cosmid.cosmid_name
            primer = entry.primer.primer_name
            seq = entry.end_tag_sequence.strip()
            if entry.primer.direction == 'F':
                csv1.write(cos + ',' + primer + ',' + seq + '\n')
    csv1.closed
    f1.closed
    
    with open("contig_retrieval_tool/primers_2.csv" , 'w') as f2:
        csv2 = File(f2)
        for entry in seqs:
            cos = entry.cosmid.cosmid_name
            primer = entry.primer.primer_name
            seq = entry.end_tag_sequence.strip()
            if entry.primer.direction == 'R':
                csv2.write(cos + ',' + primer + ',' + seq + '\n')
    csv2.closed
    f2.closed

#this function is only called by other views, not directly associated with a URL
#writes contigs to fasta file(text.fa)    
def write_fasta(contigs):
    with open('contig_retrieval_tool/contigs.fa', 'w') as f:
        fasta = File(f)
        contigs = list(contigs)
        for contig, seq in contigs:
            fasta.write('>' + contig + '\n' + seq + '\n')
        fasta.closed
        f.closed

#retieve data to write to library file for annotations tool to run 
def orf_data(contig_list):
    contig_id = Contig.objects.filter(contig_name__in = contig_list).values('id')
    contigs = Contig.objects.filter(contig_name__in = contig_list).values_list('id','contig_name', 'contig_sequence', 'blast_hit_accession')
    orfs = Contig_ORF_Join.objects.filter(contig__in = contig_id).values_list('contig','orf','start', 'stop', 'complement', 'prediction_score')
    anno = ORF.objects.filter(contig__in = contig_id).values_list('id','annotation', 'orf_sequence')
    
    write_lib(contigs, orfs, anno)


#this function is only called by other views, not directly associated with a URL
def write_lib(contigs, orfs, anno):
    with open("annotation_tool/data.lib", 'w') as f:
        data = File(f)
        data.write('#!/usr/bin/perl \n sub data{\n')
        for c_id, name, seq, access in contigs:
            contig = name
            sequence = seq
            accession = access if access != None else ''
            data.write('$contig_orf{' + contig + '}\n = [\'' + sequence + '\',\n')
            data.write('{\'glimmer\' => {},\n')
            data.write('\'genbank\' => {},\n')
            data.write('\'manual\' =>{')
            count = 0
            for con_id, orf_id, start, stop, comp, score in orfs:
                for o_id, ann, seqs in anno:
                    if c_id == con_id and o_id == orf_id:
                        count += 1
                        comp = -1 if comp == 1 else 1
                        data.write('\'' + contig + '-' + str(count) + '\' => \n { start =>' + str(start) + ',\n end =>' + str(stop) + ',\n')
                        data.write('reading_frame =>' + str(comp) + ',\n score =>\'' + str(score) + '\',\n')
                        annotation = ann if ann != None else ''
                        data.write('annotation=>\'' + annotation + '\',\n sequence =>\'' + seqs + '\'\n},')
            data.write('}},\'' + accession + '\'];\n')
        data.write('return(\%contig_orf);} \n1;')
        data.closed
    f.closed


#sequence search
@login_required
def BlastSearch(request):
    blastform = BlastForm()
    return render_to_response('blast_search.html', {'blastform': blastform}, context_instance=RequestContext(request))

@login_required
def BlastResults(request):

    #change directory to blast_tool
    old_dir = os.getcwd()
    new_dir = old_dir + '/blast_tool/'
    os.chdir(new_dir)
    
    #get parameters, and write to file
    e = request.POST.get('expect_threshold')
    w = request.POST.get('word_size')
    ma = request.POST.get('match_score')
    mi = request.POST.get('mismatch_score')
    go = request.POST.get('gap_open_penalty')
    ge = request.POST.get('gap_extension_penalty')
    
    #get query sequence, clean of whitespace, and write
    seq = request.POST.get('sequence')
    seq = ''.join(seq.split())
    queryseq = SeqRecord(Seq(seq, generic_dna), id="query")
    queryfh = open("blast_query.fa", "w")
    SeqIO.write(queryseq, queryfh, "fasta") 
    queryfh.close()

    #prepare file to write sequences into - for making blast db
    out = open("blast_db.fa", "w")
    
    #get the url from which redirect occurred; determines what sequences are written in the blast db fasta file
    #possibilities: '/search/blast/', '/search/cosmid/', '/search/contig/', '/search/orf/', '/search/subclone/'
    url = request.GET.get('from')
    
    #get contig sequences; use contig name as descriptor line for fasta file
    if (url == '/search/blast/') or (url == '/search/cosmid/') or (url == '/search/contig/'):
        contigs = Contig.objects.all()
        for contig in contigs:
            contig.contig_sequence = contig.contig_sequence.strip()
            seqrecord = SeqRecord(Seq(contig.contig_sequence, generic_dna), id=contig.contig_name)
            SeqIO.write(seqrecord, out, "fasta")
    
    #get orf sequences; use orf_id as descriptor line for fasta file 
    if (url == '/search/blast/') or (url == '/search/cosmid/') or (url == '/search/orf/')or (url == '/search/subclone/'):        
        orfs = ORF.objects.all()
        for orf in orfs:
            orf.orf_sequence = orf.orf_sequence.strip()
            seqrecord = SeqRecord(Seq(orf.orf_sequence, generic_dna), id='ORF_' + str(orf.id))
            SeqIO.write(seqrecord, out, "fasta")
            
    #get end-tag sequences; use (cosmid_name + primer_name) as descriptor line for fasta file
    if (url == '/search/blast/') or (url == '/search/cosmid/'): 
        end_tags = End_Tag.objects.all().select_related('cosmid__primer')
        for end_tag in end_tags:
            end_tag.end_tag_sequence = end_tag.end_tag_sequence.strip()
            seqrecord = SeqRecord(Seq(end_tag.end_tag_sequence, generic_dna), id=end_tag.cosmid.cosmid_name + "_" + end_tag.primer.primer_name)
            SeqIO.write(seqrecord, out, "fasta")
            
    out.close()
    
    #makeblastdb to create BLAST database of files from fastafile
    system("makeblastdb -in blast_db.fa -out blast_db.db -dbtype nucl")

    #run blast command with query, parameters, and created database
    cmd = NcbiblastnCommandline(query="blast_query.fa", db="blast_db.db", evalue=float(e), word_size=int(w), reward=int(ma), penalty=int(mi), gapopen=int(go), gapextend=int(ge), outfmt=5, out="blast_results.xml")
    system(str(cmd))
    
    #parse xml file
    try:
        resultsfh = open("blast_results.xml")
        records = NCBIXML.parse(resultsfh)
        test = records.next()
    except Exception:
        results_list = 0
        seq = ""
    else:
        results_list = []
        for alignment in test.alignments:
            list_title = alignment.title.split(' ')
            title = list_title[1]
            length = alignment.length
            for hsp in alignment.hsps:
                result = {}
                align_length = hsp.align_length
                evalue = hsp.expect
                hsp_query = hsp.query
                hsp_match = hsp.match
                hsp_subject = hsp.sbjct
                query_start = hsp.query_start
                subject_start = hsp.sbjct_start
                result['title'] = title
                result['length'] = length
                result['align_length'] = align_length
                result['evalue'] = evalue
                result['query_start'] = query_start
                result['subject_start'] = subject_start
                result['query_end'] = query_start + align_length
                result['subject_end'] = subject_start + align_length
                result['hsp_query'] = hsp_query
                result['hsp_match'] = hsp_match
                result['hsp_subject'] = hsp_subject
                result['hsp'] = hsp
                results_list.append(result)
    
    #change directory back to old dir
    os.chdir(old_dir)
            
    return render_to_response('blast_results.html', {'results_list': results_list, 'query': seq}, context_instance=RequestContext(request))

#search forms
def CosmidSearchView(request):
    form = CosmidForm
    basicform = AllSearchForm
    blast_form = BlastForm
    return render_to_response('cosmid_search.html', {'advancedform': form, 'basicform': basicform, 'blast_form':blast_form}, context_instance=RequestContext(request))

def SubcloneSearchView(request):
    form = SubcloneForm
    basicform = AllSearchForm
    blast_form = BlastForm
    return render_to_response('subclone_search.html', {'advancedform': form, 'basicform': basicform, 'blast_form':blast_form}, context_instance=RequestContext(request))

def SubcloneAssaySearchView(request):
    form = SubcloneAssayForm
    basicform = AllSearchForm
    return render_to_response('subclone_assay_search.html', {'advancedform': form, 'basicform': basicform}, context_instance=RequestContext(request))

def CosmidAssaySearchView(request):
    form = CosmidAssayForm
    basicform = AllSearchForm
    return render_to_response('cosmid_assay_search.html', {'advancedform': form, 'basicform': basicform}, context_instance=RequestContext(request))

def OrfSearchView(request):
    form = OrfSearchForm
    basicform = AllSearchForm
    blast_form = BlastForm
    return render_to_response('orf_search.html', {'advancedform': form, 'basicform': basicform, 'blast_form':blast_form}, context_instance=RequestContext(request))

def ContigSearchView(request):
    form = ContigSearchForm
    basicform = AllSearchForm
    blast_form = BlastForm
    return render_to_response('contig_search.html', {'advancedform': form, 'basicform': basicform, 'blast_form':blast_form}, context_instance=RequestContext(request))

#can delete this view
#def SearchAll(request):
#    form = AllSearchForm
#    return render_to_response('all_search.html', {'form': form}, context_instance=RequestContext(request))

#search result views
@login_required
def CosmidResults(request):
    cosmid_name = request.GET.get('cosmid_name')
    host = request.GET.get('host')
    researcher= request.GET.get('researcher')
    library = request.GET.get('library')
    screen = request.GET.get('screen')
    ec_collection = request.GET.get('ec_collection')
    original_media = request.GET.get('original_media')
    pool = request.GET.get('pool')
    lab_book_ref = request.GET.get('lab_book_ref')
    comments = request.GET.get('cosmid_comments')
    values = { 'cosmid_name__icontains' : cosmid_name, 'host': host, 'researcher' : researcher, 'library': library, 'screen': screen, 'ec_collection__icontains': ec_collection, 'original_media__icontains': original_media, 'pool': pool, 'lab_book_ref__icontains': lab_book_ref, 'comments__icontains': comments}
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    qargs = {}
    for k, v in values.items():
        if v != '':
            qargs[k] = v
    if any(qargs):
        results = Cosmid.objects.filter(**qargs).order_by(order_by)
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 1
        try:
            cosmid_list = p.page(page)
        except PageNotAnInteger:
            cosmid_list = p.page(1)
    else:
        results = None
        cosmid_list = results
        search = ''
        total = None
    
    return render_to_response('cosmid_end_tag_all.html', {'cosmid_list': cosmid_list, 'queries':queries, 'search':search, 'total':total, 'order_by':order_by}, context_instance=RequestContext(request))

@login_required
def SubcloneResults(request):
    name = request.GET.get('subclone_name')
    cosmid = request.GET.get('cosmid')
    orf = request.GET.get('orf')
    vector = request.GET.get('vector')
    researcher = request.GET.get('researcher')
    ec_collection = request.GET.get('ec_collection')
    
    values = {'subclone_name__icontains' : name, 'cosmid': cosmid, 'researcher' : researcher, 'orf': orf, 'vector': vector, 'researcher': researcher, 'ec_collection__icontains': ec_collection}
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    qargs = {}
    for k, v in values.items():
        if v != '':
            qargs[k] = v
    if any(qargs):
        results = Subclone.objects.filter(**qargs).order_by(order_by)
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 1
        try:
            subclone_list = p.page(page)
        except PageNotAnInteger:
            subclone_list = p.page(1)
    else:
        results = None
        subclone_list = results
        search = ''
        total = None
    
    
    return render_to_response('subclone_all.html', {'subclone_list': subclone_list, 'queries':queries, 'search':search, 'total':total, 'order_by':order_by}, context_instance=RequestContext(request))

@login_required
def SubcloneAssayResults(request):
    subclone = request.GET.get('subclone')
    host = request.GET.get('host')
    substrate = request.GET.get('substrate')
    researcher = request.GET.get('researcher')
    subclone_km = request.GET.get('subclone_km')
    subclone_temp = request.GET.get('subclone_temp')    
    subclone_ph = request.GET.get('subclone_ph')
    subclone_comments = request.GET.get('subclone_comments')
    
    values = { 'subclone' : subclone, 'host': host, 'researcher' : researcher, 'substrate': substrate, 'subclone_km': subclone_km, 'subclone_temp': subclone_temp, 'subclone_ph': subclone_ph, 'subclone_comments__icontains': subclone_comments}
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    qargs = {}
    for k, v in values.items():
        if v != '':
            qargs[k] = v
    if any(qargs):
        results = Subclone_Assay.objects.filter(**qargs).order_by(order_by)
        total = results.count
        p= Paginator(results, 5)
        page = request.GET.get('page')
        search = 1
        try:
            subclone_assay_list = p.page(page)
        except PageNotAnInteger:
            subclone_assay_list = p.page(1)
    else:
        results = None;
        subclone_assay_list = results
        search = ''
        total = None
    
    return render_to_response('subclone_assay_all.html', {'subclone_assay_list': subclone_assay_list, 'search':search, 'queries':queries, 'total':total, 'order_by':order_by}, context_instance=RequestContext(request))

@login_required
def CosmidAssayResults(request):
    #gets all of the user inputted information from the form
    cosmid = request.GET.get('cosmid')
    host = request.GET.get('host')
    substrate = request.GET.get('substrate')
    researcher = request.GET.get('researcher')
    cosmid_km = request.GET.get('cosmid_km')
    cosmid_temp = request.GET.get('cosmid_temp')    
    cosmid_ph = request.GET.get('cosmid_ph')
    cosmid_comments = request.GET.get('cosmid_comments')
    
    #converts it to dictionary
    values = {'cosmid': cosmid, 'host': host, 'researcher' : researcher, 'substrate': substrate, 'cosmid_km': cosmid_km, 'cosmid_temp': cosmid_temp, 'cosmid_ph': cosmid_ph, 'cosmid_comments__icontains': cosmid_comments}
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    #iterates through dictionary and assigns an arg value if it was entered
    qargs = {}
    for k, v in values.items():
        if v != '':
            qargs[k] = v
    if any(qargs):
        results = Cosmid_Assay.objects.filter(**qargs).order_by(order_by) #returns queryset of results based on qargs4
        total = results.count
        p= Paginator(results, 20)           #splits result sets into 20/page
        page = request.GET.get('page')      #gets current page
        search = 1                    #control what is seen in template
        try:
            cosmid_assay_list = p.page(page)
        except PageNotAnInteger:
            cosmid_assay_list = p.page(1)      #if no current page, go to first page
    else:
        results = None
        cosmid_assay_list = results
        search = ''
        total = None
        
    return render_to_response('cosmid_assay_all.html', {'cosmid_assay_list': cosmid_assay_list, 'search':search, 'queries':queries, 'total':total, 'order_by':order_by}, context_instance=RequestContext(request))

@login_required
def OrfResults(request):
    annotation = request.GET.get('annotation')
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    if (annotation):
        results = ORF.objects.filter(annotation__icontains=annotation).order_by(order_by)
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 1
        try:
            orf_list = p.page(page)
        except PageNotAnInteger:
            orf_list = p.page(1)
    else:
        results = None
        orf_list = results
        search = ''
        total = None
    
    return render_to_response('orf_all.html', {'orf_list': orf_list, 'search':search, 'queries':queries, 'total':total, 'order_by':order_by}, context_instance=RequestContext(request))

@login_required
def ContigResults(request):
    pool = request.GET.get('pool')
    contig_name = request.GET.get('contig_name')
    contig_accession = request.GET.get('contig_accession')
    values = {'pool' : pool, 'contig_name__icontains': contig_name, 'contig_accession' : contig_accession}
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    qargs = {}
    for k, v in values.items():
        if v != '':
            qargs[k] = v
    if any(qargs):
        results = Contig.objects.filter(**qargs).order_by(order_by) #returns queryset of results based on qargs
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 1
        try:
            contig_list = p.page(page)
        except PageNotAnInteger:
            contig_list = p.page(1)
    else:
        results = None
        contig_list = results
        search = ''
        total = None

    return render_to_response('contig_all.html', {'contig_list': contig_list, 'queries':queries, 'search':search, 'total':total, 'order_by':order_by}, context_instance=RequestContext(request))

@login_required
def CosmidBasicResults(request):
   #gets the list of words they entered
    query = request.GET.get('query')
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    #if no words entered, returns no results
    if query == '':
        results = None
        cosmid_list = results
        search = ''
        total = None
    else:
        #splits string into a list
        keywords = query.split()
        #builds a Q object for each word in the list
        list_name_qs = [Q(cosmid_name__icontains=word) for word in keywords]
        list_host_qs = [Q(host__host_name__icontains=word) for word in keywords]
        list_researcher_qs = [Q(researcher__researcher_name__icontains=word) for word in keywords]
        list_library_qs = [Q(library__library_name__icontains=word) for word in keywords]
        list_screen_qs = [Q(screen__screen_name__icontains=word) for word in keywords]
        list_ec_collection_qs = [Q(ec_collection__icontains=word) for word in keywords]
        list_original_media_qs = [Q(original_media__icontains=word) for word in keywords]
        list_pool_qs = [Q(pool__service_provider__icontains=word) for word in keywords]
        list_labbook_qs = [Q(lab_book_ref__icontains=word) for word in keywords]
        list_comments_qs = [Q(cosmid_comments__icontains=word) for word in keywords]
        
        #combines all the Q objects with the OR operator
        final_q = reduce(operator.or_, list_name_qs + list_host_qs + list_researcher_qs + list_library_qs + list_screen_qs + list_ec_collection_qs + list_original_media_qs + list_pool_qs + list_labbook_qs + list_comments_qs)
        results = Cosmid.objects.filter(final_q).order_by(order_by)
        total = results.count
        
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 2
        try:
            cosmid_list = p.page(page)
        except PageNotAnInteger:
            cosmid_list = p.page(1)
    return render_to_response('cosmid_end_tag_all.html', {'cosmid_list': cosmid_list, 'query': query, 'search':search, 'queries':queries, 'total':total, 'order_by':order_by}, context_instance=RequestContext(request))

@login_required
def SubcloneBasicResults(request):
    #gets the list of words they entered
    query = request.GET.get('query')
    #splits string into a list
    keywords = query.split()
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    
    #if no words entered, returns no results
    if query == '':
        results = None
        subclone_list = results
        search = ''
        total = None
    else:
        #builds a Q object for each word in the list
        list_name_qs = [Q(subclone_name__icontains=word) for word in keywords]
        list_cosmid_qs = [Q(cosmid__cosmid_name__icontains=word) for word in keywords]
        list_orfid_qs = []
        for word in keywords:
            if isinstance(word, types.IntType):
                list_orfid_qs.append(Q(orf__id__exact=word))
        list_orfanno_qs = [Q(orf__annotation__icontains=word) for word in keywords]
        list_vector_qs = [Q(vector__vector_name__icontains=word) for word in keywords]
        list_researcher_qs = [Q(researcher__researcher_name__icontains=word) for word in keywords]
        list_ec_collection_qs = [Q(ec_collection__icontains=word) for word in keywords] 
        list_primer1_qs = [Q(primer1_name__icontains=word) for word in keywords]
        list_primer2_qs = [Q(primer2_name__icontains=word) for word in keywords]        
        #combines all the Q objects with the OR operator
        final_q = reduce(operator.or_, list_name_qs + list_cosmid_qs + list_orfid_qs + list_orfanno_qs + list_vector_qs + list_ec_collection_qs + list_researcher_qs + list_primer1_qs + list_primer2_qs)
        results = Subclone.objects.filter(final_q).order_by(order_by)
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 2
        try:
            subclone_list = p.page(page)
        except PageNotAnInteger:
            subclone_list = p.page(1)
    return render_to_response('subclone_all.html', {'subclone_list': subclone_list, 'query': query, 'queries':queries, 'search':search, 'total':total, 'order_by':order_by}, context_instance=RequestContext(request))

@login_required
def CosmidAssayBasicResults(request):
    #gets the list of words they entered
    query = request.GET.get('query')
    #splits string into a list
    keywords = query.split()
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    
    #if no words entered, returns no results
    if query == '':
        results = None
        cosmid_assay_list = results
        search = ''
        total = None
    else:
        #builds a Q object for each word in the list
        list_name_qs = [Q(cosmid__cosmid_name__icontains=word) for word in keywords]
        list_host_qs = [Q(host__host_name__icontains=word) for word in keywords]
        list_substrate_qs = [Q(substrate__substrate_name__icontains=word) for word in keywords]
        list_antibiotic_qs = [Q(antibiotic__antibiotic_name__icontains=word) for word in keywords]
        list_researcher_qs = [Q(researcher__researcher_name__icontains=word) for word in keywords]
        list_km_qs = [Q(cosmid_km__icontains=word) for word in keywords] 
        list_temp_qs = [Q(cosmid_temp__icontains=word) for word in keywords]
        list_ph_qs = [Q(cosmid_ph__icontains=word) for word in keywords]        
        list_comments_qs = [Q(cosmid_comments__icontains=word) for word in keywords]
        #combines all the Q objects with the OR operator
        final_q = reduce(operator.or_, list_name_qs + list_host_qs + list_substrate_qs + list_antibiotic_qs + list_researcher_qs + list_km_qs + list_temp_qs + list_ph_qs + list_comments_qs)
        results = Cosmid_Assay.objects.filter(final_q).order_by(order_by)
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 2
        try:
            cosmid_assay_list = p.page(page)
        except PageNotAnInteger:
            cosmid_assay_list = p.page(1)
    return render_to_response('cosmid_assay_all.html', {'cosmid_assay_list': cosmid_assay_list, 'query': query, 'queries':queries, 'search':search, 'total':total, 'order_by':order_by}, context_instance=RequestContext(request))

@login_required
def SubcloneAssayBasicResults(request):
    #gets the list of words they entered
    query = request.GET.get('query')
    #splits string into a list
    keywords = query.split()
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    
    #if no words entered, returns no results
    if query == '':
        results = None
        subclone_assay_list = results
        search = ''
        total = None
    else:
        #builds a Q object for each word in the list
        list_subclone_qs = [Q(subclone__subclone_name__icontains=word) for word in keywords]
        list_host_qs = [Q(host__host_name__icontains=word) for word in keywords]
        list_substrate_qs = [Q(substrate__substrate_name__icontains=word) for word in keywords]
        list_antibiotic_qs = [Q(antibiotic__antibiotic_name__icontains=word) for word in keywords]
        list_researcher_qs = [Q(researcher__researcher_name__icontains=word) for word in keywords]
        list_km_qs = [Q(subclone_km__icontains=word) for word in keywords] 
        list_temp_qs = [Q(subclone_temp__icontains=word) for word in keywords]
        list_ph_qs = [Q(subclone_ph__icontains=word) for word in keywords]        
        list_comments_qs = [Q(subclone_comments__icontains=word) for word in keywords]
        #combines all the Q objects with the OR operator
        final_q = reduce(operator.or_, list_subclone_qs + list_host_qs + list_substrate_qs + list_antibiotic_qs + list_researcher_qs + list_km_qs + list_temp_qs + list_ph_qs + list_comments_qs)
        results = Subclone_Assay.objects.filter(final_q).order_by(order_by)
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 2
        try:
            subclone_assay_list = p.page(page)
        except PageNotAnInteger:
            subclone_assay_list = p.page(1)
    return render_to_response('subclone_assay_all.html', {'subclone_assay_list': subclone_assay_list, 'query': query, 'search':search, 'queries':queries, 'total':total, 'order_by':order_by}, context_instance=RequestContext(request))

@login_required
def OrfBasicResults(request):
    #gets the list of words they entered
    query = request.GET.get('query')
    #splits string into a list
    keywords = query.split()
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    
    #if no words entered, returns no results
    if query == '':
        results = None
        orf_list = results
        search = ''
        total = None
    else:
        #builds a Q object for each word in the list
        list_orfid_qs = []
        for word in keywords:
            if isinstance(word, types.IntType):
                list_orfid_qs.append(Q(orf__id__exact=word))
        list_orfanno_qs = [Q(annotation__icontains=word) for word in keywords]
        list_subclone_qs = [Q(subclone__subclone_name__icontains=word) for word in keywords]
        final_q = reduce(operator.or_, list_subclone_qs + list_orfanno_qs + list_orfid_qs)
        results = ORF.objects.filter(final_q).order_by(order_by)
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 2
        try:
            orf_list = p.page(page)
        except PageNotAnInteger:
            orf_list = p.page(1)
    return render_to_response('orf_all.html', {'orf_list': orf_list, 'query': query, 'search':search, 'queries':queries, 'total':total, 'order_by':order_by}, context_instance=RequestContext(request))

@login_required
def ContigBasicResults(request):
    #gets the list of words they entered
    query = request.GET.get('query')
    #splits string into a list
    keywords = query.split()
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    
    #if no words entered, returns no results
    if query == '':
        results = None
        contig_list = results
        search = ''
        total = None
    else:
        #builds a Q object for each word in the list
        list_poolid_qs = []
        for word in keywords:
            if isinstance(word, types.IntType):
                list_poolid_qs.append(Q(pool__id__exact=word))
        list_name_qs = [Q(contig_name__icontains=word) for word in keywords]
        list_accession_qs = [Q(contig_accession__icontains=word) for word in keywords]
        final_q = reduce(operator.or_, list_poolid_qs + list_name_qs + list_accession_qs)
        results = Contig.objects.filter(final_q).order_by(order_by)
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 2
        try:
            contig_list = p.page(page)
        except PageNotAnInteger:
            contig_list = p.page(1)
    return render_to_response('contig_all.html', {'contig_list': contig_list, 'query': query, 'search':search, 'queries':queries, 'total':total, 'order_by':order_by}, context_instance=RequestContext(request))

#detail views
@login_required
def CosmidDetail(request, cosmid_name):
    #returns the Cosmid object requested
    cosmid = Cosmid.objects.get(cosmid_name=cosmid_name)
    
    #gets all associated values with the requested cosmid object
    c_id = cosmid.pk
    name = cosmid.cosmid_name
    host = cosmid.host
    researcher = cosmid.researcher
    library = cosmid.library
    screen = cosmid.screen
    ec_collection = cosmid.ec_collection
    original_media = cosmid.original_media
    pool = cosmid.pool
    lab_book = cosmid.lab_book_ref
    cosmid_comments = cosmid.cosmid_comments
    
    #returns all end tags that are associated with the cosmid
    etresult = End_Tag.objects.filter(cosmid=c_id)
    pids = []
    #returns all the primers ids for the end tags
    for p in etresult:
        pids.append(p.primer_id)
    #returns a queryset of all primer objects used on all associated end tags
    primerresults = Primer.objects.filter(id__in= pids).values
    
    #returns queryset of all contigs associated with the cosmid requested
    contigresults = Contig.objects.filter(cosmid=c_id)
    contigids = []
    blankimg = None
    for c in contigresults:
        contigids.append(c.id)
        blankimg = GenerateImage(c)
    
    #returns all the orfs for the contigs that are associated with the cosmid
    orfresults = Contig_ORF_Join.objects.filter(contig_id__in=contigids).order_by('start')
    orfids = []
    for o in orfresults:
        orfids.append(o.orf_id)
    #returns all the sequences for all the associated orfs
    seq = ORF.objects.filter(id__in=orfids)
            
    def get_context_data(self, **kwargs):
        context = super(CosmidEditView, self).get_context_data(**kwargs)
        #Add in queryset of end tags
        context['end_tag_list'] = End_Tag.objects.all()
        return context
    
    return render_to_response('cosmid_detail.html', {'blank': blankimg, 'pids': pids, 'primers': primerresults, 'endtags': etresult, 'orfids': orfids, 'seq': seq, 'contigid': contigresults, 'orfs': orfresults, 'contigs': contigresults, 'cosmidpk': c_id, 'name': name, 'host': host, 'researcher': researcher, 'library': library, 'screen': screen, 'ec_collection': ec_collection, 'media': original_media, 'pool': pool, 'lab_book': lab_book, 'cosmid_comments': cosmid_comments}, context_instance=RequestContext(request))

def GenerateImage(contig):
    #get the picture and make a file.
    binaryimage = {'contig': contig.image_contig, 'align': contig.image_align, 'genbank': contig.image_genbank, 'predicted': contig.image_predicted, 'manual': contig.image_manual}
    name = contig.contig_name
    blanks = []
    for imgtype, img in binaryimage.items():
        if img:
            decodedimg = base64.b64decode(img)
            writeimg = open("mainsite/static/tempdisplay/" + name +  imgtype + ".png", "wb")
            writeimg.write(decodedimg)
            writeimg.close()
        else:
            blanks.append(imgtype)
    
    return blanks

@login_required
def ContigDetail(request, contig_name):
    contig = Contig.objects.get(contig_name=contig_name)
    
    key = contig.id
    name = contig.contig_name
    pool = contig.pool
    seq = contig.contig_sequence
    accession = contig.contig_accession
    cosmids = Cosmid.objects.filter(contig=contig.id)
    
    orfresults = Contig_ORF_Join.objects.filter(contig_id=contig.id).order_by('start')
    orfids = []
    for o in orfresults:
        orfids.append(o.orf_id)
    orfseq = ORF.objects.filter(id__in=orfids)
    
    #get the picture and make a file.
    blankimg = GenerateImage(contig)
            
    return render_to_response('contig_detail.html', {'blank': blankimg, 'orfresults': orfresults, 'orfids': orfids, 'orfseq': orfseq, 'cosmids': cosmids, 'sequence': seq, 'accession': accession, 'pool': pool, 'name': name, 'key': key}, context_instance=RequestContext(request))


@login_required
def OrfDetail(request, pk):
    orf = ORF.objects.get(id = pk)
    contigorfs = Contig_ORF_Join.objects.filter(orf_id = orf.id)
    
    contigids = []
    for c in contigorfs:
        contigids.append(c.contig_id)
    contigs = Contig.objects.filter(id__in = contigids)
    return render_to_response('orf_detail.html', {'orf': orf, 'contigs': contigs} , context_instance=RequestContext(request))

#the 5 classes below all use the generic DetailView to generate a detailed listing of the requested object from the database
class OrfDetailView(DetailView): #can delete this view
    model = ORF
    template_name = 'orf_detail.html'
 
class SubcloneAssayDetailView(DetailView):
    model = Subclone_Assay
    template_name = 'subclone_assay_detail.html'
    
class CosmidAssayDetailView(DetailView):
    model = Cosmid_Assay
    template_name = 'cosmid_assay_detail.html'

class SubcloneDetailView(DetailView):
    model = Subclone
    slug_field = 'subclone_name'
    slug_url_kwarg = 'subclone_name'
    template_name = 'subclone_detail.html'
  
class VectorDetailView(DetailView) :
    model = Vector
    template_name = 'vector_detail.html'
    
#edit views (updateview class)
#nb: slug fields required for using names in the urls instead of primary keys (Kathy)

class CosmidEditView(UpdateView):
    model = Cosmid
    template_name = 'cosmid_edit.html'
    slug_field = 'cosmid_name' 
    slug_url_kwarg = 'cosmid_name'
    success_url = reverse_lazy('cosmid-end-tag-list')
    
    def get_object(self, queryset=None):
        cosmid_object = Cosmid.objects.get(cosmid_name=self.kwargs['cosmid_name'])
        return cosmid_object
    
    def get_success_url(self):
        return ('/cosmid/' + self.get_object().cosmid_name)

#only for editing a cosmid's endtags -- ideally should be combined with cosmid edit (Kathy)
class CosmidEndTagEditView(UpdateView):
    model = Cosmid
    form_class = EndTagFormSet #requires both {{ form }} and {{ form_class }} in template
    template_name = 'cosmid_only_end_tag_edit.html'
    slug_field = 'cosmid_name' 
    slug_url_kwarg = 'cosmid_name'
    
    def get_object(self, queryset=None):
        cosmid_object = Cosmid.objects.get(cosmid_name=self.kwargs['cosmid_name'])
        return cosmid_object
    
    def get_success_url(self):
        return ('/cosmid/' + self.get_object().cosmid_name)

class SubcloneEditView(UpdateView):
    model = Subclone
    template_name = 'subclone_edit.html'
    slug_field = 'subclone_name'
    slug_url_kwarg = 'subclone_name'
    success_url = reverse_lazy('subclone-list')
    
class CosmidAssayEditView(UpdateView):
    model = Cosmid_Assay
    template_name = 'cosmid_assay_edit.html'
    success_url = reverse_lazy('cosmid-assay-list')

class SubcloneAssayEditView(UpdateView):
    model = Subclone_Assay
    template_name = 'subclone_assay_edit.html'
    success_url = reverse_lazy('subclone-assay-list')
    
class ORFEditView(UpdateView):
    model = ORF
    fields = ['orf_sequence', 'annotation']
    slug_field = 'pk'
    slug_url_kwarg = 'pk'
    template_name = 'orf_edit.html'
    success_url = reverse_lazy('orf-list')

    def get_object(self, queryset=None):
        orf_object = ORF.objects.get(id=self.kwargs['pk'])
        return orf_object
    
    #run annotation tool to update the stored images
    def get_success_url(self):
        orf = self.get_object().id
        contig_id = ORF.objects.filter(id = orf).values("contig")
        contig = Contig.objects.filter(id = contig_id).values("contig_name")
        orf_data(contig)
        system("perl annotation_tool/annotation_pipeline.pl -update")
        save_images("tmp")
        return ('/orf/' + orf)
    

class ContigEditView(UpdateView):
    model = Contig
    fields = ['contig_accession']
    template_name = 'contig_edit.html'
    success_url = reverse_lazy('contig-list')
    
    def get_object(self, queryset=None):
        contig_object = Contig.objects.get(id=self.kwargs['pk'])
        return contig_object
    
    #run annotation tool to update the stored images
    def get_success_url(self):
        contig = self.get_object().contig_name
        orf_data(contig)
        system("perl annotation_tool/annotation_pipeline.pl -update")
        save_images("tmp")
        return ('/contig/' + contig)
    
    
#Delete views (Katelyn)
class ContigORFDeleteView(DeleteView):
    model=Contig_ORF_Join
    template_name = 'contig_orf_delete.html'
    success_url = reverse_lazy('contig-list')
    
    def get_object(self, queryset=None):
        con_orf_object = Contig_ORF_Join.objects.get(id=self.kwargs['pk'])
        return con_orf_object
    
    #run annotation tool to update the stored images
    def get_success_url(self):
        contig_obj = self.get_object().contig
        contig = Contig.objects.filter(contig_name = contig_obj).values("contig_name")
        orf_data(contig)
        system("perl annotation_tool/annotation_pipeline.pl -update")
        save_images("tmp")
        return ('/contig/' + contig_obj.contig_name)
    
    
class ORFContigListView(ListView):
    model = Contig_ORF_Join
    template_name = 'orf_contig_all.html'
    paginate_by = 20
    
#retrieve ORFContigListView queryset to export as csv
@login_required
def orf_contig_queryset(response):
    qs = Contig_ORF_Join.objects.all()
    return queryset_export_csv(qs)  
    
# Create views for adding data to one model (Kathy)
class SubcloneCreateView(CreateView):
    model = Subclone
    template_name = 'subclone_add.html'
    success_url = reverse_lazy('subclone-list')

class CosmidAssayCreateView(CreateView):
    model = Cosmid_Assay
    template_name = 'cosmid_assay_add.html'
    success_url = reverse_lazy('cosmid-assay-list')

class SubcloneAssayCreateView(CreateView):
    model = Subclone_Assay
    template_name = 'subclone_assay_add.html'
    success_url = reverse_lazy('subclone-assay-list')
    
# Create views for adding data to multiple models with the same template

# Add to Cosmid and End_Tag tables (Kathy)
@permission_required('mainsite.cosmid.can_add_cosmid')
def CosmidEndTagCreate(request):
    if request.method == "POST":
        cosmid_form = CosmidForm(request.POST)
        end_tag_formset = EndTagFormSet(request.POST) #needs to be here
        if cosmid_form.is_valid():
            
            #do not commit new cosmid input until end tag form inputs have been checked 
            new_cosmid = cosmid_form.save(commit=False)
            end_tag_formset = EndTagFormSet(request.POST, instance=new_cosmid)

            #validation for the two primers chosen: primers cannot be the same (defined in the model)  
            if end_tag_formset.is_valid():
            
                #save cosmid, and process end tags
                new_cosmid.save()
                new_end_tags = end_tag_formset.save(commit=False)
                
                #if no end-tags submitted, new_end_tags is an empty list
                if (new_end_tags):
                    #check length -- if not empty, then either 1 or 2
                    if len(new_end_tags) == 2:
                        #remove whitespace from end tag sequences, make uppercase and save 
                        new_end_tags[0].end_tag_sequence = "".join(new_end_tags[0].end_tag_sequence.split()).upper()
                        new_end_tags[1].end_tag_sequence = "".join(new_end_tags[1].end_tag_sequence.split()).upper()
                        new_end_tags[0].save()
                        new_end_tags[1].save()
                    else:
                        new_end_tags[0].end_tag_sequence = "".join(new_end_tags[0].end_tag_sequence.split()).upper()
                        new_end_tags[0].save()
                else:
                    pass
                return HttpResponseRedirect('/cosmid/' + new_cosmid.cosmid_name) 
        
    else:
        cosmid_form = CosmidForm(instance=Cosmid())
        end_tag_formset = EndTagFormSet(instance=Cosmid())
    return render_to_response('cosmid_end_tag_add.html', {'cosmid_form': cosmid_form, 'end_tag_formset': end_tag_formset}, context_instance=RequestContext(request))
    
# Add to ORF and Contig-ORF-Join tables (Kathy)
@permission_required('mainsite.cosmid.can_add_orf')
def ORFContigCreate(request):
    
    #track errors with dict
    form_errors = {}
    
    if request.method == "POST":
        contig_orf_form = ContigORFJoinForm(request.POST, instance=Contig_ORF_Join())
        orf_form = ORFForm(request.POST, instance=ORF())
        if contig_orf_form.is_valid() and orf_form.is_valid():
            
            #save the new ORF and new contig but do not commit to the database tables yet
            new_orf = orf_form.save(commit=False)
            new_contig_orf = contig_orf_form.save(commit=False)
            orf_seq = new_orf.orf_sequence
            
            #remove all whitespace chars in string, and change to uppercase
            orf_seq = ''.join(orf_seq.split())
            orf_seq = orf_seq.upper()
            
            #check that sequence input is not blank
            if orf_seq == "":
                form_errors['error'] = 'Error: sequence cannot be blank'
            
            #if not blank, continue to process
            else:
                
                #if complement was indicated on form, get rev-com of ORF (for validation)
                complement = new_contig_orf.complement
                if complement == True:
                    orf_seq_rc = "" 
                    rc = {'A':'T', 'T':'A', 'G':'C', 'C':'G'}
                    check_seq = orf_seq[::-1]
                    for base in check_seq:
                        base = rc[base]
                        orf_seq_rc = orf_seq_rc + base
                    orf_seq_rc = ''.join(orf_seq_rc.split())
                    orf_seq = orf_seq_rc 
             
                #check that orf sequence actually in contig before comitting to contig_orf join
                contig_seq = new_contig_orf.contig.contig_sequence
                if orf_seq in contig_seq: 
                 
                    #check if orf_seq already present in orf table
                    orf_db_check = 0
                    orf_to_use = None 
                    orfs = ORF.objects.all()
                    for orf_object in orfs:
                        if orf_object.orf_sequence == new_orf.orf_sequence:
                            orf_db_check = 1
                            orf_to_use = orf_object

                    #if an orf with same sequence found in the database, use that orf instance
                    if orf_db_check == 1:    
                        new_orf = orf_to_use
                   
                    #otherwise, make a new orf instance to use
                    else:
                        #new_orf.orf_sequence = orf_seq
                        new_orf.save()
                            
                    #using the orf, make new instance of contig_orf_join
                    new_contig_orf.orf = new_orf
                    
                    #calculate start and stop and set
                    #if on the complement, stop is before start on contig
                    
                    #SWAPS THE START AND STOP POSITION FOR REVERSE SEQUENCES - NOT DONE BY CONVENTION SO REMOVED
                    #if complement == True:
                    #    orf_stop = contig_seq.index(orf_seq) + 1    # +1 to account for string index starting at 0
                    #    orf_start = orf_stop + len(orf_seq) - 1     # -1 to account again for indexing

                    #if not on the complement, start is before stop on contig
                    #else:
                    
                    orf_start = contig_seq.index(orf_seq) + 1   # +1 to account for string index starting at 0
                    orf_stop = orf_start + len(orf_seq) - 1     # -1 to account again for indexing
                    
                    #set start and stop
                    new_contig_orf.start = orf_start
                    new_contig_orf.stop = orf_stop
                    
                    #manual add of orf-contig (not generated by database tool)
                    new_contig_orf.predicted = False
                    
                    #check if this contig_orf_instance already in db, and return error
                    #nb: need to check: contig id, orf id, start, stop, complement
                    all_contig_orf_joins = Contig_ORF_Join.objects.all()
                    contig_orf_db_check = 0
                    for contig_orf_join in all_contig_orf_joins:
                        if (contig_orf_join.contig.id == new_contig_orf.contig.id and
                            contig_orf_join.orf.id == new_contig_orf.orf.id and
                            contig_orf_join.start == new_contig_orf.start and
                            contig_orf_join.stop == new_contig_orf.stop and
                            contig_orf_join.complement == new_contig_orf.complement):
                            contig_orf_db_check = 1
                    
                    if contig_orf_db_check == 1:
                        form_errors['error'] = 'Error: attempt to add duplicate entry'
                    
                    #if it doesn't exist, save it
                    else:
        
                        #save and redirect to contig's detailview
                        new_contig_orf.save()
                        
                        #update images in database with the new contig_orf  
                        orf_data(new_contig_orf)
                        system("perl annotation_tool/annotation_pipeline.pl -update")
                        save_images("tmp")
                        
                        #get contig name to use in redirect
                        contig_name = new_contig_orf.contig.contig_name
                        return HttpResponseRedirect('/contig/' + contig_name)   
            
                #orf not in contig; return error message
                else:
                    form_errors['ORF_not_in_contig'] = u'Error: The specified ORF is not found in selected Contig.'
        else:
            form_errors['error'] = 'Error: required field(s) blank'
    else:
        contig_orf_form = ContigORFJoinForm(instance=Contig_ORF_Join())
        orf_form = ORFForm(instance=ORF())
    
    return render_to_response('orf_contig_add.html', {'contig_orf_form': contig_orf_form, 'orf_form': orf_form, 'form_errors': form_errors}, context_instance=RequestContext(request))

#Add contigs to a given pool; contigs from FASTA file (Kathy)
@permission_required('mainsite.cosmid.can_add_contig')
def ContigPoolCreate(request):
    
    #track errors with dict
    form_errors = {}
    
    if request.method == "POST":
        contig_upload_form = UploadContigsForm(request.POST, request.FILES)
        contig_form = ContigForm(request.POST) 
        if contig_upload_form.is_valid() and contig_form.is_valid():
            
            #parse the fasta file using BioPython SeqIO.parse; store each contig-sequence record in a list
            fasta_file = request.FILES['fasta_file']
            file_name = request.FILES['fasta_file'].name
            records = []
            for seq_record in SeqIO.parse(fasta_file, "fasta"):
                records.append(seq_record)

            #return error message if file was not parsed successfully by SeqIO.parse
            if len(records) == 0:
                form_errors['file_error'] = 'Error: uploaded file is not FASTA format: ' + file_name
            
            #if file was parsed successfully, add all records to Contig table in database
            else:
                
                #get pool id
                pool = request.POST.get('pool')
                
                #iterate through records list and save each sequence
                for item in records:
                    
                    #append the pool id to the contig name for unique contig name in db
                    pool = str(pool)
                    name = 'pool' + pool + "_" + item.id
                    contig = Contig.objects.create(contig_name=name, pool_id=pool, contig_sequence = item.seq)
                    
                return HttpResponseRedirect('/results/contig/?pool=' + pool + "&contig_name=&contig_accession=")
                
        else:
            form_errors['error'] = 'Error: required field(s) blank'
    else:
        contig_form = ContigForm(instance=Contig())
        contig_upload_form = UploadContigsForm()      
    return render_to_response('contig_pool_add.html', {'contig_upload_form': contig_upload_form, 'contig_form': contig_form, 'form_errors': form_errors}, context_instance=RequestContext(request))

#force download csv file of input queryset(Nina)
def queryset_export_csv(qs):
    import csv
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment;filename="export.csv"'
    writer = csv.writer(response)
    qs_model = qs.model
    
    headers = []
    for field in qs_model._meta.fields:
        if not field.name == 'id':
            headers.append(field.name)
    writer.writerow(headers)

    for obj in qs:
        row = []
        val = ""
        for field in headers:
            try:
                val = getattr(obj, field)
            except:
                val = " "
            if callable(val):
                val = val()
            if type(val) == unicode:
                val = val.encode("utf-8")
            else:
                val = val
            row.append(val)
        writer.writerow(row)
    return response

# List views for lookup tables (Kathy)
class PrimerListView(ListView):
    model = Primer
    template_name = 'primer_all.html'
    paginate_by = 20

#retrieve PrimerListView queryset to export as csv
@login_required
def primer_queryset(response):
    qs = Primer.objects.all()
    return queryset_export_csv(qs)
    
class AntibioticListView(ListView):
    model = Antibiotic
    template_name = 'antibiotic_all.html'
    paginate_by = 20

#retrieve AntibioticListView queryset to export as csv
@login_required
def antibiotic_queryset(response):
    qs = Antibiotic.objects.all()
    return queryset_export_csv(qs)

class HostListView(ListView):
    model = Host
    template_name = 'host_all.html'
    paginate_by = 20
    
#retrieve HostListView queryset to export as csv
@login_required
def host_queryset(response):
    qs = Host.objects.all()
    return queryset_export_csv(qs)

class ScreenListView(ListView):
    model = Screen
    template_name = 'screen_all.html'
    paginate_by = 20
    
#retrieve ScreenListView queryset to export as csv
@login_required
def screen_queryset(response):
    qs = Screen.objects.all()
    return queryset_export_csv(qs)
    
class LibraryListView(ListView):
    model = Library
    template_name = 'library_all.html'
    paginate_by = 20
    
#retrieve LibraryListView queryset to export as csv
@login_required
def library_queryset(response):
    qs = Library.objects.all()
    return queryset_export_csv(qs)
    
class ResearcherListView(ListView):
    model = Researcher
    template_name = 'researcher_all.html'
    paginate_by = 20
    
#retrieve ResearcherListView queryset to export as csv
@login_required
def researcher_queryset(response):
    qs = Researcher.objects.all()
    return queryset_export_csv(qs)

class VectorListView(ListView):
    model = Vector
    template_name = 'vector_all.html'
    paginate_by = 20
    
#retrieve VectorListView queryset to export as csv
@login_required
def vector_queryset(response):
    qs = Vector.objects.all()
    return queryset_export_csv(qs)

class PoolListView(ListView):
    model = Pooled_Sequencing
    template_name = 'pool_all.html'
    paginate_by = 20
    
#retrieve PoolListView queryset to export as csv
@login_required
def pool_queryset(response):
    qs = Pooled_Sequencing.objects.all()
    return queryset_export_csv(qs)
    
class SubstrateListView(ListView):
    model = Substrate
    template_name = 'substrate_all.html'
    paginate_by = 20
    
#retrieve SubstrateListView queryset to export as csv
@login_required
def substrate_queryset(response):
    qs = Substrate.objects.all()
    return queryset_export_csv(qs)


# List views for non-lookup tables, no longer class based views (Katelyn)
def SubcloneListView(request):
    queries = request.GET.copy()
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    if queries.has_key('page'):
        del queries['page']
    search = ''
    results = Subclone.objects.all().order_by(order_by)
    total = results.count()
    p= Paginator(results, 20)
    page = request.GET.get('page')
    try:
        subclone_list = p.page(page)
    except PageNotAnInteger:
        subclone_list = p.page(1)
    return render_to_response('subclone_all.html', {'subclone_list':subclone_list, 'order_by':order_by, 'total':total, 'search':search}, context_instance=RequestContext(request))    
    

#retrieve SubcloneListView queryset to export as csv
@login_required
def subclone_queryset(response):
    qs = Subclone.objects.all()
    return queryset_export_csv(qs)
    
def CosmidAssayListView(request):
    queries = request.GET.copy()
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    if queries.has_key('page'):
        del queries['page']
    search = ''
    results = Cosmid_Assay.objects.all().order_by(order_by)
    total = results.count()
    p= Paginator(results, 20)
    page = request.GET.get('page')
    try:
        cosmid_assay_list = p.page(page)
    except PageNotAnInteger:
        cosmid_assay_list = p.page(1)
    return render_to_response('cosmid_assay_all.html', {'cosmid_assay_list':cosmid_assay_list, 'order_by':order_by, 'total':total, 'search':search}, context_instance=RequestContext(request))    
    

#retrieve CosmidAssayListView queryset to export as csv
@login_required
def cosmid_assay_queryset(response):
    qs = Cosmid_Assay.objects.all()
    return queryset_export_csv(qs)
    
def SubcloneAssayListView(request):
    queries = request.GET.copy()
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    if queries.has_key('page'):
        del queries['page']
    search = ''
    results = Subclone_Assay.objects.all().order_by(order_by)
    total = results.count()
    p= Paginator(results, 20)
    page = request.GET.get('page')
    try:
        subclone_assay_list = p.page(page)
    except PageNotAnInteger:
        subclone_assay_list = p.page(1)
    return render_to_response('subclone_assay_all.html', {'subclone_assay_list':subclone_assay_list, 'order_by':order_by, 'total':total, 'search':search}, context_instance=RequestContext(request))    
    


#retrieve SubcloneAssayListView queryset to export as csv
@login_required
def subclone_assay_queryset(response):
    qs = Subclone_Assay.objects.all()
    return queryset_export_csv(qs)


def ORFListView(request):
    queries = request.GET.copy()
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    if queries.has_key('page'):
        del queries['page']
    search = ''
    results = ORF.objects.all().order_by(order_by)
    total = results.count()
    p= Paginator(results, 20)
    page = request.GET.get('page')
    try:
        orf_list = p.page(page)
    except PageNotAnInteger:
        orf_list = p.page(1)
    return render_to_response('orf_all.html', {'orf_list':orf_list, 'order_by':order_by, 'total':total, 'search':search}, context_instance=RequestContext(request))    
    

#retrieve ORFListView queryset to export as csv
@login_required
def orf_queryset(response):
    qs = ORF.objects.all()
    return queryset_export_csv(qs)
    
def ContigListView(request):
    queries = request.GET.copy()
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    if queries.has_key('page'):
        del queries['page']
    search = ''
    results = Contig.objects.all().order_by(order_by)
    total = results.count()
    p= Paginator(results, 20)
    page = request.GET.get('page')
    try:
        contig_list = p.page(page)
    except PageNotAnInteger:
        contig_list = p.page(1)
    return render_to_response('contig_all.html', {'contig_list':contig_list, 'order_by':order_by, 'total':total, 'search':search}, context_instance=RequestContext(request))    
    

#retrieve ContigListView queryset to export as csv
@login_required
def contig_queryset(response):
    contigs = Contig.objects.all()
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment;filename="export.csv"'
    writer = csv.writer(response)
    
    #hard code columns names for lack of time
    writer.writerow(['Contig Name', 'Sequencing Pool', 'Contig Sequence', 'Contig NCBI Accession', 'BLAST Hit Accession'])
    for contig in contigs:

        #get contig accession, which can be none
        try:
            contig_acc = contig.contig_accession
        except Exception:
            contig_acc = ""
        
        #get blast accession, which can be none
        try:
            blast_acc = contig.blast_hit_accession
        except Exception:
            blast_acc = ""
        
        #write to csv
        writer.writerow([contig.contig_name, contig.pool.id, contig.contig_sequence,contig_acc, blast_acc])
    return response
    

# List views for multi-table views (Kathy)

def CosmidEndTagListView(request):
    queries = request.GET.copy()
    if queries.has_key('order_by'):
        del queries['order_by']
        order_by = request.GET.get('order_by')
    else:
        order_by = 'id'
    if queries.has_key('page'):
        del queries['page']
    search = ''
    results = Cosmid.objects.all().order_by(order_by)
    total = results.count()
    p= Paginator(results, 20)
    page = request.GET.get('page')
    try:
        cosmid_list = p.page(page)
    except PageNotAnInteger:
        cosmid_list = p.page(1)
    return render_to_response('cosmid_end_tag_all.html', {'cosmid_list':cosmid_list, 'order_by':order_by, 'total':total, 'search':search}, context_instance=RequestContext(request))    
    
    
  
#custom csv export for CosmidEndTagListView -- 8 tables/models, and many-to-many relationships
@login_required
def cosmid_endtag_queryset(response):
    cosmids = Cosmid.objects.all().select_related('end_tag__contig__researcher__library__screen__host__screen')
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment;filename="export.csv"'
    writer = csv.writer(response)
    
    #hard code columns names for lack of time
    writer.writerow(['Cosmid Name', 'Researcher Name', 'Library', 'Screen', 'Expression Host',
                     'E. coli Stock Location', 'Sequencing Pool', 'End Tag 1', 'End Tag 2', 'Contig 1', 'Contig 2', 'Comments'])
    for cosmid in cosmids:
        
        #get contigs, which can be none
        contigs = []
        for contig in cosmid.contig_set.all():
            contigs.append(contig.contig_name)
        try:
            contig1 = contigs[0]
        except Exception:
            contig1 = ""
        try:
            contig2 = contigs[1]
        except Exception:
            contig2 = ""
        
        #get pool, which can be none
        try:
            pool = cosmid.pool.id
        except Exception:
            pool = ""
       
        #get endtags, which can be none
        end_tags = []
        for end_tag in cosmid.end_tag_set.all():
            end_tags.append(end_tag.end_tag_sequence)
        try:
            endtag1 = end_tags[0]
        except Exception:
            endtag1 = ""
        try:
            endtag2 = end_tags[1]
        except Exception:
            endtag2 = ""
        
        #write to csv
        writer.writerow([cosmid.cosmid_name, cosmid.researcher.researcher_name, cosmid.library.library_name,
                         cosmid.screen.screen_name, cosmid.host.host_name, cosmid.ec_collection, pool, endtag1, endtag2,
                         contig1, contig2, cosmid.cosmid_comments])
    return response

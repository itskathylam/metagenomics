from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy
from operator import attrgetter
import operator
from django.core.paginator import Paginator, PageNotAnInteger
from django.core.files import File
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
from os import system
import pdb
import Image
from django.db.models import Q
import re

#Main, About etc

#@login_required
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

@login_required
def ContigTool(request):
    return (render(request, 'contig.html'))

@login_required
def AnnotationTool(request):
    email_form = EmailForm()
    all_contigs = Contig.objects.all()
    return render_to_response('tool_annotation.html', {'email_form': email_form, 'all_contigs': all_contigs}, context_instance=RequestContext(request))

def AnnotationToolResults(request):
    if request.method == "POST":
        results = request.POST
        pdb.set_trace()
    return render_to_response('tool_annotation_results.html', {'results': results })

def ContigTool(request):
    context = {'pool':Pooled_Sequencing.objects.all()}
    if request.method == "POST":
        if 'detail' in request.POST:
            pool_id =  request.POST['pool']            
            pool = Pooled_Sequencing.objects.all()
            details = Pooled_Sequencing.objects.filter(id = pool_id)
            cosmids = Cosmid.objects.filter(pool = pool_id)
            contigs = Contig.objects.all()
            context = {'pool': pool, 'detail': details, 'cosmids': cosmids, 'contigs': contigs}
            
        if 'submit' in request.POST:
            pool = request.POST['pool']
            cos = request.POST.getlist('cos')
            cos_selected = Cosmid.objects.filter(cosmid_name__in = cos).values_list('id', 'cosmid_name')
            contig_pipeline(pool, cos_selected) #need to integrate this step with renes tool and generate the tool
            results = read_csv('testtest.csv') #where does this come from????? should use database.....
            entries = []
            for row in results:
                entry = row[0:3]
                entry.append(row[5])
                entry.append(row[7])
                entry.append(row[8])
                entry.append(row[12])
                entries.append(entry)
            var = RequestContext(request, {'results': entries})
            return render_to_response('tool_contig_submit.html', var)
                
    variables = RequestContext(request, context)
    return render_to_response('tool_contig.html', variables)

def ContigToolResults(request):
    if request.method == 'POST':
        if 'submit' in request.POST:
            cosmidcontigs = request.POST.getlist('select')
    
        pattern = re.compile(r'^(.+)<\$\$>(.+)$')

        joins = {}
        for pair in cosmidcontigs:
            match = pattern.match(pair)
            joins[match.group(1)] = match.group(2)
        
        cosmids = []
        for join in joins:
            #pdb.set_trace()
            cosmid = Cosmid.objects.get(cosmid_name=join)
            contig = Contig.objects.get(contig_name=joins[join])
            contig.cosmid.add(cosmid)
            cosmids.append(join)
        return HttpResponseRedirect('/results/basic/cosmid?query=' + ' '.join(cosmids))
    
    return render_to_response('tool_contig_result.html', {'results': joins}, context_instance=RequestContext(request))
#read csv file into array
def read_csv(filename):
    import csv
    with open("contig_retrieval_tool/tmp/out/%s" %filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter = ',')
        rows = []
        for row in reader:
            rows.append(row)
    csvfile.closed
    return rows

def contig_pipeline(pool, cos_selected):
    pool_id = pool
    contigs = Contig.objects.filter(pool = pool_id).values_list('contig_name', 'contig_sequence')
    cosmids = cos_selected
    seqs = End_Tag.objects.select_related('cosmids').values_list('id', 'primer', 'end_tag_sequence')
    primer_set1 = Primer.objects.select_related('primer').filter(primer_pair = '1').values_list('id','primer_name')
    primer_set2 = Primer.objects.select_related('primer').filter(primer_pair = '2').values_list('id','primer_name')

    HttpResponse(write_fasta(contigs), write_csv('primers_1', cosmids, primer_set1, seqs), write_csv('primers_2', cosmids, primer_set2, seqs))
    HttpResponse(system("perl contig_retrieval_tool/retrieval_pipeline.pl contig_retrieval_tool/primers_1.csv contig_retrieval_tool/primers_2.csv contig_retrieval_tool/contigs.fa"))
    changed_rows = Contig.objects.filter(pool = pool_id)
    #for r in changed_rows:
    #    r.image_contig = Image.open("./img/contig.png")
    #    r.image_genbank = Image.open("./img/genbank.png")
    #    r.image_predicted = Image.open("./img/predicted.png")
    #    r.image_manual = Image.open("./img/manual.png")
    #    r.save()
    
def write_csv(file_name, cosmids, primer_set, seqs):
    with open("./contig_retrieval_tool/tmp/out/%s.csv" %file_name, 'w') as f:
        csv = File(f)
        seqs = list(seqs)
        cos = dict(cosmids)
        primers = dict(primer_set)
        for x, y, z in seqs:
            for c_id, csmd in cos.iteritems():
                for p_id, prmr in primers.iteritems():
                    if y == c_id and x == p_id:
                        csv.write(csmd + ',' + prmr + ',' + z + '\n')
        csv.closed
        f.closed

#writes contigs to fasta file(text.fa)    
def write_fasta(contigs):
    with open('./contig_retrieval_tool/contigs.fa', 'w') as f:
        fasta = File(f)
        contigs = list(contigs)
        for contig, seq in contigs:
            fasta.write('>' + contig + '\n' + seq + '\n')
        fasta.closed
        f.closed


def orf_data(request):
    contig_id = Contig.objects.filter(contig_name = 'scaffold58_1').values('id')
    contigs = Contig.objects.filter(contig_name = 'scaffold58_1').values_list('contig_name', 'contig_sequence', 'blast_hit_accession')
    orfs = Contig_ORF_Join.objects.filter(contig = contig_id).values_list('start', 'stop', 'complement', 'prediction_score')
    anno = ORF.objects.filter(contig = contig_id).values_list('annotation', 'orf_sequence')
   
    return HttpResponse(write_lib(contigs, orfs, anno))

def write_lib(contigs, orfs, anno):
    with open('./data.lib', 'w') as f:
        data = File(f)
        data.write('#!/usr/bin/perl \n sub data{\n')
        contig = ''
        accession = ''
        count = 1
        for name, seq, access in contigs:
            contig = name
            accession = access
            data.write('$contig_orf{' + name + '}\n = [\'' + seq + '\',\n')
        data.write('{\'glimmer\' => {},\n')
        data.write('\'genbank\' => {},\n')
        for start, stop, comp, score in orfs:
            for ann, seqs in anno:
                    comp = -1 if comp == 1 else 1
                    data.write('\'manual\' =>{\'' + contig + '-' + str(++count) + '\' => \n { start =>' + str(start) + ',\n end =>' + str(stop) + ',\n')
                    data.write('reading_frame =>' + str(comp) + ',\n score =>\'' + str(score) + '\',\n')
                    data.write('=>\'' + ann + '\',\n sequence =>\'' + seqs + '\'\n}}}' + accession + '];\n')
        data.write('return(\%contig_orf);} \n 1;') 
        data.closed
        f.closed


#sequence search
@login_required
def BlastSearch(request):
    blastform = BlastForm()
    return render_to_response('blast_search.html', {'blastform': blastform}, context_instance=RequestContext(request))

@login_required
def BlastResults(request):

    #get query sequence, clean of whitespace
    seq = request.POST.get('sequence')
    seq = ''.join(seq.split())
    
    #get parameters, and write to file
    e = request.POST.get('expect_threshold')
    w = request.POST.get('word_size')
    ma = request.POST.get('match_score')
    mi = request.POST.get('mismatch_score')
    go = request.POST.get('gap_open_penalty')
    ge = request.POST.get('gap_extension_penalty')
   
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
def SearchAll(request):
    form = AllSearchForm
    return render_to_response('all_search.html', {'form': form}, context_instance=RequestContext(request))

#search result views
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
    qargs = {}
    for k, v in values.items():
        if v != '':
            qargs[k] = v
    if any(qargs):
        results = Cosmid.objects.filter(**qargs)
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
    
    return render_to_response('cosmid_end_tag_all.html', {'cosmid_list': cosmid_list, 'queries':queries, 'search':search, 'total':total}, context_instance=RequestContext(request))


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
    qargs = {}
    for k, v in values.items():
        if v != '':
            qargs[k] = v
    if any(qargs):
        results = Subclone.objects.filter(**qargs)
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
    
    
    return render_to_response('subclone_all.html', {'subclone_list': subclone_list, 'queries':queries, 'search':search, 'total':total}, context_instance=RequestContext(request))

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
    qargs = {}
    for k, v in values.items():
        if v != '':
            qargs[k] = v
    if any(qargs):
        results = Subclone_Assay.objects.filter(**qargs)
        total = results.count
        p= Paginator(results, 20)
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
    
    return render_to_response('subclone_assay_all.html', {'subclone_assay_list': subclone_assay_list, 'search':search, 'queries':queries, 'total':total}, context_instance=RequestContext(request))

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
    #iterates through dictionary and assigns an arg value if it was entered
    qargs = {}
    for k, v in values.items():
        if v != '':
            qargs[k] = v
    if any(qargs):
        results = Cosmid_Assay.objects.filter(**qargs) #returns queryset of results based on qargs4
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
        
    return render_to_response('cosmid_assay_all.html', {'cosmid_assay_list': cosmid_assay_list, 'search':search, 'queries':queries, 'total':total}, context_instance=RequestContext(request))

def OrfResults(request):
    orf_list = request.GET.get('annotation')
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    if (annotation):
        results = ORF.objects.filter(annotation__icontains=annotation)
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
    
    return render_to_response('orf_all.html', {'orf_list': orf_list, 'search':search, 'queries':queries, 'total':total}, context_instance=RequestContext(request))

def ContigResults(request):
    pool = request.GET.get('pool')
    contig_name = request.GET.get('contig_name')
    contig_accession = request.GET.get('contig_accession')
    values = {'pool' : pool, 'contig_name__icontains': contig_name, 'contig_accession' : contig_accession}
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    qargs = {}
    for k, v in values.items():
        if v != '':
            qargs[k] = v
    if any(qargs):
        results = Contig.objects.filter(**qargs) #returns queryset of results based on qargs
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

    return render_to_response('contig_all.html', {'contig_list': contig_list, 'queries':queries, 'search':search, 'total':total}, context_instance=RequestContext(request))


def CosmidBasicResults(request):
   #gets the list of words they entered
    query = request.GET.get('query')
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
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
        results = Cosmid.objects.filter(final_q)
        total = results.count
        
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 2
        try:
            cosmid_list = p.page(page)
        except PageNotAnInteger:
            cosmid_list = p.page(1)
    return render_to_response('cosmid_end_tag_all.html', {'cosmid_list': cosmid_list, 'query': query, 'search':search, 'queries':queries, 'total':total}, context_instance=RequestContext(request))

def SubcloneBasicResults(request):
    #gets the list of words they entered
    query = request.GET.get('query')
    #splits string into a list
    keywords = query.split()
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    
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
        results = Subclone.objects.filter(final_q)
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 2
        try:
            subclone_list = p.page(page)
        except PageNotAnInteger:
            subclone_list = p.page(1)
    return render_to_response('subclone_all.html', {'subclone_list': subclone_list, 'query': query, 'queries':queries, 'search':search, 'total':total}, context_instance=RequestContext(request))

def CosmidAssayBasicResults(request):
    #gets the list of words they entered
    query = request.GET.get('query')
    #splits string into a list
    keywords = query.split()
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    
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
        results = Cosmid_Assay.objects.filter(final_q)
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 2
        try:
            cosmid_assay_list = p.page(page)
        except PageNotAnInteger:
            cosmid_assay_list = p.page(1)
    return render_to_response('cosmid_assay_all.html', {'cosmid_assay_list': cosmid_assay_list, 'query': query, 'queries':queries, 'search':search, 'total':total}, context_instance=RequestContext(request))

def SubcloneAssayBasicResults(request):
    #gets the list of words they entered
    query = request.GET.get('query')
    #splits string into a list
    keywords = query.split()
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    
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
        results = Subclone_Assay.objects.filter(final_q)
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 2
        try:
            subclone_assay_list = p.page(page)
        except PageNotAnInteger:
            subclone_assay_list = p.page(1)
    return render_to_response('subclone_assay_all.html', {'subclone_assay_list': subclone_assay_list, 'query': query, 'search':search, 'queries':queries, 'total':total}, context_instance=RequestContext(request))

def OrfBasicResults(request):
    #gets the list of words they entered
    query = request.GET.get('query')
    #splits string into a list
    keywords = query.split()
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    
    
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
        results = ORF.objects.filter(final_q)
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 2
        try:
            orf_list = p.page(page)
        except PageNotAnInteger:
            orf_list = p.page(1)
    return render_to_response('orf_all.html', {'orf_list': orf_list, 'query': query, 'search':search, 'queries':queries, 'total':total}, context_instance=RequestContext(request))

def ContigBasicResults(request):
    #gets the list of words they entered
    query = request.GET.get('query')
    #splits string into a list
    keywords = query.split()
    queries = request.GET.copy();
    if queries.has_key('page'):
        del queries['page']
    
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
        results = Contig.objects.filter(final_q)
        total = results.count
        p= Paginator(results, 20)
        page = request.GET.get('page')
        search = 2
        try:
            contig_list = p.page(page)
        except PageNotAnInteger:
            contig_list = p.page(1)
    return render_to_response('contig_all.html', {'contig_list': contig_list, 'query': query, 'search':search, 'queries':queries, 'total':total}, context_instance=RequestContext(request))

#detail views
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
    for c in contigresults:
        contigids.append(c.id)
    
    #returns all the orfs for the contigs that are associated with the cosmid
    orfresults = Contig_ORF_Join.objects.filter(contig_id__in=contigids)
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
    
    return render_to_response('cosmid_detail.html', {'pids': pids, 'primers': primerresults, 'endtags': etresult, 'orfids': orfids, 'seq': seq, 'contigid': contigresults, 'orfs': orfresults, 'contigs': contigresults, 'cosmidpk': c_id, 'name': name, 'host': host, 'researcher': researcher, 'library': library, 'screen': screen, 'ec_collection': ec_collection, 'media': original_media, 'pool': pool, 'lab_book': lab_book, 'cosmid_comments': cosmid_comments}, context_instance=RequestContext(request))

def ContigDetail(request, contig_name):
    contig = Contig.objects.get(contig_name=contig_name)
    
    key = contig.id
    name = contig.contig_name
    pool = contig.pool
    seq = contig.contig_sequence
    accession = contig.contig_accession
    cosmids = Cosmid.objects.filter(contig=contig.id)
    
    orfresults = Contig_ORF_Join.objects.filter(contig_id=contig.id)
    orfids = []
    for o in orfresults:
        orfids.append(o.orf_id)
    orfseq = ORF.objects.filter(id__in=orfids)
    
    
    return render_to_response('contig_detail.html', {'orfresults': orfresults, 'orfids': orfids, 'orfseq': orfseq, 'cosmids': cosmids, 'sequence': seq, 'accession': accession, 'pool': pool, 'name': name, 'key': key}, context_instance=RequestContext(request))


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
    
#only for editing a cosmid's endtags -- ideally should be combined with cosmid edit
class CosmidEndTagEditView(UpdateView):
    model = Cosmid
    form_class = EndTagFormSetUpdate #requires both {{ form }} and {{ form_class }} in template
    template_name = 'cosmid_only_end_tag_edit.html'
    slug_field = 'cosmid_name' 
    slug_url_kwarg = 'cosmid_name'
    success_url = reverse_lazy('cosmid-end-tag-list')
    #Note: this works because change is goes to db, but results in Django page error
    #Django error: 'list' object has no attribute '__dict__'
    
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
    #exclude = ['contig']
    template_name = 'orf_edit.html'
    success_url = reverse_lazy('orf-list')

class ContigEditView(UpdateView):
    model = Contig
    fields = ['contig_accession']
    template_name = 'contig_edit.html'
    success_url = reverse_lazy('contig-list')
    
#Delete views (Katelyn)
class ContigORFDeleteView(DeleteView):
    model=Contig_ORF_Join
    template_name = 'contig_orf_delete.html'
    success_url = reverse_lazy('orf-contig-list')

# List views for non-lookup tables (Kathy)
class SubcloneListView(ListView):
    model = Subclone
    template_name = 'subclone_all.html'
    paginate_by = 20

#retrieve SubcloneView queryset to export as csv
def subclone_queryset(response):
    qs = Subclone.objects.all()
    return queryset_export_csv(qs)
    
class CosmidAssayListView(ListView):
    model = Cosmid_Assay
    template_name = 'cosmid_assay_all.html'
    paginate_by = 20

#retrieve CosmidAssayListView queryset to export as csv
def cosmid_assay_queryset(response):
    qs = Cosmid_Assay.objects.all()
    return queryset_export_csv(qs)
    
class SubcloneAssayListView(ListView):
    model = Subclone_Assay
    template_name = 'subclone_assay_all.html'
    paginate_by = 20

#retrieve SubcloneListView queryset to export as csv
def subclone_assay_queryset(response):
    qs = Subclone_Assay.objects.all()
    return queryset_export_csv(qs)

class ORFListView (ListView):
    model = ORF
    template_name = 'orf_all.html'
    paginate_by = 20

#retrieve ORFListView queryset to export as csv
def orf_queryset(response):
    qs = ORF.objects.all()
    return queryset_export_csv(qs)
    
class ContigListView (ListView):
    model = Contig
    template_name = 'contig_all.html'
    paginate_by = 20

#retrieve ContigListView queryset to export as csv
def contig_queryset(response):
    qs = Contig.objects.all()
    return queryset_export_csv(qs)

# List views for multi-table views (Kathy)

class CosmidEndTagListView(ListView):
    model = Cosmid
    template_name = 'cosmid_end_tag_all.html'
    paginate_by = 20
  
#retrieve CosmidEndTagListView queryset to export as csv
def cosmid_endtag_queryset(response):
    qs = Cosmid.objects.all()
    return queryset_export_csv(qs)  
    
class ORFContigListView(ListView):
    model = Contig_ORF_Join
    template_name = 'orf_contig_all.html'
    paginate_by = 20
    
#retrieve ORFContigListView queryset to export as csv
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
                    #remove whitespace from end tag sequences and save 
                    new_end_tags[0].end_tag_sequence = "".join(new_end_tags[0].end_tag_sequence.split())
                    new_end_tags[1].end_tag_sequence = "".join(new_end_tags[1].end_tag_sequence.split())
                    new_end_tags[0].save()
                    new_end_tags[1].save()
                else:
                    pass
                return HttpResponseRedirect('/cosmid/') 
        
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
            
            #remove all whitespace chars in string
            orf_seq = ''.join(orf_seq.split())
            
            #check that sequence input is not blank!
            if orf_seq == "":
                form_errors['error'] = 'Error: sequence cannot be blank'
            
            #if not blank, continue to process
            else:
                
                #if complement was indicated on form, get rev-com of ORF (for validation)
                complement = new_contig_orf.complement
                orf_seq_rc = ""
                if complement == True:
                    rc = {'A':'T', 'T':'A', 'G':'C', 'C':'G'}
                    orf_seq = orf_seq[::-1]
                    for base in orf_seq:
                        base = rc[base]
                        orf_seq_rc = orf_seq_rc + base
                
                #check that orf sequence actually in contig before comitting to contig_orf join
                contig_seq = new_contig_orf.contig.contig_sequence
                if orf_seq in contig_seq or orf_seq_rc in contig_seq: 
                    
                    #check if orf_seq already present in orf table
                    orfs = ORF.objects.all()
                    for orf_object in orfs:
                        
                        #if so, use existing orf instance
                        if orf_object.orf_sequence == orf_seq:
                            new_orf = orf_object
                        
                        #otherwise, make new orf instance in orf table
                        
                            new_orf.orf_sequence = orf_seq
                            new_orf.save()  
                    
                    #make new instance of contig_orf_join
                    new_contig_orf.orf = new_orf
                    
                    #calculate start and stop
                    orf_start = contig_seq.index(orf_seq) + 1
                    orf_stop = orf_start + len(orf_seq) - 1
                    new_contig_orf.start = orf_start
                    new_contig_orf.stop = orf_stop
                    
                    #manual add of orf-contig (not generated by database tool)
                    new_contig_orf.predicted = False
                    
                    #save and redirect to contig's detailview
                    new_contig_orf.save()
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
        line = ""
        for field in headers:
            val = getattr(obj, field)
            if callable(val):
                val = val()
            if type(val) == unicode:
                val = val.encode("utf-8")
            if val is None:
                val =""
            else:
                try:
                    val = silent(val)
                except:
                    pass
                try:
                    val = val.id
                except:
                    pass
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
def primer_queryset(response):
    qs = Primer.objects.all()
    return queryset_export_csv(qs)
    
class AntibioticListView(ListView):
    model = Antibiotic
    template_name = 'antibiotic_all.html'
    paginate_by = 20

#retrieve AntibioticListView queryset to export as csv
def antibiotic_queryset(response):
    qs = Antibiotic.objects.all()
    return queryset_export_csv(qs)

class HostListView(ListView):
    model = Host
    template_name = 'host_all.html'
    paginate_by = 20
    
#retrieve HostListView queryset to export as csv
def host_queryset(response):
    qs = Host.objects.all()
    return queryset_export_csv(qs)

class ScreenListView(ListView):
    model = Screen
    template_name = 'screen_all.html'
    paginate_by = 20
    
#retrieve ScreenListView queryset to export as csv
def screen_queryset(response):
    qs = Screen.objects.all()
    return queryset_export_csv(qs)
    
class LibraryListView(ListView):
    model = Library
    template_name = 'library_all.html'
    paginate_by = 20
    
#retrieve LibraryListView queryset to export as csv
def library_queryset(response):
    qs = Library.objects.all()
    return queryset_export_csv(qs)
    
class ResearcherListView(ListView):
    model = Researcher
    template_name = 'researcher_all.html'
    paginate_by = 20
    
#retrieve ResearcherListView queryset to export as csv
def researcher_queryset(response):
    qs = Researcher.objects.all()
    return queryset_export_csv(qs)

class VectorListView(ListView):
    model = Vector
    template_name = 'vector_all.html'
    paginate_by = 20
    
#retrieve VectorListView queryset to export as csv
def vector_queryset(response):
    qs = Vector.objects.all()
    return queryset_export_csv(qs)

class PoolListView(ListView):
    model = Pooled_Sequencing
    template_name = 'pool_all.html'
    paginate_by = 20
    
#retrieve PoolListView queryset to export as csv
def pool_queryset(response):
    qs = Pooled_Sequencing.objects.all()
    return queryset_export_csv(qs)
    
class SubstrateListView(ListView):
    model = Substrate
    template_name = 'substrate_all.html'
    paginate_by = 20
    
#retrieve SubstrateListView queryset to export as csv
def substrate_queryset(response):
    qs = Substrate.objects.all()
    return queryset_export_csv(qs)

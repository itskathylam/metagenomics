from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy
from operator import attrgetter

from mainsite.models import *
from mainsite.forms import *

from Bio.Blast.Applications import NcbiblastnCommandline

from Bio.Blast import NCBIXML
from Bio import SeqIO
import StringIO
import pdb
#pdb.set_trace()



#Main, About etc

#login_required
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

def UserSettings(request):
    form = UserForm
    return render_to_response('usersettings.html', {'form': form}, context_instance=RequestContext(request))
def Faq(request):
    return (render(request, 'faq.html'))

def UserDoc(request):
    return (render(request, 'userdoc.html'))

def ContigTool(request):
    return (render(request, 'contig.html'))

def Pooling(request):
    return (render(request, 'pooling.html'))

#sequence search
def BlastSearch(request):
    blastform = BlastForm
    return render_to_response('blast_search.html', {'blastform': blastform}, context_instance=RequestContext(request))

def BlastResults(request):
    #get all sequences in the database and names
    #sequence = Contig.objects.all().contig_sequence
    #name = Contig.objects.all().contig_name
    #
    ##write entries to a fasta file
    #outfh = open("newtempfile.fa", "w")
    #Bio.SeqIO.write(sequence, outfh, "fasta")
    #outfh.close()
    #
    ##makeblastdb to create BLAST database of files from fastafile
    #os.system(str(makeblastdb -in newtempfile.fa -out contigdb))
    #
    ##get query sequence type of blast and parameters
    #seq = request.POST.get('sequence')
    ##blast = n #mega, dcmega
    #
    ##run blast command with query, parameters, and created database
    ##/home/rene/endtags/end/install/ncbi-blast-2.2.29+-src/c++/ReleaseMT/bin
    #cmd = NcbiblastnCommandLine(query=".fa", db="contigdb", evalue=1, outfmt=5, out=".xml")
    #os.system(str(cmd))
    #
    ##have to know when its done to be able to continue?
    #
    ##parse .xml file
    #records = NCBIXML.parse()
    #
    ##results
    #records.next()
    
    #make this view a loading page and then redirect to results??
    return render_to_response('blast_results.html', {'sequence': seq}, context_instance=RequestContext(request))


#search forms
def CosmidSearchView(request):
    form = CosmidForm
    return render_to_response('cosmid_search.html', {'form': form}, context_instance=RequestContext(request))

def SubcloneSearchView(request):
    form = SubcloneForm
    return render_to_response('subclone_search.html', {'form': form}, context_instance=RequestContext(request))

def SubcloneAssaySearchView(request):
    form = SubcloneAssayForm
    return render_to_response('subclone_assay_search.html', {'form': form}, context_instance=RequestContext(request))

def CosmidAssaySearchView(request):
    form = CosmidAssayForm
    return render_to_response('cosmid_assay_search.html', {'form': form}, context_instance=RequestContext(request))

def OrfSearchView(request):
    form = OrfSearchForm
    return render_to_response('orf_search.html', {'form': form}, context_instance=RequestContext(request))

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
    values = { 'cosmid_name__icontains' : cosmid_name, 'host': host, 'researcher' : researcher, 'library': library, 'screen': screen, 'ec_collection__icontains': ec_collection, 'original_media__icontains': original_media, 'pool': pool, 'lab_book_ref__icontains': lab_book_ref}
    args = {}
    for k, v in values.items():
        if v:
            args[k] = v
    results = Cosmid.objects.filter(**args)
    return render_to_response('cosmid_end_tag_all.html', {'cosmid_list': results}, context_instance=RequestContext(request))

def SubcloneResults(request):
    name = request.GET.get('subclone_name')
    cosmid = request.GET.get('cosmid')
    orf = request.GET.get('orf')
    vector = request.GET.get('vector')
    researcher = request.GET.get('researcher')
    ec_collection = request.GET.get('ec_collection')
    
    values = {'subclone_name__icontains' : name, 'cosmid': cosmid, 'researcher' : researcher, 'orf': orf, 'vector': vector, 'researcher': researcher, 'ec_collection__icontains': ec_collection}
    args = {}
    for k, v in values.items():
        if v:
            args[k] = v
    results = Subclone.objects.filter(**args)
    return render_to_response('subclone_all.html', {'subclone_list': results}, context_instance=RequestContext(request))

def SubcloneAssayResults(request):
    subclone = request.GET.get('subclone')
    host = request.GET.get('host')
    substrate = request.GET.get('substrate')
    researcher = request.GET.get('researcher')
    subclone_km = request.GET.get('subclone_km')
    subclone_temp = request.GET.get('subclone_temp')    
    subclone_ph = request.GET.get('subclone_ph')
    subclone_comments = request.GET.get('subclone_comments')
    
    values = { 'subclone' : subclone, 'host': host, 'researcher' : researcher, 'substrate': substrate, 'subclone_km': subclone_km, 'subclone_temp': subclone_temp, 'subclone_ph': subclone_ph, 'subclone_comments': subclone_comments}
    args = {}
    for k, v in values.items():
        if v:
            args[k] = v
    results = Subclone_Assay.objects.filter(**args)
    return render_to_response('subclone_assay_all.html', {'subclone_assay_list': results}, context_instance=RequestContext(request))

def CosmidAssayResults(request):
    cosmid = request.GET.get('cosmid')
    host = request.GET.get('host')
    substrate = request.GET.get('substrate')
    researcher = request.GET.get('researcher')
    cosmid_km = request.GET.get('cosmid_km')
    cosmid_temp = request.GET.get('cosmid_temp')    
    cosmid_ph = request.GET.get('cosmid_ph')
    cosmid_comments = request.GET.get('cosmid_comments')
    
    values = {'cosmid': cosmid, 'host': host, 'researcher' : researcher, 'substrate': substrate, 'cosmid_km': cosmid_km, 'cosmid_temp': cosmid_temp, 'cosmid_ph': cosmid_ph, 'cosmid_comments': cosmid_comments}
    args = {}
    for k, v in values.items():
        if v:
            args[k] = v
    results = Cosmid_Assay.objects.filter(**args)
    return render_to_response('cosmid_assay_all.html', {'cosmid_assay_list': results}, context_instance=RequestContext(request))

def OrfResults(request):
    annotation = request.GET.get('annotation')
    results = ORF.objects.filter(annotation__icontains=annotation)
    return render_to_response('orf_all.html', {'orf_list': results}, context_instance=RequestContext(request))

#detail views
def CosmidDetail(request, cosmid_name):
    cosmid = Cosmid.objects.get(cosmid_name=cosmid_name)
    
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
    
    etresult = End_Tag.objects.filter(cosmid=c_id)
    pids = []
    for p in etresult:
        pids.append(p.primer_id)  
    primerresults = Primer.objects.filter(id__in= pids).values
    
    contigresults = Contig.objects.filter(cosmid=c_id)
    contigids = []
    for c in contigresults:
        contigids.append(c.id)
    
    orfresults = Contig_ORF_Join.objects.filter(contig_id__in=contigids)
    orfids = []
    for o in orfresults:
        orfids.append(o.orf_id)
    seq = ORF.objects.filter(id__in=orfids)
    
    return render_to_response('cosmid_detail.html', {'pids': pids, 'primers': primerresults, 'endtags': etresult, 'orfids': orfids, 'seq': seq, 'contigid': contigresults, 'orfs': orfresults, 'contigs': contigresults, 'cosmidpk': c_id, 'name': name, 'host': host, 'researcher': researcher, 'library': library, 'screen': screen, 'ec_collection': ec_collection, 'media': original_media, 'pool': pool, 'lab_book': lab_book}, context_instance=RequestContext(request))


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

class OrfDetailView(DetailView):
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
    template_name = 'subclone_detail.html'
  
#edit views (updateview class)
class CosmidEditView(UpdateView):
    model = Cosmid
    template_name = 'cosmid_edit.html'
    success_url = reverse_lazy('cosmid-end-tag-list')
    
class SubcloneEditView(UpdateView):
    model = Subclone
    template_name = 'subclone_edit.html'
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
    
class CosmidAssayListView(ListView):
    model = Cosmid_Assay
    template_name = 'cosmid_assay_all.html'
    
class SubcloneAssayListView(ListView):
    model = Subclone_Assay
    template_name = 'subclone_assay_all.html'

class ORFListView (ListView):
    model = ORF
    template_name = 'orf_all.html'
    
class ContigListView (ListView):
    model = Contig
    template_name = 'contig_all.html'
    
  
# List views for multi-table views (Kathy)

class CosmidEndTagListView(ListView):
    model = Cosmid
    template_name = 'cosmid_end_tag_all.html'
    
class ORFContigListView(ListView):
    model = Contig_ORF_Join
    template_name = 'orf_contig_all.html'
    
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
                new_cosmid.save()
                end_tag_formset.save()
                return HttpResponseRedirect('/cosmid/') 
        
    else:
        cosmid_form = CosmidForm(instance=Cosmid())
        end_tag_formset = EndTagFormSet(instance=Cosmid())
    return render_to_response('cosmid_end_tag_add.html', {'cosmid_form': cosmid_form, 'end_tag_formset': end_tag_formset}, context_instance=RequestContext(request))

    
# Add to ORF and Contig-ORF-Join tables (Kathy)
@permission_required('mainsite.cosmid.can_add_contig_orf_join')
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
            
            #validate orf sequence actually in contig before comitting to contig_orf join
            orf_seq = new_orf.orf_sequence 
            contig_seq = new_contig_orf.contig.contig_sequence
            if orf_seq in contig_seq:
                new_orf.save()
                new_contig_orf.orf = new_orf
                
                #calculate start and stop
                orf_start = contig_seq.index(orf_seq) + 1
                orf_stop = orf_start + len(orf_seq) - 1
                new_contig_orf.start = orf_start
                new_contig_orf.stop = orf_stop
                
                #manual add of orf-contig (not generated by database tool)
                new_contig_orf.db_generated = False
                
                new_contig_orf.save()
                return HttpResponseRedirect('/orfcontig/')
            
            #orf not in contig; return error message
            else:
                form_errors['ORF_not_in_contig'] = u'Error: The specified ORF is not found in chosen Contig.'
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
        contig_form = ContigForm(request.POST) #must be here as well
        if contig_upload_form.is_valid():
            
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
                for item in records:
                    if contig_form.is_valid():
                        contig_form = ContigForm(request.POST)
                        new_contig = contig_form.save(commit=False)
                        
                        #get the pood id for use in appending to scaffold name, and save record
                        pool =  str(new_contig.pool.id)
                        
                        #save record
                        new_contig.contig_name = 'pool' + pool + "_" + item.id
                        new_contig.contig_sequence = item.seq
                        new_contig.save()
                return HttpResponseRedirect('/contig/')          
    else:
        contig_form = ContigForm()
        contig_upload_form = UploadContigsForm()      
    return render_to_response('contig_pool_add.html', {'contig_upload_form': contig_upload_form, 'contig_form': contig_form, 'form_errors': form_errors}, context_instance=RequestContext(request))

#force download of input queryset to csv file (Nina)
def queryset_export_csv(qs):
    import csv
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment;filename="export.csv"'
    writer = csv.writer(response)
    qs_model = qs.model
    
    headers = []
    for field in qs_model._meta.fields:
        headers.append(field.name)
    writer.writerow(headers)

    for obj in qs:
        row = []
        for field in headers:
            val = getattr(obj, field)
            if callable(val):
                val = val()
            if type(val) == unicode:
                val = val.encode("utf-8")
            row.append(val)
        writer.writerow(row)
    return response

# List views for lookup tables (Kathy)
class PrimerListView(ListView):
    model = Primer
    template_name = 'primer_all.html'

#retrieve PrimerListView queryset to export as csv
def primer_queryset(response):
    qs = Primer.objects.all()
    return queryset_export_csv(qs)

class HostListView(ListView):
    model = Host
    template_name = 'host_all.html'
    
#retrieve HostListView queryset to export as csv
def host_queryset(response):
    qs = Host.objects.all()
    return queryset_export_csv(qs)

class ScreenListView(ListView):
    model = Screen
    template_name = 'screen_all.html'
    
#retrieve ScreenListView queryset to export as csv
def screen_queryset(response):
    qs = Screen.objects.all()
    return queryset_export_csv(qs)
    
class LibraryListView(ListView):
    model = Library
    template_name = 'library_all.html'
    
#retrieve LibraryListView queryset to export as csv
def library_queryset(response):
    qs = Library.objects.all()
    return queryset_export_csv(qs)
    
class ResearcherListView(ListView):
    model = Researcher
    template_name = 'researcher_all.html'
    
#retrieve ResearcherListView queryset to export as csv
def researcher_queryset(response):
    qs = Researcher.objects.all()
    return queryset_export_csv(qs)

class VectorListView(ListView):
    model = Vector
    template_name = 'vector_all.html'
    
#retrieve VectorListView queryset to export as csv
def vector_queryset(response):
    qs = Vector.objects.all()
    return queryset_export_csv(qs)

class PoolListView(ListView):
    model = Pooled_Sequencing
    template_name = 'pool_all.html'
    
#retrieve PoolListView queryset to export as csv
def pool_queryset(response):
    qs = Pooled_Sequencing.objects.all()
    return queryset_export_csv(qs)
    
class SubstrateListView(ListView):
    model = Substrate
    template_name = 'substrate_all.html'
    
#retrieve SubstrateListView queryset to export as csv
def substrate_queryset(response):
    qs = Substrate.objects.all()
    return queryset_export_csv(qs)


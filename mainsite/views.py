from django.shortcuts import render, render_to_response
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from mainsite.models import *
from mainsite.forms import *

#Main, About etc
login_required
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
    return (render(request, 'usersettings.html'))

def Faq(request):
    return (render(request, 'faq.html'))

def UserDoc(request):
    return (render(request, 'userdoc.html'))

def ContigTool(request):
    return (render(request, 'contig.html'))

def Pooling(request):
    return (render(request, 'pooling.html'))

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
 
   
class CosmidDetailView(DetailView):
    model = Cosmid
    template_name = 'cosmid_detail.html'

class SubcloneAssayDetailView(DetailView):
    model = Subclone_Assay
    template_name = 'subclone_assay_detail.html'
    
class CosmidAssayDetailView(DetailView):
    model = Cosmid_Assay
    template_name = 'cosmid_assay_detail.html'

class SubcloneDetailView(DetailView):
    model = Subclone
    template_name = 'subclone_detail.html'
    
class ContigDetailView(DetailView):
    model = Contig
    template_name = 'contig_detail.html'
    
class ContigOrfDetailView(DetailView):
    model = ORF
    template_name = 'orf_detail.html'
  
#edit views (updateview class)  
class CosmidEditView(UpdateView):
    model = Cosmid
    template_name = 'cosmid_edit.html'
    
class SubcloneEditView(UpdateView):
    model = Subclone
    template_name = 'subclone_edit.html'
    
class CosmidAssayEditView(UpdateView):
    model = Cosmid_Assay
    template_name = 'cosmid_assay_edit.html'

class SubcloneAssayEditView(UpdateView):
    model = Subclone_Assay
    template_name = 'subclone_assay_edit.html'
    
class ContigORFEditView(UpdateView):
    model = ORF
    template_name = 'contig_orf_edit.html'

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
  
    
# List views for multi-table views (Kathy)

class CosmidEndTagListView(ListView):
    model = Cosmid
    template_name = 'cosmid_end_tag_all.html'
    

# Create views for adding data to one model (Kathy)

class SubcloneCreateView(CreateView):
    model = Subclone
    template_name = 'subclone_add.html'
    success_url = 'subclone-list'
    
class CosmidAssayCreateView(CreateView):
    model = Cosmid_Assay
    template_name = 'cosmid_assay_add.html'
    success_url = 'cosmid-assay-list'

class SubcloneAssayCreateView(CreateView):
    model = Subclone_Assay
    template_name = 'subclone_assay_add.html'
    success_url = 'subclone-assay-list'
    

# Create views for adding data to multiple models with the same template

def CosmidEndTagCreate(request):
    if request.method == "POST":
        cosmidform = CosmidForm(request.POST, instance=Cosmid())
        endtagform1 = EndTagForm(request.POST, instance=End_Tag())
        endtagform2 = EndTagForm(request.POST, instance=End_Tag())
        if cosmidform.is_valid() and endtagform1.is_valid() and endtagform2.is_valid():
            new_cosmid = cosmidform.save()    
            new_end_tag_1 = endtagform1.save(commit=False)
            new_end_tag_2 = endtagform2.save(commit=False) 
            new_end_tag_1.cosmid = new_cosmid
            new_end_tag_2.cosmid = new_cosmid
            new_end_tag_1.save()
            new_end_tag_2.save()
            return HttpResponseRedirect('/cosmid/')
    else:
        cosmidform = CosmidForm(instance=Cosmid())
        endtagform1 = EndTagForm(instance=End_Tag())
        endtagform2 = EndTagForm(instance=End_Tag())
    return render_to_response('cosmid_end_tag_add.html', {'cosmid_form': cosmidform, 'end_tag_form1': endtagform1, 'end_tag_form2': endtagform2}, context_instance=RequestContext(request))


# List views for lookup tables (Kathy)
class PrimerListView(ListView):
    model = Primer
    template_name = 'primer_all.html'

class HostListView(ListView):
    model = Host
    template_name = 'host_all.html'
    
class ScreenListView(ListView):
    model = Screen
    template_name = 'screen_all.html'
    
class LibraryListView(ListView):
    model = Library
    template_name = 'library_all.html'
    
class ResearcherListView(ListView):
    model = Researcher
    template_name = 'researcher_all.html'

class VectorListView(ListView):
    model = Vector
    template_name = 'vector_all.html'

class PoolListView(ListView):
    model = Pooled_Sequencing
    template_name = 'pool_all.html'
    
class SubstrateListView(ListView):
    model = Substrate
    template_name = 'substrate_all.html'
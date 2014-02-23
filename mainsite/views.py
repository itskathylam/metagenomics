from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from mainsite.models import *
from mainsite.forms import *

#Main, About etc

#@login_required
def MainPage(request):
    template_name = 'index.html'
    return (render(request, 'index.html'))

#@login_required
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

def Contig(request):
    return (render(request, 'contig.html'))

def Pooling(request):
    return (render(request, 'pooling.html'))

#detail views

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
    
class ORFContigListView(ListView):
    model = Contig_ORF_Join
    template_name = 'orf_contig_all.html'
    
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

# Add to Cosmid and End_Tag tables (Kathy)
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
                    end_tag_formset.save
                    return HttpResponseRedirect('/cosmid/') 
        
    else:
        cosmid_form = CosmidForm(instance=Cosmid())
        end_tag_formset = EndTagFormSet(instance=Cosmid())
    return render_to_response('cosmid_end_tag_add.html', {'cosmid_form': cosmid_form, 'end_tag_formset': end_tag_formset}, context_instance=RequestContext(request))

    
# Add to ORF and Contig-ORF-Join tables (Kathy)
def ORFContigCreate(request):
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
                #new_contig_orf.orf = new_orf
                #new_contig_orf.start = contig_seq.index(orf_seq)
                #new_contig_orf.stop = new_contig_orf.start + len(orf_seq)
                #new_contig_orf.db_generated = "FALSE"
                #new_contig_orf.save()
                
                return HttpResponseRedirect('/orfcontig/')
            else:
                return HttpResponseRedirect('/')
    else:
        contig_orf_form = ContigORFJoinForm(instance=Contig_ORF_Join())
        orf_form = ORFForm(instance=ORF())
    return render_to_response('orf_contig_add.html', {'contig_orf_form': contig_orf_form, 'orf_form': orf_form}, context_instance=RequestContext(request))














from django.shortcuts import render, render_to_response
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

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
  
#edit views (updateview class)  
class CosmidEditView(UpdateView):
    model = Cosmid
    template_name = 'cosmid_edit.html'

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

def CosmidEndTagCreate(CreateView):
    model = Cosmid
    template_name = 'cosmid_end_tag_add.html'
    success_url = 'cosmid-end-tag-list'


















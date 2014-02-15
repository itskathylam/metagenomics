from django.shortcuts import render
from django.views.generic import ListView, CreateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


from mainsite.models import *

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

class CosmidListView(ListView):
    model = Cosmid
    template_name = 'cosmid_all.html'
    


# Create views for adding data to one model (Kathy)

class PrimerCreateView(CreateView):
    model = Primer
    fields = ['primer_name', 'primer_sequence']
    template_name = 'primer_add.html'
    
    def get_success_url(self):
        return reverse('primer-list')
    
class HostCreateView(CreateView):
    model = Host
    template_name = 'host_add.html'
    
    def get_success_url(self):
        return reverse('host-list')
    
class ScreenCreateView(CreateView):
    model = Screen
    template_name = 'screen_add.html'
    
    def get_success_url(self):
        return reverse('screen-list')

class ResearcherCreateView(CreateView):
    model = Researcher
    template_name = 'researcher_add.html'
    
    def get_success_url(self):
        return reverse('researcher-list')
    
class SubstrateCreateView(CreateView):
    model = Substrate
    template_name = 'substrate_add.html'
    
    def get_success_url(self):
        return reverse('substrate-list')

class VectorCreateView(CreateView):
    model = Vector
    template_name = 'vector_add.html'
    
    def get_success_url(self):
        return reverse('vector-list')
    
class PooledSequencingCreateView(CreateView):
    model = Pooled_Sequencing
    template_name = 'pool_add.html'
    
    def get_success_url(self):
        return reverse('pool-list')

class LibraryCreateView(CreateView):
    model = Library
    template_name = 'library_add.html'
    
    def get_success_url(self):
        return reverse('library-list')
    
class SubcloneCreateView(CreateView):
    model = Subclone
    template_name = 'subclone_add.html'
    
    def get_success_url(self):
        return reverse('subclone-list')
    
class CosmidAssayCreateView(CreateView):
    model = Cosmid_Assay
    template_name = 'cosmid_assay_add.html'
    
    def get_success_url(self):
        return reverse('cosmid-assay-list')

class SubcloneAssayCreateView(CreateView):
    model = Subclone_Assay
    template_name = 'subclone_assay_add.html'
    
    def get_success_url(self):
        return reverse('subclone-assay-list')
    
    
# Create views for adding data to multiple models with the same add form




















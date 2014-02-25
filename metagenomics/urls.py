from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
admin.autodiscover()
from mainsite.views import *

urlpatterns = patterns('',
    # Admin and Static Pages (Main, About, and Logging in and Out) 
    url(r'^$', MainPage, name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/', AboutPage, name='about'),
    url(r'^login/', 'django.contrib.auth.views.login'),
    url(r'^logout/', Logout, name='logout'),
    url(r'^user/settings/', UserSettings, name= 'usersettings'),
    url(r'^help/faq', Faq, name='faq'),
    url(r'^help/userdoc', UserDoc, name='userdoc'),
    
    #login_required( ) - add to all views below
    
    #Tools Views
    url(r'^tools/contig', ContigTool, name='contig'),
    url(r'^tools/pooling', Pooling, name='pool'),
    
    #Detail views
    url(r'^cosmid/(?P<cosmid_name>\w+)/$', CosmidDetail, name='cosmid-detail'),
    url(r'^assay/subclone/(?P<pk>\d+)/$', SubcloneAssayDetailView.as_view(), name='sublcone-assay-detail'),
    url(r'^assay/cosmid/(?P<pk>\d+)/$', CosmidAssayDetailView.as_view(), name='cosmid-assay-detail'),
    url(r'^subclone/(?P<pk>\d+)/$', SubcloneDetailView.as_view(), name='subclone-detail'),
    url(r'^contig/(?P<pk>\d+)/$', ContigDetailView.as_view(), name='contig-detail'),
    url(r'^contig-orf/(?P<pk>\d+)/$', ContigOrfDetailView.as_view(), name='contig-orf-detail'),
    
    #Edit views (Updateviews)
    url(r'^edit/cosmid/(?P<pk>\d+)$', CosmidEditView.as_view(), name='cosmid-edit'),
    url(r'^edit/subclone/(?P<pk>\d+)$', SubcloneEditView.as_view(), name='subclone-edit'),
    url(r'^edit/assay/cosmid/(?P<pk>\d+)$', CosmidAssayEditView.as_view(), name='cosmid-assay-edit'),
    url(r'^edit/assay/subclone/(?P<pk>\d+)$', SubcloneAssayEditView.as_view(), name='subclone-assay-edit'),
    url(r'^edit/contig-orf/(?P<pk>\d+)$', ContigORFEditView.as_view(), name='contig-orf-edit'),
    #Search views
    #url(r'^search/cosmid/$', CosmidSearchView),
    #url(r'^search/subclone/$', SubcloneSearchView),
    #url(r'^search/assay/$', AssaySearchView),
    #url(r'^search/orf/$', ORFSearchView),
    
    # listviews for lookup tables 
    url(r'^primer/', PrimerListView.as_view(), name='primer-list'),
    url(r'^host/', HostListView.as_view(), name='host-list'),
    url(r'^screen/', ScreenListView.as_view(), name='screen-list'),
    url(r'^library/', LibraryListView.as_view(), name='library-list'),
    url(r'^researcher/', ResearcherListView.as_view(), name='researcher-list'),
    url(r'^vector/', VectorListView.as_view(), name='vector-list'),
    url(r'^pool/', PoolListView.as_view(), name='pool-list'),
    url(r'^substrate/', SubstrateListView.as_view(), name='substrate-list'),
    
    # listviews for nonlookup tables
    url(r'^subclone/$', SubcloneListView.as_view(), name='subclone-list'),
    url(r'^assay/cosmid/$', CosmidAssayListView.as_view(), name='cosmid-assay-list'),
    url(r'^assay/subclone/$', SubcloneAssayListView.as_view(), name='subclone-assay-list'),
    url(r'^orf/$', ORFListView.as_view(), name='orf-list'),
    
    # listviews for multiple-table-based views
    url(r'^cosmid/$', CosmidEndTagListView.as_view(), name='cosmid-end-tag-list'), # for cosmid and endtags (Kathy)
    
    # createviews - form to add data to database table  
    url(r'^add/subclone/$', SubcloneCreateView.as_view(), name='subclone-add'),
    url(r'^add/assay/cosmid/$', CosmidAssayCreateView.as_view(), name='cosmid-assay-add'),
    url(r'^add/assay/subclone/$', SubcloneAssayCreateView.as_view(), name='subclone-assay-add'),
    
    # createviews for adding data to multiple tables at once
    url(r'^add/cosmid/$', CosmidEndTagCreate, name='cosmid-end-tag-add'),
    
    url(r'^export/primer', primer_queryset),
    url(r'^export/host', host_queryset),
    url(r'^export/screen', screen_queryset),
    url(r'^export/library', library_queryset),
    url(r'^export/researcher', researcher_queryset),
    url(r'^export/vector', vector_queryset),
    url(r'^export/pool', pool_queryset),
    url(r'^export/substrate', substrate_queryset),


        #url(r'^fasta/', FAOutput)
)
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
admin.autodiscover()
from mainsite.views import *

urlpatterns = patterns('',
    #Admin and Static Pages (Main, About, and Logging in and Out) 
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
    
    url(r'^blast/search', BlastSearch, name='blast'),
    url(r'^blast/results', BlastResults, name='blast-results'),
    
    #Detail views
    url(r'^cosmid/(?P<cosmid_name>[\w-]+)/$', CosmidDetail, name='cosmid-detail'),
    url(r'^assay/subclone/(?P<pk>\d+)/$', SubcloneAssayDetailView.as_view(), name='sublcone-assay-detail'),
    url(r'^assay/cosmid/(?P<pk>\d+)/$', CosmidAssayDetailView.as_view(), name='cosmid-assay-detail'),
    url(r'^subclone/(?P<pk>\d+)/$', SubcloneDetailView.as_view(), name='subclone-detail'),
    url(r'^contig/(?P<contig_name>[\w-]+)/$', ContigDetail, name='contig-detail'),
    url(r'^orf/(?P<pk>\d+)/$', OrfDetailView.as_view(), name='orf-detail'),
    url(r'^vector/(?P<pk>\d+)/$', VectorDetailView.as_view(), name='vector-detail'),
    
    #Edit views (Updateviews)
    url(r'^edit/cosmid/(?P<pk>\d+)$', permission_required('mainsite.cosmid.can_change_cosmid')(CosmidEditView.as_view()), name='cosmid-edit'),
    url(r'^edit/subclone/(?P<pk>\d+)$', permission_required('mainsite.cosmid.can_change_subclone')(SubcloneEditView.as_view()), name='subclone-edit'),
    url(r'^edit/assay/cosmid/(?P<pk>\d+)$', permission_required('mainsite.cosmid.can_change_cosmid_assay')(CosmidAssayEditView.as_view()), name='cosmid-assay-edit'),
    url(r'^edit/assay/subclone/(?P<pk>\d+)$', permission_required('mainsite.cosmid.can_change_subclone_assay')(SubcloneAssayEditView.as_view()), name='subclone-assay-edit'),
    url(r'^edit/orf/(?P<pk>\d+)$', permission_required('mainsite.cosmid.can_change_orf')(ORFEditView.as_view()), name='orf-edit'),
    url(r'^edit/contig/(?P<pk>\d+)$', permission_required('mainsite.cosmid.can_change_contig')(ContigEditView.as_view()), name='contig-edit'),
    
    #Delete views (DeleteViews)
    url(r'^delete/contig-orf/(?P<pk>\d+)$', ContigORFDeleteView.as_view(), name='contig-orf-delete'),
    
    #Search views
    url(r'^search/cosmid/$', CosmidSearchView, name='cosmid-search'),
    url(r'^results/cosmid?page=n/', CosmidResults, name='cosmid-results'),
    url(r'^search/subclone/$', SubcloneSearchView, name='subclone-search'),
    url(r'^results/subclone/', SubcloneResults, name='subclone-results'),
    url(r'^search/assay/subclone$', SubcloneAssaySearchView, name = 'subclone-assay-search'),
    url(r'^results/assay/subclone$', SubcloneAssayResults, name='subclone-assay-results'),
    url(r'^search/assay/cosmid$', CosmidAssaySearchView, name = 'cosmid-assay-search'),
    url(r'^results/assay/cosmid$', CosmidAssayResults, name='cosmid-assay-results'),
    url(r'^search/orf/$', OrfSearchView, name='orf-search'),
    url(r'^results/orf/$', OrfResults, name = 'orf-results'),
    
    url(r'^search/$', SearchAll, name = 'all-search'),
    url(r'^results/$', AllResults, name = 'all-results'),
    
    #listviews for lookup tables 
    url(r'^primer/$', PrimerListView.as_view(), name='primer-list'),
    url(r'^host/$', HostListView.as_view(), name='host-list'),
    url(r'^screen/$', ScreenListView.as_view(), name='screen-list'),
    url(r'^library/$', LibraryListView.as_view(), name='library-list'),
    url(r'^researcher/$', ResearcherListView.as_view(), name='researcher-list'),
    url(r'^vector/$', VectorListView.as_view(), name='vector-list'),
    url(r'^pool?page=n/$', PoolListView.as_view(), name='pool-list'),
    url(r'^substrate/$', SubstrateListView.as_view(), name='substrate-list'),
    url(r'^antibiotic/$', AntibioticListView.as_view(), name='antibiotic-list'),
    
    #listviews for nonlookup tables
    url(r'^subclone/$', SubcloneListView.as_view(), name='subclone-list'),
    url(r'^assay/cosmid/$', CosmidAssayListView.as_view(), name='cosmid-assay-list'),
    url(r'^assay/subclone/$', SubcloneAssayListView.as_view(), name='subclone-assay-list'),
    url(r'^orf/$', ORFListView.as_view(), name='orf-list'),
    url(r'^contig/$', ContigListView.as_view(), name='contig-list'),
    
    #listviews for multiple-table-based views
    url(r'^cosmid/$', CosmidEndTagListView.as_view(), name='cosmid-end-tag-list'), # for cosmid and endtags (Kathy)
    url(r'^orfcontig/$', ORFContigListView.as_view(), name='orf-contig-list'), # not a useful view; may remove (Kathy)
    
    #createviews - form to add data to database table  
    url(r'^add/subclone/$', permission_required('mainsite.cosmid.can_add_subclone')(SubcloneCreateView.as_view()), name='subclone-add'),
    url(r'^add/assay/cosmid/$', permission_required('mainsite.cosmid.can_add_cosmid_assay')(CosmidAssayCreateView.as_view()), name='cosmid-assay-add'),
    url(r'^add/assay/subclone/$', permission_required('mainsite.cosmid.can_add_subclone_assay')(SubcloneAssayCreateView.as_view()), name='subclone-assay-add'),
    
    #createviews for adding data to multiple tables at once
    url(r'^add/cosmid/$', CosmidEndTagCreate, name='cosmid-end-tag-add'),
    url(r'^add/orfcontig/$', ORFContigCreate, name='orf-contig-add'),
    url(r'^add/contigpool/$', ContigPoolCreate, name='contig-pool-add'),
    
    
    #export URLS
    url(r'^export/primer', primer_queryset),
    url(r'^export/host', host_queryset),
    url(r'^export/screen', screen_queryset),
    url(r'^export/library', library_queryset),
    url(r'^export/researcher', researcher_queryset),
    url(r'^export/vector', vector_queryset),
    url(r'^export/pool', pool_queryset),
    url(r'^export/substrate', substrate_queryset),


)
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
admin.autodiscover()
from mainsite.views import *
from django.contrib.auth.views import login, password_change

urlpatterns = patterns('',
    #Admin and Static Pages (Main, About, and Logging in and Out) 
    url(r'^$', MainPage, name='home'),
    url(r'^admin/', include(admin.site.urls)), #can not add a $ to end of the regular expression here
    url(r'^about/$', AboutPage, name='about'),
    
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', Logout, name='logout'),
    url(r'^user/settings/$', UserSettings, name='usersettings'),
    url(r'^user/password/change/$', 'django.contrib.auth.views.password_change'),
    url(r'^user/password/changed/$', 'django.contrib.auth.views.password_change_done', name="password_change_done"),
    
    url(r'^help/faq/$', Faq, name='faq'),
    url(r'^help/userdoc/$', UserDoc, name='userdoc'),
    
    
    #Tools Views
    url(r'^tools/contig/$', ContigTool, name='contig'),
    url(r'^tools/annotation/$', AnnotationTool, name='annotation'),
    url(r'^tools/annotation/results/$', AnnotationToolResults, name='annotation-results'),
    url(r'^tools/contig/results/$', ContigToolResults, name='contig-tool-results'),

    
    #Detail views
    url(r'^cosmid/(?P<cosmid_name>.*)/$', CosmidDetail, name='cosmid-detail'),
    url(r'^contig/(?P<contig_name>[\w-]+)/$', ContigDetail, name='contig-detail'),
    url(r'^orf/(?P<pk>\d+)/$', OrfDetail, name='orf-detail'),
    url(r'^assay/subclone/(?P<pk>\d+)/$', login_required(SubcloneAssayDetailView.as_view()), name='sublcone-assay-detail'),
    url(r'^assay/cosmid/(?P<pk>\d+)/$', login_required(CosmidAssayDetailView.as_view()), name='cosmid-assay-detail'),
    url(r'^subclone/(?P<subclone_name>.*)/$', login_required(SubcloneDetailView.as_view()), name='subclone-detail'),
    url(r'^vector/(?P<pk>\d+)/$', login_required(VectorDetailView.as_view()), name='vector-detail'),
    
    #Edit views (Updateviews)
    url(r'^edit/cosmid/(?P<cosmid_name>.*)/$', permission_required('mainsite.cosmid.can_change_cosmid')(CosmidEditView.as_view()), name='cosmid-edit'),
    url(r'^edit/subclone/(?P<subclone_name>.*)$', permission_required('mainsite.cosmid.can_change_subclone')(SubcloneEditView.as_view()), name='subclone-edit'),
    url(r'^edit/assay/cosmid/(?P<pk>\d+)$', permission_required('mainsite.cosmid.can_change_cosmid_assay')(CosmidAssayEditView.as_view()), name='cosmid-assay-edit'),
    url(r'^edit/assay/subclone/(?P<pk>\d+)$', permission_required('mainsite.cosmid.can_change_subclone_assay')(SubcloneAssayEditView.as_view()), name='subclone-assay-edit'),
    url(r'^edit/orf/(?P<pk>\d+)$', permission_required('mainsite.cosmid.can_change_orf')(ORFEditView.as_view()), name='orf-edit'),
    url(r'^edit/contig/(?P<pk>\d+)$', permission_required('mainsite.cosmid.can_change_contig')(ContigEditView.as_view()), name='contig-edit'),
    url(r'^edit/cosmid/endtags/(?P<pk>\d+)$', permission_required(CosmidEndTagEditView.as_view()), name='cosmid-end-tag-edit'), 
    
    #Delete views (DeleteViews)
    url(r'^delete/contig-orf/(?P<pk>\d+)$', login_required(ContigORFDeleteView.as_view()), name='contig-orf-delete'),
    
    #Search views
    url(r'^search/cosmid/$', CosmidSearchView, name='cosmid-search'),
    url(r'^results/cosmid/$', CosmidResults, name='cosmid-results'),
    url(r'^results/basic/cosmid$', CosmidBasicResults, name = 'cosmid-basic-results'),
    url(r'^search/subclone/$', SubcloneSearchView, name='subclone-search'),
    url(r'^results/subclone/$', SubcloneResults, name='subclone-results'),
    url(r'^results/basic/subclone/$', SubcloneBasicResults, name='subclone-basic-results'),
    
    url(r'^search/assay/subclone$', SubcloneAssaySearchView, name = 'subclone-assay-search'),
    url(r'^results/assay/subclone$', SubcloneAssayResults, name='subclone-assay-results'),
    url(r'^results/basic/assay$', SubcloneAssayBasicResults, name='subclone-assay-basic-results'), #need to add the view and template for this
    
    url(r'^search/assay/cosmid$', CosmidAssaySearchView, name = 'cosmid-assay-search'),
    url(r'^results/assay/cosmid$', CosmidAssayResults, name='cosmid-assay-results'),
    url(r'^results/basic/assay/cosmid$', CosmidAssayBasicResults, name='cosmid-assay-basic-results'),
    
    url(r'^search/orf/$', OrfSearchView, name='orf-search'),
    url(r'^results/orf/$', OrfResults, name = 'orf-results'),
    url(r'^results/basic/orf$', OrfBasicResults, name = 'orf-basic-results'),
    
    url(r'^search/contig/$', ContigSearchView, name='contig-search'),
    url(r'^results/contig/$', ContigResults, name='contig-results'),
    url(r'^results/basic/contig$', ContigBasicResults, name = 'contig-basic-results'),
    
    url(r'^search/blast/$', BlastSearch, name='blast-search'),
    url(r'^results/blast/', BlastResults, name='blast-results'),
    
    #listviews for lookup tables 
    url(r'^primer/$', login_required(PrimerListView.as_view()), name='primer-list'),
    url(r'^host/$', login_required(HostListView.as_view()), name='host-list'),
    url(r'^screen/$', login_required(ScreenListView.as_view()), name='screen-list'),
    url(r'^library/$', login_required(LibraryListView.as_view()), name='library-list'),
    url(r'^researcher/$', login_required(ResearcherListView.as_view()), name='researcher-list'),
    url(r'^vector/$', login_required(VectorListView.as_view()), name='vector-list'),
    url(r'^pool?page=n/$', login_required(PoolListView.as_view()), name='pool-list'),
    url(r'^substrate/$', login_required(SubstrateListView.as_view()), name='substrate-list'),
    url(r'^antibiotic/$', login_required(AntibioticListView.as_view()), name='antibiotic-list'),
    
    #listviews for nonlookup tables
    url(r'^subclone/$', login_required(SubcloneListView.as_view()), name='subclone-list'),
    url(r'^assay/cosmid/$', login_required(CosmidAssayListView.as_view()), name='cosmid-assay-list'),
    url(r'^assay/subclone/$', login_required(SubcloneAssayListView.as_view()), name='subclone-assay-list'),
    url(r'^orf/$', login_required(ORFListView.as_view()), name='orf-list'),
    url(r'^contig/$', login_required(ContigListView.as_view()), name='contig-list'),
    
    #listviews for multiple-table-based views
    url(r'^cosmid/$', login_required(CosmidEndTagListView.as_view()), name='cosmid-end-tag-list'), # for cosmid and endtags (Kathy)
    url(r'^orfcontig/$', login_required(ORFContigListView.as_view()), name='orf-contig-list'), # not a useful view? may remove (Kathy)
    
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
    url(r'^export/antibiotic', antibiotic_queryset),
    url(r'^export/host', host_queryset),
    url(r'^export/screen', screen_queryset),
    url(r'^export/library', library_queryset),
    url(r'^export/researcher', researcher_queryset),
    url(r'^export/vector', vector_queryset),
    url(r'^export/pool', pool_queryset),
    url(r'^export/substrate', substrate_queryset),
    url(r'^export/subclone', subclone_queryset),
    url(r'^export/cosmid_assay', cosmid_assay_queryset),
    url(r'^export/subclone_assay', subclone_assay_queryset),
    url(r'^export/orf', orf_queryset),
    url(r'^export/contig', contig_queryset),
    url(r'^export/cosmid_endtag', cosmid_endtag_queryset),
    url(r'^export/orf_contig', orf_contig_queryset),
   
    
)
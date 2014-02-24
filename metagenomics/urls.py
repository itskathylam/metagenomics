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
    url(r'^cosmid/(?P<cosmid_name>[\w-]+)/$', CosmidDetail, name='cosmid-detail'),
    url(r'^assay/subclone/(?P<pk>\d+)/$', SubcloneAssayDetailView.as_view(), name='sublcone-assay-detail'),
    url(r'^assay/cosmid/(?P<pk>\d+)/$', CosmidAssayDetailView.as_view(), name='cosmid-assay-detail'),
    url(r'^subclone/(?P<pk>\d+)/$', SubcloneDetailView.as_view(), name='subclone-detail'),
    url(r'^contig/(?P<contig_name>[\w-]+)/$', ContigDetail, name='contig-detail'),
    url(r'^orf/(?P<pk>\d+)/$', OrfDetailView.as_view(), name='orf-detail'),
    
    #Edit views (Updateviews)
    url(r'^edit/cosmid/(?P<pk>\d+)$', CosmidEditView.as_view(), name='cosmid-edit'),
    url(r'^edit/subclone/(?P<pk>\d+)$', SubcloneEditView.as_view(), name='subclone-edit'),
    url(r'^edit/assay/cosmid/(?P<pk>\d+)$', CosmidAssayEditView.as_view(), name='cosmid-assay-edit'),
    url(r'^edit/assay/subclone/(?P<pk>\d+)$', SubcloneAssayEditView.as_view(), name='subclone-assay-edit'),
    url(r'^edit/orf/(?P<pk>\d+)$', ORFEditView.as_view(), name='orf-edit'),
    
    #Search views
    url(r'^search/cosmid/$', CosmidSearchView, name='cosmid-search'),
    url(r'^results/cosmid/', CosmidResults, name='cosmid-results'),
    url(r'^search/subclone/$', SubcloneSearchView, name='subclone-search'),
    url(r'^results/subclone/', SubcloneResults, name='subclone-results'),
    #url(r'^search/assay/$', AssaySearchView),
    #url(r'^search/orf/$', ORFSearchView),
    
    # listviews for lookup tables 
    url(r'^primer/$', PrimerListView.as_view(), name='primer-list'),
    url(r'^host/$', HostListView.as_view(), name='host-list'),
    url(r'^screen/$', ScreenListView.as_view(), name='screen-list'),
    url(r'^library/$', LibraryListView.as_view(), name='library-list'),
    url(r'^researcher/$', ResearcherListView.as_view(), name='researcher-list'),
    url(r'^vector/$', VectorListView.as_view(), name='vector-list'),
    url(r'^pool/$', PoolListView.as_view(), name='pool-list'),
    url(r'^substrate/$', SubstrateListView.as_view(), name='substrate-list'),
    
    # listviews for nonlookup tables
    url(r'^subclone/$', SubcloneListView.as_view(), name='subclone-list'),
    url(r'^assay/cosmid/$', CosmidAssayListView.as_view(), name='cosmid-assay-list'),
    url(r'^assay/subclone/$', SubcloneAssayListView.as_view(), name='subclone-assay-list'),
    url(r'^orf/$', ORFListView.as_view(), name='orf-list'),
    url(r'^contig/$', ContigListView.as_view(), name='contig-list'),
    
    # listviews for multiple-table-based views
    url(r'^cosmid/$', CosmidEndTagListView.as_view(), name='cosmid-end-tag-list'), # for cosmid and endtags (Kathy)
    url(r'^orfcontig/$', ORFContigListView.as_view(), name='orf-contig-list'), # not a useful view; may remove (Kathy)
    
    # createviews - form to add data to database table  
    url(r'^add/subclone/$', SubcloneCreateView.as_view(), name='subclone-add'),
    url(r'^add/assay/cosmid/$', CosmidAssayCreateView.as_view(), name='cosmid-assay-add'),
    url(r'^add/assay/subclone/$', SubcloneAssayCreateView.as_view(), name='subclone-assay-add'),
    
    # createviews for adding data to multiple tables at once
    url(r'^add/cosmid/$', CosmidEndTagCreate, name='cosmid-end-tag-add'),
    url(r'^add/orfcontig/$', ORFContigCreate, name='orf-contig-add'),
    url(r'^add/contigpool/$', ContigPoolCreate, name='contig-pool-add'),
)
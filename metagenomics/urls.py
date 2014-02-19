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
    
    url(r'^tools/contig', Contig, name='contig'),
    url(r'^tools/pooling', Pooling, name='pool'),
    
    #Detail views
    url(r'^cosmid/(?P<pk>\d+)/$', CosmidDetailView.as_view(), name='cosmid-detail'),
    url(r'^assay/subclone/(?P<pk>\d+)/$', SubcloneAssayDetailView.as_view(), name='sublcone-assay-detail'),
    
    #Edit views (Updateviews)
    url(r'^cosmid/(?P<pk>\d+)/edit$', CosmidEditView.as_view(), name='cosmid-edit'),
    
    
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
    url(r'^subclone/', SubcloneListView.as_view(), name='subclone-list'),
    url(r'^assay/cosmid/', CosmidAssayListView.as_view(), name='cosmid-assay-list'),
    url(r'^assay/subclone/$', SubcloneAssayListView.as_view(), name='subclone-assay-list'),
    url(r'^orf/', ORFListView.as_view(), name='orf-list'),

    # listviews for multiple-table-based views
    url(r'^cosmid/', CosmidEndTagListView.as_view(), name='cosmid-end-tag-list'), # for cosmid and endtags (Kathy)
    
    # createviews - form to add data to database table  
    url(r'^add/subclone/$', SubcloneCreateView.as_view(), name='subclone-add'),
    url(r'^add/assay/cosmid/$', CosmidAssayCreateView.as_view(), name='cosmid-assay-add'),
    url(r'^add/assay/subclone/$', SubcloneAssayCreateView.as_view(), name='subclone-assay-add'),
    
    # createviews for adding data to multiple tables at once
    url(r'^add/cosmid/$', CosmidEndTagCreate, name='cosmid-end-tag-add'),
    
)
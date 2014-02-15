from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
admin.autodiscover()

# for lookup table views
from mainsite.views import *

urlpatterns = patterns('',
    #Admin and Static Pages (Main, About, and Logging in and Out)
    url(r'^$', MainPage, name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/', AboutPage, name='about'),
    url(r'^login/', 'django.contrib.auth.views.login'),
    url(r'^logout/', Logout, name='logout'),
    url(r'^user/settings/', UserSettings, name= 'usersettings'),
    
    #login_required( ) - add to all views below
    
    # lookup table listviews (Kathy)
    url(r'^primer/', PrimerListView.as_view(), name='primer-list'),
    url(r'^host/', HostListView.as_view(), name='host-list'),
    url(r'^screen/', ScreenListView.as_view(), name='screen-list'),
    url(r'^library/', LibraryListView.as_view(), name='library-list'),
    url(r'^researcher/', ResearcherListView.as_view(), name='researcher-list'),
    url(r'^vector/', VectorListView.as_view(), name='vector-list'),
    url(r'^pool/', PoolListView.as_view(), name='pool-list'),
    url(r'^substrate/', SubstrateListView.as_view(), name='substrate-list'),
    
    # nonlookup table listviews (Kathy)
    url(r'^subclone/', SubcloneListView.as_view(), name='subclone-list'),
    url(r'^assay/cosmid/', CosmidAssayListView.as_view(), name='cosmid-assay-list'),
    url(r'^assay/subclone/', SubcloneAssayListView.as_view(), name='subclone-assay-list'),
    url(r'^orf/', ORFListView.as_view(), name='orf-list'),
    
    # multiple-table-based views
    url(r'^cosmid/', CosmidListView.as_view(), name='cosmid-list'), # for cosmid and endtags
    
    # createviews (Kathy) Form to add data to database
    url(r'^add/primer/$', PrimerCreateView.as_view(), name='primer-add'),
    url(r'^add/host/$', HostCreateView.as_view(), name='host-add'),
    url(r'^add/screen/$', ScreenCreateView.as_view(), name='screen-add'),
    url(r'^add/library/$', LibraryCreateView.as_view(), name='library-add'),
    url(r'^add/researcher/$', ResearcherCreateView.as_view(), name='researcher-add'),
    url(r'^add/substrate/$', SubstrateCreateView.as_view(), name='substrate-add'),
    url(r'^add/vector/$', VectorCreateView.as_view(), name='vector-add'),
    url(r'^add/pool/$', PooledSequencingCreateView.as_view(), name='pool-add'),
    url(r'^add/subclone/$', SubcloneCreateView.as_view(), name='subclone-add'),
    url(r'^add/assay/cosmid/$', CosmidAssayCreateView.as_view(), name='cosmid-assay-add'),
    url(r'^add/assay/subclone/$', SubcloneAssayCreateView.as_view(), name='subclone-assay-add'),
)
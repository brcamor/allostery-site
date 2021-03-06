from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'edge.views.home_page', name='home'),
    url(r'^home', 'edge.views.home_page', name='home'),
    url(r'^chains', 'edge.views.chain_setup', name='chain_setup'), 
    url(r'^hetatms', 'edge.views.hetatm_setup', name='hetatm_setup'),
    url(r'^source', 'edge.views.source_setup', name='source_setup'),
    url(r'^bond_results', 'edge.views.bond_results', name='bond_results'),
    url(r'^atom_results', 'edge.views.atom_results', name='atom_results'),   
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))

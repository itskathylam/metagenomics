from django.contrib import admin
from mainsite.models import *
import reversion

class EndTagAdmin(admin.TabularInline):
    model = End_Tag
    max_num = 2
    verbose_name_plural = 'End Tags'


class CosmidAdmin(admin.ModelAdmin):
    model = Cosmid
    list_display = ('cosmid_name', 'researcher', 'library', 'pool')
    search_fields = ['cosmid_name']
    inlines = [EndTagAdmin]


class Subclone_Assay_Admin(reversion.VersionAdmin):
    pass  

admin.site.register(Cosmid, CosmidAdmin)
#admin.site.register(End_Tag), EndTagAdmin)

admin.site.register(Contig)
admin.site.register(ORF)
admin.site.register(Contig_ORF_Join)

admin.site.register(Subclone)
admin.site.register(Cosmid_Assay)
admin.site.register(Subclone_Assay, Subclone_Assay_Admin)

admin.site.register(Host)
admin.site.register(Screen)
admin.site.register(Vector)
admin.site.register(Library)
admin.site.register(Researcher)
admin.site.register(Pooled_Sequencing)
admin.site.register(Primer)
admin.site.register(Substrate)
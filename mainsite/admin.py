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

class Contig_Admin(reversion.VersionAdmin):
    pass

class ORF_Admin(reversion.VersionAdmin):
    pass

class Contig_ORF_Join_Admin(reversion.VersionAdmin):
    pass

class Subclone_Admin(reversion.VersionAdmin):
    pass

class Cosmid_Assay_Admin(reversion.VersionAdmin):
    pass

class Host_Admin(reversion.VersionAdmin):
    pass

class Screen_Admin(reversion.VersionAdmin):
    pass

class Vector_Admin(reversion.VersionAdmin):
    pass

class Library_Admin(reversion.VersionAdmin):
    pass

class Researcher_Admin(reversion.VersionAdmin):
    pass

class Pooled_Sequencing_Admin(reversion.VersionAdmin):
    pass

class Primer_Admin(reversion.VersionAdmin):
    pass

class Substrate_Admin(reversion.VersionAdmin):
    pass

admin.site.register(Cosmid, CosmidAdmin)
#admin.site.register(End_Tag), EndTagAdmin)

admin.site.register(Contig, Contig_Admin)
admin.site.register(ORF, ORF_Admin)
admin.site.register(Contig_ORF_Join, Contig_ORF_Join_Admin)

admin.site.register(Subclone, Subclone_Admin)
admin.site.register(Cosmid_Assay, Cosmid_Assay_Admin)
admin.site.register(Subclone_Assay, Subclone_Assay_Admin)

admin.site.register(Host, Host_Admin)
admin.site.register(Screen, Screen_Admin)
admin.site.register(Vector, Vector_Admin)
admin.site.register(Library, Library_Admin)
admin.site.register(Researcher, Researcher_Admin)
admin.site.register(Pooled_Sequencing, Pooled_Sequencing_Admin)
admin.site.register(Primer, Primer_Admin)
admin.site.register(Substrate, Substrate_Admin)
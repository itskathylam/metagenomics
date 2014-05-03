from django.contrib import admin
from mainsite.models import *
import reversion

class EndTagAdmin(admin.TabularInline):
    model = End_Tag
    max_num = 0
    verbose_name_plural = 'End Tags'

class CosmidAdmin(reversion.VersionAdmin): #admin.ModelAdmin):
    #pass
    model = Cosmid
    list_display = ('cosmid_name', 'researcher', 'host', 'screen', 'ec_collection', 'original_media', 'lab_book_ref', 'cosmid_comments', 'library', 'pool')
    search_fields = ['cosmid_name', 'researcher', 'host', 'screen', 'ec_collection', 'original_media', 'lab_book_ref', 'cosmid_comments', 'library', 'pool']
    inlines = [EndTagAdmin]

class Subclone_Assay_Admin(reversion.VersionAdmin):
    list_display = ('subclone', 'host', 'substrate', 'antibiotic', 'researcher', 'subclone_km', 'subclone_temp', 'subclone_ph', 'subclone_comments')
    search_fields = ['subclone', 'host', 'substrate', 'antibiotic', 'researcher', 'subclone_km', 'subclone_temp', 'subclone_ph', 'subclone_comments']
    
class Contig_Admin(reversion.VersionAdmin):
    list_display = ('contig_name', 'contig_accession', 'blast_hit_accession', 'pool')
    search_fields = ['contig_name', 'cosmid', 'contig_accession']
    
class ORF_Admin(reversion.VersionAdmin):
    list_display = ('id', 'annotation')
    search_fields = ['id', 'annotation']
    
class Contig_ORF_Join_Admin(reversion.VersionAdmin):
    list_display = ('id', 'contig', 'orf', 'start', 'stop', 'orf_accession', 'predicted', 'prediction_score')
    
class Subclone_Admin(reversion.VersionAdmin):
    list_display = ('subclone_name', 'cosmid', 'orf', 'vector', 'researcher', 'ec_collection', 'primer1_name', 'primer2_seq', 'primer1_name', 'primer2_seq')
    search_fields = ['subclone_name', 'cosmid', 'orf', 'vector', 'researcher', 'ec_collection', 'primer1_name', 'primer2_seq', 'primer1_name', 'primer2_seq']

class Cosmid_Assay_Admin(reversion.VersionAdmin):
    list_display = ('cosmid', 'host', 'substrate', 'antibiotic', 'researcher', 'cosmid_km', 'cosmid_temp', 'cosmid_ph', 'cosmid_comments')
    search_fields = ['cosmid', 'host', 'substrate', 'antibiotic', 'researcher', 'cosmid_km', 'cosmid_temp', 'cosmid_ph', 'cosmid_comments']
    
class Host_Admin(reversion.VersionAdmin):
    search_fields = ('host_name',)
    
class Screen_Admin(reversion.VersionAdmin):
    search_fields = ['screen_name']

class Vector_Admin(reversion.VersionAdmin):
    list_display = ('vector_name', 'vector_type', 'vector_accession', 'description')
    search_fields = ['vector_name', 'vector_type', 'vector_accession', 'description']

class Library_Admin(reversion.VersionAdmin):
    list_display = ('library_name', 'biosample', 'vector', 'number_clones', 'insert_size')
    search_fields = ['library_name', 'biosample', 'vector', 'number_clones', 'insert_size']
    
class Researcher_Admin(reversion.VersionAdmin):
    search_fields = ['researcher_name']

class Pooled_Sequencing_Admin(reversion.VersionAdmin):
    list_display = ('service_provider', 'ncbi_sra_accession', 'max_number', 'pool_comments')
    search_fields = ['service_provider', 'ncbi_sra_accession', 'max_number', 'pool_comments']

class Primer_Admin(reversion.VersionAdmin):
    list_display = ('primer_name', 'primer_pair', 'direction', 'primer_sequence')
    search_fields = ['primer_name', 'primer_pair', 'direction', 'primer_sequence']
    
class Substrate_Admin(reversion.VersionAdmin):
    search_fields = ('substrate_name',)


admin.site.register(Cosmid, CosmidAdmin)

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

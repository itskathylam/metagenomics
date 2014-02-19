from django.contrib import admin
from mainsite.models import *

#class ChoiceInline(admin.TabularInline):
#    model = Choice
#    extra = 3

#class PollAdmin(admin.ModelAdmin):
#    fieldsets = [
#        ('Basic',        {'fields': ['question']}),
#        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
#    ]
#    inlines = [ChoiceInline]
#    list_display = ('question', 'pub_date', 'was_published_recently')
#    list_filter = ['pub_date']
#    search_fields = ['question']
    
admin.site.register(Host)
admin.site.register(Screen)
admin.site.register(Vector)
admin.site.register(Library)
admin.site.register(Researcher)
admin.site.register(Pooled_Sequencing)
admin.site.register(Cosmid)
admin.site.register(Primer)
admin.site.register(End_Tag)
admin.site.register(Contig)
admin.site.register(ORF)
admin.site.register(Contig_ORF_Join)
admin.site.register(Subclone)
admin.site.register(Substrate)
admin.site.register(Cosmid_Assay)
admin.site.register(Subclone_Assay)
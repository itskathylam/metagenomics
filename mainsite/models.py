from django.db import models

class Host(models.Model):
    host_name = models.CharField(max_length=150, unique=True)
    
    def __unicode__(self):
        return self.host_name
    
    class Meta:
        ordering = ['host_name']

class Screen(models.Model):
    screen_name = models.CharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return self.screen_name
    
    class Meta:
        ordering = ['screen_name']

class Vector(models.Model):
    vector_name = models.CharField(max_length=50, unique=True)
    vector_type = models.CharField(max_length=50)
    vector_accession = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    
    def __unicode__(self):
        return self.vector_name
    
    class Meta:
        ordering = ['vector_name']
    
class Library(models.Model):
    library_name = models.CharField(max_length=100, unique=True)
    biosample = models.CharField(max_length=50)
    vector = models.ForeignKey(Vector)
    number_clones = models.PositiveIntegerField()
    insert_size = models.PositiveIntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return self.library_name
    
    class Meta:
        verbose_name_plural = 'Libraries'

class Researcher(models.Model):
    researcher_name = models.CharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return self.researcher_name
    
    class Meta:
        ordering = ['researcher_name']
    
class Pooled_Sequencing(models.Model):
    service_provider = models.CharField(max_length=200)
    ncbi_sra_accession = models.CharField(max_length=100, blank=True, null=True)
    max_number = models.PositiveIntegerField()

    def __unicode__(self):
        return self.pk
    
    class Meta:
        verbose_name_plural = 'Sequencing Pools'

class Cosmid(models.Model):
    cosmid_name = models.CharField(max_length=50)
    host = models.ForeignKey(Host)
    researcher = models.ForeignKey(Researcher)
    library = models.ForeignKey(Library)
    screen = models.ForeignKey(Screen)
    ec_collection = models.CharField(max_length=50)
    original_media = models.CharField(max_length=200, blank=True, null=True)
    pool = models.ForeignKey(Pooled_Sequencing, blank=True, null=True)
    lab_book_ref = models.CharField(max_length=100, blank=True, null=True)
    
    def __unicode__(self):
        return self.cosmid_name
    
    class Meta:
        unique_together = ("cosmid_name", "researcher")

class Primer(models.Model):
    primer_name = models.CharField(max_length=50, unique=True)
    primer_sequence = models.CharField(max_length=200)
    cosmid = models.ManyToManyField(Cosmid, through='End_Tag')
    
    def __unicode__(self):
        return self.primer_name
    
    class Meta:
        ordering = ['primer_name']

class End_Tag(models.Model):
    cosmid = models.ForeignKey(Cosmid)
    primer = models.ForeignKey(Primer)
    end_tag_sequence = models.TextField()
    
    class Meta:
        unique_together = ("cosmid", "primer")


class Contig(models.Model):
    pool = models.ForeignKey(Pooled_Sequencing)
    contig_name = models.CharField(max_length=200)
    contig_sequence = models.TextField()
    cosmid = models.ManyToManyField(Cosmid)
    contig_accession = models.CharField(max_length=50, blank=True, null=True)
    
    def __unicode__(self):
        return self.contig_name

    def __unicode__(self):
        return self.contig_name

class ORF(models.Model):
    orf_sequence = models.TextField() 
    annotation = models.CharField(max_length=255, blank=True, null=True)
    contig = models.ManyToManyField(Contig, through='Contig_ORF_Join')

    def __unicode__(self):
        return self.id
    
    class Meta:
        verbose_name_plural = 'ORFs'

class Contig_ORF_Join(models.Model):
    contig = models.ForeignKey(Contig)
    orf = models.ForeignKey(ORF)
    start = models.PositiveIntegerField()
    stop = models.PositiveIntegerField()
    orf_accession = models.CharField(max_length=50, blank=True, null=True)
    db_generated = models.BooleanField()

    class Meta:
            verbose_name_plural = 'Contig & ORF Relationships'


class Subclone(models.Model):
    subclone_name = models.CharField(max_length=50)
    cosmid = models.ForeignKey(Cosmid)
    orf = models.ForeignKey(ORF)
    vector = models.ForeignKey(Vector)
    researcher = models.ForeignKey(Researcher)
    ec_collection = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.subclone_name
    
    class Meta:
        unique_together = ("subclone_name", "researcher")

class Substrate(models.Model):
    substrate_name = models.CharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return self.substrate_name
    
    class Meta:
        ordering = ['substrate_name']
    
class Cosmid_Assay(models.Model):
    cosmid = models.ForeignKey(Cosmid)
    host = models.ForeignKey(Host)
    substrate = models.ForeignKey(Substrate)
    researcher = models.ForeignKey(Researcher)
    cosmid_km = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    cosmid_temp = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    cosmid_ph = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    cosmid_comments = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ("cosmid", "host", "substrate")
        verbose_name_plural = 'Cosmid Assays'
    
class Subclone_Assay(models.Model):
    subclone = models.ForeignKey(Subclone)
    host = models.ForeignKey(Host)
    substrate = models.ForeignKey(Substrate)
    researcher = models.ForeignKey(Researcher)
    subclone_km = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    subclone_temp = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    subclone_ph = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    subclone_comments = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ("subclone", "host", "substrate")
        verbose_name_plural = 'Subclone Assays'

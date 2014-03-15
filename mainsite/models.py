from django.db import models
import watson

class Host(models.Model):
    host_name = models.CharField("Host Name", max_length=150, unique=True)
    
    def __unicode__(self):
        return self.host_name
    
    class Meta:
        ordering = ['host_name']

class Screen(models.Model):
    screen_name = models.CharField("Screen Name", max_length=100, unique=True)
    
    def __unicode__(self):
        return self.screen_name
    
    class Meta:
        ordering = ['screen_name']

class Vector(models.Model):
    vector_name = models.CharField("Vector Name", max_length=50, unique=True)
    vector_type = models.CharField("Type", max_length=50)
    vector_accession = models.CharField("NCBI Accession", max_length=50, blank=True, null=True)
    description = models.CharField("Description", max_length=255, blank=True, null=True)
    
    def __unicode__(self):
        return self.vector_name
    
    class Meta:
        ordering = ['vector_name']
    
class Library(models.Model):
    library_name = models.CharField("Library Name", max_length=100, unique=True)
    biosample = models.CharField("NCBI BioSample ID", max_length=50)
    vector = models.ForeignKey(Vector)
    number_clones = models.PositiveIntegerField("Est. Number of Unique Clones")
    insert_size = models.PositiveIntegerField("Est.Insert Size", blank=True, null=True)
    
    def __unicode__(self):
        return self.library_name
    
    class Meta:
        verbose_name_plural = 'Libraries'

class Researcher(models.Model):
    researcher_name = models.CharField("Researcher Name", max_length=100, unique=True)
    
    def __unicode__(self):
        return self.researcher_name
    
    class Meta:
        ordering = ['researcher_name']
    
class Pooled_Sequencing(models.Model):
    service_provider = models.CharField("Service Provider Name", max_length=200)
    ncbi_sra_accession = models.CharField("NCBI SRA Acession", max_length=100, blank=True, null=True)
    max_number = models.PositiveIntegerField("Maximum Number of Clones")
    pool_comments = models.TextField("Comments", blank=True, null=True)

    def __unicode__(self):
        return self.pk
    
    class Meta:
        verbose_name_plural = 'Sequencing Pools'

class Cosmid(models.Model):
    cosmid_name = models.CharField("Cosmid Name", max_length=50)
    host = models.ForeignKey(Host)
    researcher = models.ForeignKey(Researcher)
    library = models.ForeignKey(Library)
    screen = models.ForeignKey(Screen)
    ec_collection = models.CharField("E. coli Stock Location", max_length=50)
    original_media = models.CharField("Original Screen Media", max_length=200, blank=True, null=True)
    pool = models.ForeignKey(Pooled_Sequencing, blank=True, null=True)
    lab_book_ref = models.CharField("Lab Book Reference", max_length=100, blank=True, null=True)
    cosmid_comments = models.TextField("Comments", blank=True, null=True)
    
    def __unicode__(self):
        return self.cosmid_name
    
    class Meta:
        unique_together = ("cosmid_name", "researcher")

class Primer(models.Model):
    primer_name = models.CharField("Primer Name", max_length=50, unique=True)
    primer_pair = models.PositiveIntegerField("Primer Pair ID")
    primer_sequence = models.CharField("Primer Sequence", max_length=200)
    cosmid = models.ManyToManyField(Cosmid, through='End_Tag')
    
    def __unicode__(self):
        return self.primer_name
    
    class Meta:
        ordering = ['primer_name']

class End_Tag(models.Model):
    cosmid = models.ForeignKey(Cosmid, verbose_name="Cosmid Name")
    primer = models.ForeignKey(Primer, verbose_name="Primer Name")
    end_tag_sequence = models.TextField("End Tag Sequence")
    vector_trimmed = models.BooleanField()
    
    def __unicode__(self):
        return self.end_tag_sequence
    
    class Meta:
        unique_together = ("cosmid", "primer")


class Contig(models.Model):
    pool = models.ForeignKey(Pooled_Sequencing, verbose_name="Sequencing Pool")
    contig_name = models.CharField("Contig Name", max_length=200, unique=True)
    contig_sequence = models.TextField("Contig Sequence")
    cosmid = models.ManyToManyField(Cosmid)
    contig_accession = models.CharField("Contig NCBI Acccession", max_length=50, blank=True, null=True)
    blast_hit_accession = models.CharField("Top BLAST Hit NCBI Accession", max_length=50, blank=True, null=True)
    image = models.BinaryField(blank=True, null=True)
    
    def __unicode__(self):
        return self.contig_name

    def __unicode__(self):
        return self.contig_name

class ORF(models.Model):
    orf_sequence = models.TextField("ORF Sequence") 
    annotation = models.CharField("ORF Annotation", max_length=255, blank=True, null=True)
    contig = models.ManyToManyField(Contig, through='Contig_ORF_Join')

    def __unicode__(self):
        return self.id
    
    class Meta:
        verbose_name_plural = 'ORFs'

class Contig_ORF_Join(models.Model):
    contig = models.ForeignKey(Contig, verbose_name="Contig Name")
    orf = models.ForeignKey(ORF)
    start = models.PositiveIntegerField()
    stop = models.PositiveIntegerField()
    complement = models.BooleanField()
    orf_accession = models.CharField("ORF Accession", max_length=50, blank=True, null=True)
    predicted = models.BooleanField()
    prediction_score = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Contig & ORF Relationships'


class Subclone(models.Model):
    subclone_name = models.CharField("Subclone Name", max_length=50)
    cosmid = models.ForeignKey(Cosmid, verbose_name="Parent Cosmid Name")
    orf = models.ForeignKey(ORF, verbose_name="ORF ID")
    vector = models.ForeignKey(Vector, verbose_name="Vector Name")
    researcher = models.ForeignKey(Researcher)
    ec_collection = models.CharField(max_length=50, verbose_name="E. coli Stock Location")
    primer1_name = models.CharField("Primer 1 Name", max_length=50, blank=True, null=True)
    primer1_seq = models.CharField("Primer 1 Sequence", max_length=200, blank=True, null=True)
    primer2_name = models.CharField("Primer 2 Name", max_length=50, blank=True, null=True)
    primer2_seq = models.CharField("Primer 2 Sequence", max_length=200, blank=True, null=True)
    
    def __unicode__(self):
        return self.subclone_name
    
    class Meta:
        unique_together = ("subclone_name", "researcher")

class Substrate(models.Model):
    substrate_name = models.CharField("Substrate Name", max_length=100, unique=True)
    
    def __unicode__(self):
        return self.substrate_name
    
    class Meta:
        ordering = ['substrate_name']

class Antibiotic(models.Model):
    antibiotic_name = models.CharField("Antibiotic Name", max_length=100, unique=True)
    
    def __unicode__(self):
        return self.antibiotic_name
    
    class Meta:
        ordering = ['antibiotic_name']

class Cosmid_Assay(models.Model):
    cosmid = models.ForeignKey(Cosmid, verbose_name="Cosmid Name")
    host = models.ForeignKey(Host)
    substrate = models.ForeignKey(Substrate)
    antibiotic = models.ForeignKey(Antibiotic, blank=True, null=True)
    researcher = models.ForeignKey(Researcher)
    cosmid_km = models.DecimalField("Km (mM)", max_digits=5, decimal_places=2, blank=True, null=True)
    cosmid_temp = models.DecimalField("Optimum Temperature", max_digits=5, decimal_places=2, blank=True, null=True)
    cosmid_ph = models.DecimalField("Optimum pH", max_digits=5, decimal_places=2, blank=True, null=True)
    cosmid_comments = models.TextField("Comments", blank=True, null=True)
    
    class Meta:
        unique_together = ("cosmid", "host", "substrate", "antibiotic")
        verbose_name_plural = 'Cosmid Assays'
    
class Subclone_Assay(models.Model):
    subclone = models.ForeignKey(Subclone, verbose_name="Subclone Name")
    host = models.ForeignKey(Host)
    substrate = models.ForeignKey(Substrate)
    antibiotic = models.ForeignKey(Antibiotic, blank=True, null=True)
    researcher = models.ForeignKey(Researcher)
    subclone_km = models.DecimalField("Km (mM)", max_digits=5, decimal_places=2, blank=True, null=True)
    subclone_temp = models.DecimalField("Optimum Temperature", max_digits=5, decimal_places=2, blank=True, null=True)
    subclone_ph = models.DecimalField("Optimum pH", max_digits=5, decimal_places=2, blank=True, null=True)
    subclone_comments = models.TextField("Comments", blank=True, null=True)
    
    class Meta:
        unique_together = ("subclone", "host", "substrate", "antibiotic")
        verbose_name_plural = 'Subclone Assays'


watson.register(Host)
watson.register(Vector)
watson.register(Library)
watson.register(Researcher)
watson.register(Pooled_Sequencing)
watson.register(Cosmid)
watson.register(Primer, exclude=("primer_sequence"))
#watson.register(End_Tag, exclude=("end_tag_sequence"))
watson.register(Contig, exclude=("contig_sequence"))
watson.register(ORF, exclude=("orf_sequence"))
watson.register(Contig_ORF_Join)
watson.register(Subclone)
watson.register(Substrate)
watson.register(Cosmid_Assay)
watson.register(Subclone_Assay)

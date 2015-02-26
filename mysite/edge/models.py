from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class ProteinAnalysis(models.Model):
    RUN_TYPES = (
        ('E', 'edge-edge'),
        ('T', 'transients'),
    )
    pdb_id = models.CharField(max_length=4)
    time = models.DateTimeField(_("Calculation Date"), auto_now_add=True)
    run_type = models.CharField(max_length=1, choices=RUN_TYPES)
    included_chains = models.CharField(max_length=100)
    included_hetatms = models.CharField(max_length=100)
    source_residues = models.CharField(max_length=210)


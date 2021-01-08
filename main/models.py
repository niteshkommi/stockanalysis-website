from django.db import models

class endOfDay(models.Model):
    symbol      = models.CharField(max_length=30, primary_key=True, default="ERROR")
    date        = models.CharField(max_length=30, null=True)
    currDate    = models.CharField(max_length=30, null=True)
    closePrice  = models.FloatField(null=True)
    call        = models.FloatField(null=True)
    stopLoss    = models.FloatField(null=True)
    Target1     = models.FloatField(null=True)
    Target2     = models.FloatField(null=True)
    Target3     = models.FloatField(null=True)
    Target4     = models.FloatField(null=True)
    high        = models.FloatField(null=True)
    low         = models.FloatField(null=True)
    status    = models.CharField(max_length=30, null=True)
    report      = models.FileField(null=True)

    def __str__(self):
        return self.symbol

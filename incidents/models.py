from django.db import models

class LocationType(models.Model):
    """Represents a type of location e.g. on the metro."""
    visible = models.BooleanField(default=True)
    label = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.label

class Incident(models.Model):
    """Represents a harassment incident."""
    visible = models.BooleanField(default=False)
    place = models.CharField(max_length=255, help_text='Please Specify the Intersection or Area Where the Harassment Occurred')
    location_type = models.ForeignKey(LocationType, help_text='Where did the harassment occur?', blank=True)
    other_type = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    story = models.TextField(help_text='Please Tell Your Story')
    signature = models.CharField(max_length=255, blank=True, help_text='Sign Your Name or Initials (if you want to)')
    date_created = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    def __unicode__(self):
        return self.title or self.place
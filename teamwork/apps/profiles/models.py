"""
Teamwork: profiles

Database Models for the objects: Skills, Profile
"""

# Django Imports
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone


class Skills(models.Model):
    """
    Skills: A database model (object) for skills.

    Fields:
        skill: a field that contains the name of a skill

    Methods:
        __str__(self):                  Human readeable representation of the skill object.
        save(self, *args, **kwargs):    Overides the default save operator...

        """
    # skill, a string
    skill = models.CharField(max_length=255,default="")

    def __str__(self):
        return self.skill
    class Meta:
        # Verbose name is the same as class name in this case.
        verbose_name = "Skill"
        # Multiple Skill objects are referred to as Projects.
        verbose_name_plural = "Skills"
        ordering = ('skill',)

    def save(self, *args, **kwargs):
        """
        Overides the default save operator...
        Bassically a way to check if the Project object exists in the database. Will be helpful later.
        self.pk is the primary key of the Project object in the database!
        I don't know what super does...
        """
        super(Skills, self).save(*args, **kwargs)

# Converts a number into a weekday
def dayofweek(number):
    return {
        9: "Sunday",
        10: "Monday",
        11: "Tuesday",
        12: "Wednesday",
        13: "Thursday",
        14: "Friday",
        15: "Saturday",
    }.get(number, "Day that doesnt exist")

class Events(models.Model):
    """
    Events: A database model (object) for Events (Availabiliy).

    Fields:
        event_name: a field that contains the name of a skill
        day: Day of week
        start_time_hour: Hour an event starts (1-24)
        start_time_minute: Minute an event starts (1-60)
        end_time_hour: Hour an event ends (1-24)
        end_time_minute: Minute an event ends (1-60)


    Methods:
        __str__(self):                  Human readeable representation of the Event object.
        save(self, *args, **kwargs):    Overides the default save operator...

        """
    # Day (Is this a character?)
    day = models.CharField(max_length=255,default="")

    # Times stored in 24h format
    # Start time (Hours)
    start_time_hour = models.SmallIntegerField()
    # Start time (Minutes)
    start_time_min = models.SmallIntegerField()
    # End time (Hours)
    end_time_hour = models.SmallIntegerField()
    # End time (Minutes)
    end_time_min = models.SmallIntegerField()
    def __str__(self):
        event_string = "%s -> %02d:%02d - %02d:%02d"%(self.day, self.start_time_hour, self.start_time_min, self.end_time_hour, self.end_time_min)
        #event_string = self.day + "-> " + self.start_time_hour + ":" + self.start_time_min + " - " + self.end_time_hour + ":" + self.end_time_min
        return event_string

    class Meta:
        # Verbose name is the same as class name in this case.
        verbose_name = "Event"
        # Multiple Event objects are referred to as Projects.
        verbose_name_plural = "Events"
        ordering = ('day',)

    def save(self, *args, **kwargs):
        """
        Overides the default save operator...
        Bassically a way to check if the Project object exists in the database. Will be helpful later.
        self.pk is the primary key of the Project object in the database!
        I don't know what super does...
        """
        super(Events, self).save(*args, **kwargs)


class Alert(models.Model):
    """
    Alert: A notification directed to a specific user

    Fields:
        sender  - User: person sending alert, or None (if System)
        to      - User: person receiving alert
        date    - DateTime: time sent
        msg     - str: alert body
        read    - boolean: whether alert has been written/marked as read
        url     - str: URL for related page, or None

    Types:
        'course_inv'    - invitation to a course
    """

    sender = models.ForeignKey(User, default=None, related_name="sender")
    to = models.ForeignKey(User, related_name="to")
    date = models.DateTimeField(auto_now_add=True)
    # type = models.CharField(max_length=20, default="null")
    msg = models.CharField(max_length=500)
    read = models.BooleanField(default=False)
    url = models.CharField(max_length=500,default="")

    def __str__(self):
        return str(self.sender) + " -> " + str(self.to) + " : " + str()

    class Meta:
        # Verbose name is the same as class name in this case.
        verbose_name = "Alert"
        # Multiple Event objects are referred to as Projects.
        verbose_name_plural = "Alerts"
        ordering = ('date',)

    def save(self, *args, **kwargs):
        super(Alert, self).save(*args, **kwargs)


class Profile(models.Model):
    """
    Profile: A database model (object) for the user profile.

    Fields:
        user: user object
        bio: bio of user
        known_skills: stores known skills
        interest: stores interest for projects in profile
        isProf: boolean that dictates if the user is a professor
        isTa: boolean that indicates if the user is a teaching assistant

    Methods:
        __str__(self):                  Human readeable representation of the profile object.

    """
    user = models.OneToOneField(User)
    bio = models.TextField(max_length=500, blank=True)
    name = models.TextField(max_length=75, blank=True)
    institution = models.TextField(max_length=100, blank=True)
    location = models.TextField(max_length=100, blank=True)

    # Avail - Availabiliy
    avail = models.ManyToManyField(Events)

    avatar = models.ImageField(upload_to= 'avatars/', default="")

    # TODO: Interest - ManyToOne, Past Classes,
    known_skills = models.ManyToManyField(Skills, related_name="known", default="")
    learn_skills = models.ManyToManyField(Skills, related_name="learn", default="")
    # interest = models.ForeignKey(Project, on_delete=models.CASCADE)

    isProf = models.BooleanField(default=False)
    isTa = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    def __hash__(self):
        return hash(self.user)
    def __eq__(self, other):
        return (self.user == other.user)
    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self == other)

    # Alert functions, self explanitory
    def alerts(self):
        return Alert.objects.filter(to=self.user)
    def unread_alerts(self):
        return Alert.objects.filter(to=self.user,read=False)
    def read_alerts(self):
        return Alert.objects.filter(to=self.user,read=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)

from django.db import models

MAX_LENGTH = 30

BEARERS = (
	("sms",   "SMS"),
	("ivr",   "Phone Call"),
	("email", "Email"),
	("shell", "Shell Script"))


class Scope(models.Model):
	name = models.CharField(max_length=MAX_LENGTH, unique=True)
	
	def __unicode__(self):
		return self.name
	
	# a simple link to view this scope
	@models.permalink
	def get_absolute_url(self):
		return ("view-scope", [self.name])


class Keyword(models.Model):
	scope = models.ForeignKey(Scope)
	name = models.CharField(max_length=MAX_LENGTH)
	unique_together = ("scope", "name")
	
	def __unicode__(self):
		return "%s:%s" % (self.scope.name, self.name)
	
	# to view this keyword, we must also include
	# the scope name - they're only unique together,
	# and we are RESTful
	@models.permalink
	def get_absolute_url(self):
		return ("view-keyword", [self.scope.name, self.name])


class Destination(models.Model):
	name = models.CharField(max_length=MAX_LENGTH)
	#phone_number = models.PhoneNumberField()
	phone_number = models.CharField(max_length=30)
	email_address = models.EmailField()
	
	def get_something(self):
		return self._s
	
	def set_something(self,val):
		self._s = val




class Action(models.Model):
	keyword = models.ForeignKey(Keyword)
	bearer_type = models.CharField("Type", max_length=5, choices=BEARERS)
	reply_to_sender = models.BooleanField()
	destinations = models.TextField("Other Destinations", blank=True)
	payload = models.TextField("Message")
	
	def __unicode__(self):
		btd = "%s to " % (self.get_bearer_type_display())
		
		if self.reply_to_sender:
			return btd + "Sender"
		
		else:
			# list all destinations as a comma-separated
			# string, rather than \n as they are stored
			d = self.destinations.splitlines()
			return btd + ", ".join(d)
	
	# like Keyword, we must include other
	# names in this url, to be RESTful
	@models.permalink
	def get_absolute_url(self):
		return ("view-action", [self.keyword.scope.name, self.keyword.name, self.pk])


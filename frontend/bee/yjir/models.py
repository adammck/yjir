from django.db import models


MAX_TOKEN_LENGTH = 10

REPLY_VIA = (
	("",    "None"),
	("sms", "SMS"),
	("ivr", "Phone Call"))

PROXYS = (
	("", "None"),
	("shell", "Shell Script"))


class Scope(models.Model):
	name = models.CharField(max_length=MAX_TOKEN_LENGTH, unique=True)
	
	def __unicode__(self):
		return self.name
	
	# a simple link to view this scope
	@models.permalink
	def get_absolute_url(self):
		return ("view-scope", [self.name])


class Keyword(models.Model):
	scope = models.ForeignKey(Scope)
	name = models.CharField(max_length=MAX_TOKEN_LENGTH)
	unique_together = ("scope", "name")
	
	# always include the parent scope in the keywords string
	# summary, because keywords are useless without their scopes
	def __unicode__(self):
		return "%s %s" % (self.scope.name, self.name)
	
	# to view this keyword, we must also include
	# the scope name - they're only unique together,
	# and we are RESTful
	@models.permalink
	def get_absolute_url(self):
		return ("view-keyword", [self.scope.name, self.name])


class Action(models.Model):
	keyword = models.ForeignKey(Keyword)
	#proxy = models.CharField(max_length=10, choices=PROXYS, default="")
	reply_via = models.CharField(max_length=5, choices=REPLY_VIA, default="sms")
	payload = models.TextField("Message")
	
	def __unicode__(self):
		if self.reply_via != "":
			return self.get_reply_via_display() + " to Sender"
		
		else:
			# list all destinations as a comma-separated
			# string, rather than \n as they are stored
			dests = self.destination_set.all()
			dests = ["%s to %s" % (d.type, d.dest) for d in dests]
			return btd + ", ".join(dests)
	
	# like Keyword, we must include other
	# names in this url, to be RESTful
	@models.permalink
	def get_absolute_url(self):
		return ("view-action", [self.keyword.scope.name, self.keyword.name, self.pk])


class Destination(models.Model):
	action = models.ForeignKey(Action)
	type = models.CharField(max_length=5)
	dest = models.CharField(max_length=30)


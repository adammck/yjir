#!/usr/bin/env python
# vim: noet

import sys, threading, os, tempfile, stat, smtplib, time, re
from subprocess import Popen, PIPE
from kannel import *
import mobiled


# during dev, patch the python path
# to include the parent dir, which
# includes the "bee" django app
sys.path.append("../frontend")


# do the minimum possible work to
# gain access to bee.yjir models
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
from bee import settings
setup_environ(settings)
from bee.yjir.models import *




# these can be raised anywhere, to indicate that
# the incoming SMS contained something invalid
class YjirError(Exception): pass


class YJIR():
	LOG_PREFIX = {
		"info":  "  ",
		"warn": "\x1b[41m!!\x1b[0m",
		"out":  "\x1b[43m>>\x1b[0m",
		"in":   "\x1b[43m<<\x1b[0m"}
	
	
	# reaffirm my status as renegade overcomplicator,
	# by logging messages using fancy ANSI colors
	def logx(self, msg, type="info"):
		
		# extract the current thread's index from the name
		index = int(re.compile('^Thread\-').sub("",
			threading.currentThread().getName()))
		
		ansi_index = "\x1b[30m%04d\x1b[0m" % (index)
		
		# convert that index into an ansi foreground
		# color between 31 and 37, to cycle through them
		code = (7 - ((index - 4) % 7)) + 30
		ansi_code = "\x1b[%dm" % (code)
		
		# it's so pretty (and functional, too!)
		print "%s %s %s%s\x1b[0m"\
			% (ansi_index, self.LOG_PREFIX[type], ansi_code, msg)
	
	
	
	def log(self, msg, type="info"):
		print self.LOG_PREFIX[type] + " " + msg
	
	
	# create a single sms sender for this app
	def __init__(self, username, password):
		self.sms_sender = SmsSender(username, password)
		self.smtp = smtplib.SMTP(settings.EMAIL_SERVER)
	
	
	
	
	def incommingSMS(self, caller, msg):
		
		lmsg = msg.strip().lower()
		self.log('SMS from "%s": %s'\
			% (caller, lmsg), "in")
		
		# split the message into tokens
		tok = re.split('\s+', lmsg)
		
		
		try:
		
			# are we requesting a list of scopes?
			if len(tok)==1 and (tok[0]=="scopes" or tok[0]=="sc"):
				self.send_scopes(caller)
			
			# requesting a list of keywords within a scope?
			elif len(tok)==2 and (tok[1]=="keywords" or tok[0]=="kw"):
				self.send_keywords(caller, tok[0])
			
			# triggering an individual action? this is for
			# the "submit and test" button in the frontend,
			# but could be useful (but undocumented) elsewhere
			elif len(tok)==2 and tok[0]=="action":
				act = Action.objects.get(pk=tok[1])
				#self.log('Action="%s"' % (act))
				self.doAction(caller, act)
		
		
			# == MOST "$SCOPE $KEYWORD" REQUESTS END UP HERE ==
			elif len(tok) > 1:
				
				# fetch the scope and keyword (to ensure that
				# they're both valid - a ObjectDoesNotExist exception
				# is raised and caught otherwise), then fetch actions
				sc = Scope.objects.get(name=tok[0])
				kw = Keyword.objects.get(scope=sc, name=tok[1])
				acts = Action.objects.filter(keyword=kw)
				#self.log('Scope="%s", Keyword="%s"' % (sc, kw))
				
				# no actions were found for this message, so
				# respond to the caller with an unhelpful error
				# todo: is this even necessary?
				if not len(acts):
					raise YjirError(
						"Scope and Keyword were valid, " +
						"but no Actions were found")
				
				# otherwise, iterate them, and pass
				# each one to the appropriate handler
				for act in acts:
					#self.log('Action="%s"' % (act))
					self.doAction(caller, act)
				
			# we couldn't figure out what the user wanted
			else: raise YjirError("Invalid syntax")
		
		
		# something went wrong during the request! we 
		# must log it (to the console), and send an sms
		# back to the caller (as not to leave them hanging)
		except YjirError, e:
			self.log("Caught Exception", "warn")
			err = "YJIR Error: %s" % (str(e))
			self.sendSMS(caller, err)
		
		# this is a gigantic hack, because django's model
		# exceptions kind of suck. when ObjectDoesNotExist
		# is raised, no meta-information about WHAT wasn't
		# found is included - so we must pluck it from the
		# actual exception string (ie, "Scope matching query
		# does not exist")
		except ObjectDoesNotExist, e:
			words = re.split('\s+', str(e))
			klass = words[0]
			
			# as above
			self.log("%s Not Found" % (klass), "warn")
			err = "YJIR Error: No such %s" % (klass)
			self.sendSMS(caller, err)
	
	
	
	
	## ====
	## utility
	## ====
	
	# just send an SMS. we do this all over the place
	def sendSMS(self, to, msg):
		self.log('SMS to "%s": %s' % (to, msg), "out")
		self.sms_sender.send(to, msg)
	
	
	
	
	## ====
	## wat
	## ====

	def send_scopes(self, to):
		"""Send (via SMS) a list of all available Scopes"""
		scopes = Scope.objects.values_list("name", flat=True)
		msg = "Scopes: %s" % (", ".join(scopes))
		self.sendSMS(to, msg)
	
	def send_keywords(self, to, scope_name):
		"""Send (via SMS) a list of all Keywords within the named scope"""
		sc = Scope.objects.get(name=scope_name)
		keywords = Keyword.objects.filter(scope=sc).values_list("name", flat=True)
		msg = "Keywords in %s: %s" % (sc.name, ", ".join(keywords))
		self.sendSMS(to, msg)
		
	
	
	
	
	## ====
	## actions
	## ====
	
	def doAction(self, caller, act):
		
		# create a 
		dests = [[act.reply_via, caller]]
		for d in act.destination_set.all():
			dests.append([d.type, d.dest])
		
		for d in dests:
			args = [caller, d[1], act]
			if   d[0] == 'sms':   self.doSMS(*args)
			elif d[0] == 'ivr':   self.doIVR(*args)
			elif d[0] == 'email': self.doEmail(*args)
	
	
	def doSMS(self, caller, dest, act):
		self.sendSMS(dest, act.payload)
	
	
	def doIVR(self, caller, dest, act):
		dialer = mobiled.ivr.IVRDialer(node)

		# get the ivr resource for this; if it's not
		# already in use, then it should return true
		getres = dialer.getResourceIfExists
		if getres() == False:
			
			# log the situation, and wait for the
			# resource to become available. this
			# part will block indefinately
			self.log("IVR is busy", "warn")
			while getres() == False: pass
			self.log("IVR is now available")
		
		# log to stdout		
		self.log('Calling "%s": %s'\
			% (dest, act.payload), "out")
		
		try:
			# dial the recipient, and
			# wait for them to answer
			ivr = dialer.dial(dest)
			ivr.answer()

			# say the introduction and payload
			ivr.say("Welcome to Why Jer")
			ivr.getInput(1000)
			ivr.say(act.payload)
			
			# outro, and hang up
			ivr.getInput(2000)
			ivr.say("Toodles")
			ivr.hangup()
			
			# if (by some miracle) we reached this
			# point, the call was made successfully
			self.log("Call Completed")
		
		
		# something went wrong, but we have no idea
		# what, because mobiled doesn't see fit to tell us
		except mobiled.ivr.manager_api.OriginateFailed:	
			self.log("Call Failed", "warn")
			
		finally:
			# release the ivr resource
			dialer.releaseResource()
	
	
	def doEmail(self, caller, dest, act):
		self.log('Email to "%s": %s' % (dest, act.payload), "out")

		# construct the email (in full), and send via smtplib
		msg = "from: %s\r\nto: %s\r\nsubject: %s\r\n\r\n%s"\
			% (settings.EMAIL_FROM, dest, settings.EMAIL_SUBJECT, act.payload)
		self.smtp.sendmail(settings.EMAIL_FROM, dest, msg)




# create the mobiled node for IVR stuff
# one day, soon, this will be GONE! hah!
node = mobiled.Mobiled(settings.MOBILED_UDP_PORT)

node.setupIVROutgoing(
	asteriskManAPIHost=settings.ASTERISK_SERVER,
	asteriskManAPIPort=settings.ASTERISK_MANAPI_PORT,
	asteriskManAPIChannels=settings.ASTERISK_CHANNELS,
	asteriskManAPIUsername=settings.ASTERISK_MANAPI_USERNAME,
	asteriskManAPIPassword=settings.ASTERISK_MANAPI_PASSWORD)

node.setupIVRGeneral(
	fastAGIPort=settings.ASTERISK_FASTAGI_PORT,
	defaultTTS=settings.ASTERISK_DEFAULT_TTS)


try:
	# start up mobiled
	print "Starting Mobiled..."
	node.start()
	
	# start the app
	print "Waiting for SMS..."
	yjir = YJIR("mobiled", "mobiled")
	SmsReceiver(yjir.incommingSMS).run()

# as soon as the receiver is killed
# (by ctrl+c), terminate mobiled with
# extreme predjudice (node.shutdown
# seems to do nothing)
except KeyboardInterrupt:
	os._exit(0)


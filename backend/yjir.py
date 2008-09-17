#!/usr/bin/env python
# vim: noet

import sys, os, tempfile, stat, smtplib, time, re
from subprocess import Popen, PIPE
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
class InvalidKeyword(Exception): pass


class RequestHandler(mobiled.application.SMSHandler):
	def handleSMS(self, callerID, message, node):
		
		lmsg = message.strip().lower()
		print '<< SMS from "%s": %s'\
		      % (callerID, lmsg)
		
		# split the message into tokens
		tok = re.split('\s+', lmsg)
		
		
		try:
		
			# are we requesting a list of scopes?
			if len(tok)==1 and tok[0]=="scopes":
				self.send_scopes(node, callerID)
		
			# requesting a list of keywords within a scope?
			elif len(tok)==2 and tok[1]=="keywords":
				self.send_keywords(node, callerID, tok[0])
		
			# triggering an individual action? this is for
			# the "submit and test" button in the frontend,
			# but could be useful (but undocumented) elsewhere
			elif len(tok)==2 and tok[0]=="action":
				act = Action.objects.get(pk=tok[1])
				print "## action=\"%s\"" % (act)
				self.doAction(node, act, callerID)
		
			# == MOST "$SCOPE $KEYWORD" REQUESTS END UP HERE ==
			elif len(tok) > 1:
				
				# fetch the scope and keyword (to ensure that
				# they're both valid - a ObjectDoesNotExist exception
				# is raised and caught otherwise), then fetch actions
				sc = Scope.objects.get(name=tok[0])
				kw = Keyword.objects.get(scope=sc, name=tok[1])
				acts = Action.objects.filter(keyword=kw)
				
				print "## scope=\"%s\", keyword=\"%s\""\
					  % (sc.name, kw.name)
				
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
					self.doAction(node, callerID, act)
				
			# we couldn't figure out what the user wanted
			else: raise YjirError("Invalid syntax")
		
		
		# something went wrong during the request! we 
		# must log it (to the console), and send an sms
		# back to the caller (as not to leave them hanging)
		except YjirError, e:
			print "!! Caught Exception"
			err = "YJIR Error: %s" % (str(e))
			self.sendSMS(node, callerID, err)
		
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
			print "!! %s Not Found" % (klass)
			err = "YJIR Error: No such %s" % (klass)
			self.sendSMS(node, callerID, err)
		
		
		# divide up the console log
		print "\n--\n"
	
	
	
	
	## ====
	## utility
	## ====
	
	# just send an SMS. we do this all over the place
	def sendSMS(self, node, to, msg):
		
		# create the sender, and find any available
		# outgoing sms service (via setupSMSSend)
		sender = mobiled.sms.SMSSender(node)
		sender.getResource()
		
		# log to console and send the message
		print ">> SMS to \"%s\": %s" % (to, msg)
		sender.sendMessage(msg, str(to))
	
	
	
	
	
	## ====
	## wat
	## ====

	def send_scopes(self, node, to):
		"""Send (via SMS) a list of all available Scopes"""
		scopes = Scope.objects.values_list("name", flat=True)
		msg = "Scopes: %s" % (", ".join(scopes))
		self.sendSMS(node, to, msg)
	
	def send_keywords(self, node, to, scope_name):
		"""Send (via SMS) a list of all Keywords within the named scope"""
		sc = Scope.objects.get(name=scope_name)
		keywords = Keyword.objects.filter(scope=sc).values_list("name", flat=True)
		msg = "Keywords in \"%s\": %s" % (sc.name, ", ".join(keywords))
		self.sendSMS(node, to, msg)
		
	
	
	
	
	## ====
	## actions
	## ====
	
	def doAction(self, node, callerID, act):
				
		# HACK HACK HACK HACK
		# temporarily, we are only replying,
		# and ignoring other recipients
		dests = [callerID]

		# always pass the same arguments
		args = [callerID, act, dests, node]
		bt = act.reply_via
		
		# delegate each type of action to an
		# instance method, or log an error
		if   bt == 'sms': self.doSMS(*args)
		elif bt == 'ivr': self.doIVR(*args)
		else: print "!! Unknown Bearer Type: %s" %(bt)
	
	
	def doSMS(self, callerID, act, dests, node):
		for dest in dests:
			self.sendSMS(node, dest, act.payload)
	
	def doIVR(self, callerID, act, dests, node):
		
		# create the dialer, and find any available
		# outgoing ivr service (better not forget
		# the second line, or mobiled will fail
		# cryptically with no useful error msg)
		dialer = mobiled.ivr.IVRDialer(node)
		dialer.getResource()
		
		# call each destination in order
		for dest in dests:
			print ">> Calling \"%s\": %s"\
			      % (dest, act.payload)
			
			try:
				# dial the recipient, and
				# wait for them to answer
				ivr = dialer.dial(dest)
				ivr.answer()

				# say the introduction and payload
				ivr.say("Welcome to Why Jure")
				ivr.getInput(1000)
				ivr.say(act.payload)
				
				# outro, and hang up
				ivr.getInput(2000)
				ivr.say("Toodles")
				ivr.hangup()
			
			except OriginateFailed:	
				print "!! Recipient didn't answer"




# create the mobiled node, using the general handler
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

node.setupSMSSend(
	kannelHost=settings.KANNEL_SERVER,
	kannelPort=settings.KANNEL_PORT_SEND,
	kannelUsername=settings.KANNEL_USERNAME,
	kannelPassword=settings.KANNEL_PASSWORD)

node.setupSMSReceive(
	port=settings.KANNEL_PORT_RECEIVE)


# start the app
print "Starting Mobiled...",
node.runApplication(RequestHandler)
node.start()
print "[done]"




# hang around doing nothing until
# an interrupt is raised (ctrl+c)
try:
	while True:
		time.sleep(1)

# once we reach this point, forcibly
# terminate all threads by exiting
# (to prevent mobiled from hanging)
except KeyboardInterrupt:
	os._exit(0)


#!/usr/bin/env python
# vim: noet

import sys, os, tempfile, stat, smtplib, time, re
from subprocess import Popen, PIPE
import mobiled


# during dev, patch the python path
# to include the parent dir, which
# includes the "bee" django app
sys.path.append("../")


# do the minimum possible work to
# gain access to bee.yjir models
from django.core.management import setup_environ
from bee import settings
setup_environ(settings)
from bee.yjir.models import *




class RequestHandler(mobiled.application.SMSHandler):
	def __init__(self):
		
		# maintain a single smtp
		# server for this handler
		self.smtp = smtplib.SMTP(
			settings.EMAIL_SERVER)
	
	
	def handleSMS(self, callerID, message, node):
		
		lmsg = message.lower()
		print '<< SMS from "%s": %s'\
		      % (callerID, lmsg)
		
		# fetch all actions for this scope + keyword
		sc, kw = re.split('\s+', lmsg, 1)
		acts = Action.objects.filter(
			keyword__scope__name__iexact=sc,
			keyword__name__iexact=kw)
		
		print "|| scope=\"%s\", keyword=\"%s\""\
		      % (sc, kw)
		
		# abort if no actions were found
		if not len(acts):
			print "!! No actions"
			return False
		
		
		# otherwise, iterate them, and pass
		# each one to the appropriate handler
		for act in acts:
		
			# pre-prepare the destinations list, since
			# it is the same for each type of action
			dests = act.destinations.splitlines()
			if act.reply_to_sender:
				dests.append(callerID)
			
			# always use the same arguments
			args = [callerID, act, dests, node]
			bt = act.bearer_type
			
			# delegate each type of action to an
			# instance method, or log an error
			if   bt == 'sms':   self.doSMS(*args)
			elif bt == 'email': self.doEmail(*args)
			elif bt == 'ivr':   self.doIVR(*args)
			elif bt == 'shell': self.doShell(*args)
			else:               print "!! Unknown Bearer Type: %s" %(bt)
			
		# divide up the log
		print "--"
		
	
	def sendSMS(self, node, to, msg):
		
		# create the sender, and find any available
		# outgoing sms service (via setupSMSSend)
		sender = mobiled.sms.SMSSender(node)
		sender.getResource()
		
		# log to console and send the message
		print ">> SMS to \"%s\": %s" % (to, msg)
		sender.sendMessage(msg, str(to))
	
	
	def doSMS(self, callerID, act, dests, node):
		for dest in dests: self.sendSMS(node, dest, act.payload)
	
	
	def doEmail(self, callerID, act, dests, node):
		
		# emailing a reply to the sender doesn't even
		# make sense. the UI should prevent it happening
		if act.reply_to_sender:
			return False
		
		# send a separate email to each destination
		for dest in dests:
			print ">> Email to \"%s\": %s"\
			      % (dest, act.payload)
			
			# construct the email (in full), and send via smtplib
			msg = "from: %s\r\nto: %s\r\nsubject: %s\r\n\r\n%s"\
			      % (settings.EMAIL_FROM, dest, settings.EMAIL_SUBJECT, act.payload)
			self.smtp.sendmail(settings.EMAIL_FROM, dest, msg)
	
	
	def doIVR(self, callerID, act, dests, node):
		pass
	
	
	def doShell(self, callerID, act, dests, node):
		
		# remove carraige returns from the payload,
		# because HTTP puts them in, and 
		clean_payload = act.payload.replace("\r", "")
		
		# store the shell script into a temp file
		filename = tempfile.mktemp()
		tmp = open(filename, "w")
		tmp.write(clean_payload)
		tmp.close()
		
		# we will need to read + execute it
		os.chmod(tmp.name, stat.S_IREAD | stat.S_IEXEC)
		
		# execute it once for each recipient,
		# and send the results to each one
		for dest in dests:
			outp = Popen(["$0 $1", filename, dest], shell=True, stdout=PIPE).communicate()[0].strip()
			print "|| Executing Shell Script for \"%s\": %s" % (dest, tmp.name)
			self.sendSMS(node, dest, outp)
		
		# delete the temp file
		os.remove(filename)



# create the mobiled node, using the general handler
node = mobiled.Mobiled(settings.MOBILED_UDP_PORT)

#node.setupIVRGeneral(fastAGIPort=settings.ASTERISK_FASTAGI_PORT, defaultTTS=settings.ASTERISK_DEFAULT_TTS)
#node.setupIVROutgoing(asteriskManAPIHost=settings.ASTERISK_SERVER, asteriskManAPIPort=settings.ASTERISK_MANAPI_PORT, asteriskManAPIChannels=settings.ASTERISK_CHANNELS, asteriskManAPIUsername=settings.ASTERISK_MANAPI_USERNAME, asteriskManAPIPassword=settings.ASTERISK_MANAPI_PASSWORD)

node.setupSMSSend(
	kannelHost=settings.KANNEL_SERVER,
	kannelPort=settings.KANNEL_PORT_SEND,
	kannelUsername=settings.KANNEL_USERNAME,
	kannelPassword=settings.KANNEL_PASSWORD)

node.setupSMSReceive(
	port=settings.KANNEL_PORT_RECEIVE)

node.runApplication(RequestHandler)

# start the app
print "Starting Mobiled...",
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




#def mobiledInit():
#    """ Initializes mobiled; called from tgStartupInit() """
#    from mobiled import Mobiled
#    from yjir.mobiled_handlers import IncomingRequestHandler
#    import config.mobiled_config as settings
#    print 'creating mobiled node'
#    mobiledNode = Mobiled(settings.MOBILED_UDP_PORT)
#    print 'setting up mobiled node'
#    mobiledNode.setupIVROutgoing(asteriskManAPIHost=settings.ASTERISK_SERVER, asteriskManAPIPort=settings.ASTERISK_MANAPI_PORT, asteriskManAPIChannels=settings.ASTERISK_CHANNELS, asteriskManAPIUsername=settings.ASTERISK_MANAPI_USERNAME, asteriskManAPIPassword=settings.ASTERISK_MANAPI_PASSWORD)
#    mobiledNode.setupIVRGeneral(fastAGIPort=settings.ASTERISK_FASTAGI_PORT, defaultTTS=settings.ASTERISK_DEFAULT_TTS)
#    mobiledNode.setupSMSReceive(port=settings.KANNEL_PORT_RECEIVE)
#    mobiledNode.setupSMSSend(kannelHost=settings.KANNEL_SERVER, kannelPort=settings.KANNEL_PORT_SEND, kannelUsername=settings.KANNEL_USERNAME, kannelPassword=settings.KANNEL_PASSWORD)
#    print 'running handler application'
#    mobiledNode.runApplication( IncomingRequestHandler() )
#    print 'starting node'
#    mobiledNode.start()


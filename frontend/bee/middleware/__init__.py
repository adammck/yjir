from settings import *
import mobiled

class MobiledMiddleware(object):
	def __init__(self):
		print "Creating Mobiled node..."
		self.node = mobiled.Mobiled(4001)#MOBILED_UDP_PORT)
		
		print "Configuring Mobiled node..."
		self.node.setupSMSSend(
			kannelHost=KANNEL_SERVER,
			kannelPort=KANNEL_PORT_SEND,
			kannelUsername=KANNEL_USERNAME,
			kannelPassword=KANNEL_PASSWORD)

		print "Starting Mobiled node..."
		self.node.start()

#print "wwwwwaaaaaa"

#	# This is (really) ugly, but until we find a better way, it'll work...
#	print 'creating mobiled node'
#	mobiledNode = Mobiled(MOBILED_UDP_PORT)
#	try:
#		# try to start the node up
#		print 'setting up mobiled node'
#		mobiledNode.setupIVROutgoing(asteriskManAPIHost=ASTERISK_SERVER, asteriskManAPIPort=ASTERISK_MANAPI_PORT, asteriskManAPIChannels=ASTERISK_CHANNELS, asteriskManAPIUsername=ASTERISK_MANAPI_USERNAME, asteriskManAPIPassword=ASTERISK_MANAPI_PASSWORD)
#		mobiledNode.setupIVRGeneral(fastAGIPort=ASTERISK_FASTAGI_PORT, defaultTTS=ASTERISK_DEFAULT_TTS)
#		mobiledNode.setupSMSReceive(port=KANNEL_PORT_RECEIVE)
#		print 'running handler application'
#		mobiledNode.runApplication( IncomingRequestHandler() )
#		print 'starting node'
#		mobiledNode.start()
#	except:
#		# we are already running, so just do nothing
#		pass


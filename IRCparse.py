#used for client parsing.  Maybe it will be useful for server parsing, too
class IRCcommands(object):
	messagetypes = ['/join', '/leaveroom', '/listrooms', 'LEAVE', 'ROOMMSG', '/listroomppl' ]

	def __init__(self):
		# what the server reads.  Every message needs to
		# have one of these when sendign to the server.

		self.JOINROOM = "JOIN" 
		self.LEAVE = "LEAVE"
		self.DEFAULT = "DEFAULT" #TODO: for developing		
		self.MSGROOM = "ROOMMSG" #followed by roomname and then the entire message
		self.LISTROOMPPL = "/listroomppl" #followed by roomname #this doesn't work

		#what the user types
		self.joinUSR = "/join" #connects them to the server??
		self.quitUSR = "/quit" #disconnects them from the server??

	# msttypeDict = {
	# 	'JOINROOM' : joinRoom,
	# 	'LEAVEROOM' : leaveRoom,
	# }
"""
returns a tuple of parsed command in format:
(type,payload)

Note that all trailing and leading space information 
(carriage returns, etc) are removed.
"""
def parse(unparsed):
	cleaned = unparsed.strip()
	cmd = unparsed.split()[0]
	payload = " ".join(unparsed.split()[1:]).rstrip()
	return cmd, payload
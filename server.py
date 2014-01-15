import cherrypy
import os, sys, base64
import psycopg2, psycopg2.pool
from contextlib import contextmanager
from capcache import PsqlCaptcha
from htmltempl import *
from dbconf import *

#>>> h = 'be6e7836f8f6b4bf5cf79d78b44679296bb6f76f1cc187c6d15001ce0ac23771'
#>>> from capcache import PsqlCaptcha
#>>> test = PsqlCaptcha("dbname=testdb user=user")
#>>> test.validate('gluomr', h)
#

try:
	DBCONN = psycopg2.pool.ThreadedConnectionPool(1, 16, DSN)
except:
	cherrypy.log("UNABLE TO CONNECT TO DATABASE, TERMINATING!", context='DATABASE', severity=logging.ERROR, traceback=False)
	sys.exit(1)

def bin2base64url(img, fmt):
	b64 = 'data:image/' + fmt + ';base64,'
	b64 += base64.b64encode(img)
	return b64

@contextmanager
def getcursor():
	con = DBCONN.getconn()
	try:
		yield con.cursor()
	except:
		cherrypy.log("Error while running SELECT", context='DATABASE', severity=logging.ERROR, traceback=False)
		con.rollback()
	finally:
		con.commit()
		DBCONN.putconn(con)

#thing where data is POSTed to
class Submit(object):
	@cherrypy.expose
	def default(self, groupid=None, groupwww=None):
		#do something
		#return somedata

#form to fill in
class Form(object):
	@cherrypy.expose
	def default(self, group):
		if not group.isdigit():
			cherrypy.response.status = 400
			return PAGE_ERROR_400
		
		capt = PsqlCaptcha(conn_pool=DBCONN)
		imgid, imgraw = capt.getcaptcha()
		img = bin2base64url(imgraw, capt.imgformat)

		
		
		cherrypy.response.headers['Content-Type'] = 'text/html; charset=utf-8'
		
		#return somedata

#main page showing number of things in the queue
class Root(object):
	submit = Submit()
	form = Form()
	@cherrypy.expose
	def index(self):
		for i in range(0, 4):
			try:
				data = None
				with getcursor() as cur:
					cur.execute('SELECT Count(*) FROM posts')
					data = cur.fetchone()
			except psycopg2.InterfaceError:
				if i == 3:
					cherrypy.response.status = 500
					return "Database connection error"
				if not data:
					continue
			break
			
		if not data:
			cherrypy.response.status = 404
			return PAGE_ERROR_404
			
		fullpg = u"Number of entries in the queue: %i" % data[0]
			
		cherrypy.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
		return fullpg.encode('utf-8')
	
	
def main():
	captchainit = PsqlCaptcha(conn_pool=DBCONN)
	captchainit.inittable()
	captchainit.updatecache()
	
	conf_path = os.path.dirname(os.path.abspath(__file__))
	conf_path = os.path.join(conf_path, "webserver.conf")
	if os.path.isfile(conf_path):
		cherrypy.config.update(conf_path)
	else:
		cherrypy.log("Configuration file NOT Found: %s" % conf_path, context='CONFIG', severity=logging.WARNING, traceback=False)
	cherrypy.config.update({'server.socket_host' : '0.0.0.0', })
	cherrypy.config.update({'server.socket_port' : int(os.environ.get('PORT', '5000')), })
	cherrypy.quickstart(Root())

if __name__ == '__main__':
	main()

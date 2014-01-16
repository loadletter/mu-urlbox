import cherrypy
import os, sys, base64, logging
import psycopg2, psycopg2.pool
from contextlib import contextmanager
from capcache import PsqlCaptcha
from htmltempl import *
from dbconf import *

MAXFIELDLEN = 4096

try:
	DBCONN = psycopg2.pool.ThreadedConnectionPool(1, 16, DSN)
except:
	cherrypy.log("UNABLE TO CONNECT TO DATABASE, TERMINATING!", context='DATABASE', severity=logging.ERROR, traceback=False)
	sys.exit(1)

def bin2base64url(img, fmt):
	b64 = 'data:image/' + fmt + ';base64,'
	b64 += base64.b64encode(img)
	return b64.replace("\n", "")

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
	def default(self, groupid=None, groupwww=None, captchatext=None, captchaid=None, refer=None):
		cherrypy.response.headers['Content-Type'] = CONTENT_HTML
		if not groupid or not groupwww or not captchatext or not captchaid:
			cherrypy.response.status = 400
			return PAGE_POST_MISSERROR
			
		if not groupid.isdigit() or len(captchaid) != 64:
			cherrypy.response.status = 400
			return PAGE_ERROR_400
		
		groupid = int(groupid)
		
		if len(groupwww) > MAXFIELDLEN or len(captchatext) > MAXFIELDLEN:
			cherrypy.response.status = 400
			return PAGE_POST_LONGERROR
		
		if refer == None:
			refer=''
		refer = refer[0:MAXFIELDLEN]
		
		remoteip = cherrypy.request.remote.ip
		uagent = ''
		if 'User-Agent' in cherrypy.request.headers:
			uagent = cherrypy.request.headers['User-Agent']
		
		captcha = PsqlCaptcha(conn_pool=DBCONN)
		if not captcha.validate(captchatext, captchaid):
			return PAGE_POST_CAPTCHAW
		
		todbdata = (groupid, groupwww, refer, remoteip, uagent)
		for i in range(0, 4):
			try:
				with getcursor() as cur:
					cur.execute("INSERT INTO posts (groupid, groupwww, refer, remoteip, uagent) VALUES (%s, %s, %s, %s, %s)", todbdata)
			except psycopg2.InterfaceError:
				if i == 3:
					cherrypy.response.status = 500
					return PAGE_POST_DBERROR
			break

		return PAGE_POST_SUCCESSFUL

#form to fill in
class Form(object):
	@cherrypy.expose
	def default(self, group, update='no'):
		cherrypy.response.headers['Content-Type'] = CONTENT_HTML
		if not group.isdigit():
			cherrypy.response.status = 400
			return PAGE_ERROR_400
		
		group = int(group)
		
		capt = PsqlCaptcha(conn_pool=DBCONN)
		imgid, imgraw = capt.getcaptcha()
		img = bin2base64url(imgraw, capt.imgformat)

		action = "Add"
		if update == 'yes':
			action = "Update"
		
		refpg = ''
		if 'Referer' in cherrypy.request.headers:
			refpg = cherrypy.request.headers['Referer']
		
		formpg = PAGE_TOP
		formpg += FORM_TITLE % (action, group)
		formpg += PAGE_MIDDLE
		formpg += html_page_form(action, group, img, imgid, refpg)
		formpg += PAGE_BOTTOM
		
		return formpg.encode('utf-8')

#main page showing number of things in the queue
class Root(object):
	submit = Submit()
	form = Form()
	@cherrypy.expose
	def index(self):
		cherrypy.response.headers['Content-Type'] = CONTENT_HTML
		
		data = None
		for i in range(0, 4):
			try:
				with getcursor() as cur:
					cur.execute('SELECT Count(*) FROM posts')
					data = cur.fetchone()
			except psycopg2.InterfaceError:
				if i == 3:
					cherrypy.response.status = 500
					return PAGE_POST_DBERROR
				if not data:
					continue
			break
			
		if not data:
			cherrypy.response.status = 404
			return PAGE_ERROR_404
			
		fullpg = PAGE_ROOT % data[0]
		
		return fullpg.encode('utf-8')
	
	
def main():
	captchainit = PsqlCaptcha(conn_pool=DBCONN)
	captchainit.inittable()
	captchainit.updatecache()
	
	with getcursor() as initcur:
		cur.execute("CREATE TABLE IF NOT EXISTS posts (id SERIAL PRIMARY KEY, groupid INTEGER, groupwww TEXT, refer TEXT, remoteip VARCHAR(46), uagent TEXT)")
		
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

import cherrypy
import os, sys, base64, logging
import psycopg2, psycopg2.pool
from contextlib import contextmanager
from htmltempl import *
from dbconf import *

MAXFIELDLEN = 4096

INSERT_IGNORE = '''INSERT INTO posts (groupid, groupwww, refer, remoteip, uagent)
SELECT %s, %s, %s, %s, %s
WHERE NOT EXISTS (SELECT 1 FROM posts WHERE groupid = %s AND groupwww = %s)'''

try:
	DBCONN = psycopg2.pool.ThreadedConnectionPool(1, 16, DSN)
except:
	cherrypy.log("UNABLE TO CONNECT TO DATABASE, TERMINATING!", context='DATABASE', severity=logging.ERROR, traceback=False)
	sys.exit(1)

@contextmanager
def getcursor(query_name):
	con = DBCONN.getconn()
	try:
		yield con.cursor()
	except:
		cherrypy.log("Error while running %s" % query_name, context='DATABASE', severity=logging.ERROR, traceback=False)
		con.rollback()
	finally:
		con.commit()
		DBCONN.putconn(con)

#thing where data is POSTed to
class Submit(object):
	@cherrypy.expose
	def default(self, groupid=None, groupwww=None, refer=None):
		cherrypy.response.headers['Content-Type'] = CONTENT_HTML
		if not groupid or not groupwww:
			cherrypy.response.status = 400
			return PAGE_POST_MISSERROR
			
		if not groupid.isdigit():
			cherrypy.response.status = 400
			return PAGE_ERROR_400
		
		groupid = int(groupid)
		
		if len(groupwww) > MAXFIELDLEN:
			cherrypy.response.status = 400
			return PAGE_POST_LONGERROR
		
		if refer == None:
			refer=''
		refer = refer[0:MAXFIELDLEN]
		
		remoteip = cherrypy.request.remote.ip
		uagent = ''
		if 'User-Agent' in cherrypy.request.headers:
			uagent = cherrypy.request.headers['User-Agent']
		
		todbdata = (groupid, groupwww, refer, remoteip, uagent, groupid, groupwww)
		for i in range(0, 4):
			try:
				with getcursor("INSERT") as cur:
					cur.execute(INSERT_IGNORE, todbdata)
			except psycopg2.InterfaceError:
				if i == 3:
					cherrypy.response.status = 500
					return PAGE_POST_DBERROR
				continue
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

		action = "Add"
		if update == 'yes':
			action = "Update"
		
		refpg = ''
		if 'Referer' in cherrypy.request.headers:
			refpg = cherrypy.request.headers['Referer']
		
		formpg = PAGE_TOP
		formpg += FORM_TITLE % (action, group)
		formpg += PAGE_MIDDLE
		formpg += html_page_form(action, group, refpg)
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
				with getcursor("SELECT COUNT") as cur:
					cur.execute('SELECT Count(*) FROM posts')
					data = cur.fetchone()
			except psycopg2.InterfaceError:
				if i == 3:
					cherrypy.response.status = 500
					return PAGE_POST_DBERROR
				continue
			break
			
		if not data:
			cherrypy.response.status = 404
			return PAGE_ERROR_404
			
		fullpg = PAGE_ROOT % data[0]
		
		return fullpg.encode('utf-8')
	
	
def main():
	with getcursor("INIT TABLE") as initcur:
		initcur.execute("CREATE TABLE IF NOT EXISTS posts (id SERIAL PRIMARY KEY, groupid INTEGER, groupwww TEXT, refer TEXT, remoteip VARCHAR(46), uagent TEXT)")
		
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

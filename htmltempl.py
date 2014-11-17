PAGE_TOP = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>'''
PAGE_MIDDLE = '''</title>
</head>
<body bgcolor = "#F0F3F7">'''
PAGE_BOTTOM = '''</body>
</html>'''

CONTENT_HTML = "text/html; charset=utf-8"

def html_page_error_custom(msg):
    return PAGE_TOP + msg + PAGE_MIDDLE + "<h4>" + msg + "</h4><hr>" + PAGE_BOTTOM

PAGE_ERROR_400 = html_page_error_custom("400 - Bad request")
PAGE_ERROR_403 = html_page_error_custom("403 - Forbidden")
PAGE_ERROR_404 = html_page_error_custom("404 - Not found")
PAGE_ERROR_500 = html_page_error_custom("500 - Internal server error")

FORM_TITLE = u"%s website url for group %i"

PAGE_FORM_1 = u'''<form name="sendurl" action="/submit" method="POST">'''

PAGE_FORM_2 = u'''<fieldset style="margin: auto;">
	<legend><h4>%s</h4></legend>
	<!-- disabled forms arent submitted --!>
	<input type="hidden" name=groupid value="%i">
	<input type="hidden" name="refer" value="%s">
	Group URL: <input type="text" name=groupwww style="width: 72%%;" value=""><input type="submit" value="Submit">
</fieldset>
</form>'''

def html_page_form(action, groupid, refer):
	legend = FORM_TITLE % (action, groupid)
	return PAGE_FORM_1 + PAGE_FORM_2 % (legend, groupid, refer)

def html_page_error_goback(msg):
	pg = PAGE_TOP + msg + PAGE_MIDDLE + '<h4>'
	pg += msg
	pg += '''</h4><br>Click <a href="javascript:history.back()">here</a> to go back<hr>'''
	pg += PAGE_BOTTOM
	return pg

def html_page_gohome(msg):
	pg = PAGE_TOP + msg + PAGE_MIDDLE + '<h4>'
	pg += msg
	pg += '''</h4><br>Click <a href="/">here</a> to go home<hr>'''
	pg += PAGE_BOTTOM
	return pg

PAGE_POST_SUCCESSFUL = html_page_gohome("Sent ;)")
PAGE_POST_DBERROR = html_page_error_goback("Error connecting to the database")
PAGE_POST_LONGERROR = html_page_error_goback("Field too long")
PAGE_POST_MISSERROR = html_page_error_goback("Missing required field")
PAGE_ROOT = PAGE_TOP + "Mangaupdates-urlfix suggestion box" + PAGE_MIDDLE + "Number of entries in the queue: %i" + PAGE_BOTTOM


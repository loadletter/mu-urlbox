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

PAGE_FORM_1 = u'''<form name="sendurl" action="/submit" method="POST">
<table width="100%">'''

PAGE_FORM_2 = u'''<tr>
		<td valign="top">
			<fieldset>
				<legend><h4>%s</h4></legend>
				Group ID: <input type="text" name=groupid size="6" disabled=true value="%i">
				<br>
				Group URL: <input type="text" name=groupwww style="width: 300px;">
			</fieldset>
			<input type="submit" value="Submit">
		</td>
		<td style="width: 126px; padding-top:9px; padding-bottom:3px;"  align="center" >
			<fieldset style="padding: 9px;">
			<img src="%s" alt="Captcha challenge">
			<br>
			<input type="text" name="captchatext" style="width: 120px;">
			<input type="hidden" name="captchaid" value="%s">
			</fieldset>
		</td>
	</tr>
</table>
</form>'''

def html_page_form(action, groupid, captchaimgstr, captchaid):
	legend = FORM_TITLE % (action, groupid)
	return PAGE_FORM_1 + PAGE_FORM_2 % (legend, groupid, captchaimgstr, captchaid)
	
#<button onclick="myFunction()">Try it</button>
#
#<script>
#function myFunction()
#{
#window.open('http://jsfiddle.net/xQSLL/show/','','scrollbars=no,resizable=yes, width=700,height=200,status=no,location=no,toolbar=no');
#}
#</script>


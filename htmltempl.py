PAGE_TOP = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>'''
PAGE_MIDDLE = '''</title>
</head>
<body bgcolor="#99cc99">'''
PAGE_BOTTOM = '''</body>
</html>'''

CONTENT_HTML = "text/html; charset=utf-8"

def html_page_error_custom(msg):
    return PAGE_TOP + msg + PAGE_MIDDLE + "<h4>" + msg + "</h4><hr>" + PAGE_BOTTOM

PAGE_ERROR_400 = html_page_error_custom("400 - Bad request")
PAGE_ERROR_403 = html_page_error_custom("403 - Forbidden")
PAGE_ERROR_404 = html_page_error_custom("404 - Not found")
PAGE_ERROR_500 = html_page_error_custom("500 - Internal server error")

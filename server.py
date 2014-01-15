import base64
#>>> h = 'be6e7836f8f6b4bf5cf79d78b44679296bb6f76f1cc187c6d15001ce0ac23771'
#>>> from capcache import PsqlCaptcha
#>>> test = PsqlCaptcha("dbname=testdb user=user")
#>>> test.validate('gluomr', h)
#
def bin2base64url(img, fmt):
	b64 = 'data:image/' + fmt + ';base64,'
	b64 += base64.b64encode(img)
	return b64

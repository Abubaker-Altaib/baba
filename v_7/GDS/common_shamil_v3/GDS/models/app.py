from bottle import *

@route("/" , method='get')
def bio_index():
	print request.environ.get('REMOTE_ADDR')

run(port=8081 , host="0.0.0.0")
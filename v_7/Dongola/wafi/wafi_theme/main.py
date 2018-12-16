import os
from web.controllers import main
from web import http
openerpweb = http

class Binary(main.Binary):
    def placeholder(self, req, image='placeholder.png'):
        """
        Overwrite method to return placeholder images from wafi_theme modules instead of web module
        """
        addons_path = openerpweb.addons_manifest['wafi_theme']['addons_path']
        try:
            return open(os.path.join(addons_path, 'wafi_theme', 'static', 'src', 'img', image), 'rb').read()
        except:
            return super(Binary,self).placeholder(req, image=image)
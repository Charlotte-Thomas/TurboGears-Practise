from tg import expose, TGController

# Controller
class RootController(TGController):
    @expose()
    def index(self):
        return 'Hello World'
# Passing parameters to your controllers is as simple as adding 
# them to the url with the same name of the parameters in your method, 
# TurboGears will automatically map them to function arguments when calling an exposed method.
# http://localhost:8080/hello?person=MyName
    @expose()
    def hello(self, person):
        return f'Hello {person}' 

# configurator
from tg import MinimalApplicationConfigurator

config = MinimalApplicationConfigurator()
config.update_blueprint({
    'root_controller': RootController()
})

application = config.make_wsgi_app()

# serve
from wsgiref.simple_server import make_server

print("Serving on port 8080...")
httpd = make_server('', 8080, application)
httpd.serve_forever()
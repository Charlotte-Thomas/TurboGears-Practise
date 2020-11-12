from tg import expose, TGController
# helpers
import webhelpers2
import webhelpers2.text
# for serving static files
from tg.configurator.components.statics import StaticsConfigurationComponent

# Controller
class RootController(TGController):
    @expose()
    def index(self):
        return 'Hello World'

    @expose('hello.xhtml')
    def hello(self, person=None):
        return dict(person=person)

# Passing parameters to your controllers is as simple as adding 
# them to the url with the same name of the parameters in your method, 
# TurboGears will automatically map them to function arguments when calling an exposed method.
# e.g. http://localhost:8080/hello?person=MyName


# configurator
from tg import MinimalApplicationConfigurator

config = MinimalApplicationConfigurator()
config.register(StaticsConfigurationComponent) # for static files
config.update_blueprint({
    'root_controller': RootController(),
    'renderers': ['kajiki'],
    'helpers': webhelpers2,
    'serve_static': True,
    'paths': {
        'static_files': 'public' # can now access any static files in public directory e.g. http://localhost:8080/styles.css
    }
})

application = config.make_wsgi_app()

# serve
from wsgiref.simple_server import make_server

print("Serving on port 8080...")
httpd = make_server('', 8080, application)
httpd.serve_forever()



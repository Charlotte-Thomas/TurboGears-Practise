from tg import expose, TGController
# helpers
import webhelpers2
import webhelpers2.text
# for serving static files
from tg.configurator.components.statics import StaticsConfigurationComponent

# db connection
from tg.configurator.components.sqlalchemy import SQLAlchemyConfigurationComponent

from tg.util import Bunch
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime

DBSession = scoped_session(sessionmaker(autoflush=True, autocommit=False))

DeclarativeBase = declarative_base()

# TurboGears will configure a SQLAlchemy engine for us, but it will require that we provide a data model or it will just crash
def init_model(engine):
    DBSession.configure(bind=engine)
    DeclarativeBase.metadata.create_all(engine) # Create tables if they do not exist

class Log(DeclarativeBase):
    __tablename__ = 'logs'

    uid = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    person = Column(String(50), nullable=False)

# Controller
class RootController(TGController):
    # @expose()
    # def index(self):
    #     return 'Hello World'

    # @expose('hello.xhtml')
    # def hello(self, person=None):
    #     return dict(person=person)
    
    @expose(content_type='text/plain')
    def index(self): # default page
        logs = DBSession.query(Log).order_by(Log.timestamp.desc()).all()
        return 'Past Greetings\n' + '\n'.join(['%s - %s' % (l.timestamp, l.person) for l in logs])
    # @expose() them to the web
    @expose('hello.xhtml')
    def hello(self, person=None):
        DBSession.add(Log(person=person or ''))
        DBSession.commit()
        return dict(person=person)

# Passing parameters to your controllers is as simple as adding 
# them to the url with the same name of the parameters in your method, 
# TurboGears will automatically map them to function arguments when calling an exposed method.
# e.g. http://localhost:8080/hello?person=MyName


# configurator
from tg import MinimalApplicationConfigurator

config = MinimalApplicationConfigurator()
config.register(StaticsConfigurationComponent) # for static files
config.register(SQLAlchemyConfigurationComponent)

config.update_blueprint({
    'model': Bunch(
    DBSession=DBSession,
    init_model=init_model
    ),
    'root_controller': RootController(),
    'renderers': ['kajiki'],
    'helpers': webhelpers2,
    'serve_static': True,
    'paths': {
        'static_files': 'public' # can now access any static files in public directory e.g. http://localhost:8080/styles.css
    },
    'use_sqlalchemy': True,
    'sqlalchemy.url': 'sqlite:///devdata.db' # equivalent of url in SQLAlchemy tutourial in base.py
})

application = config.make_wsgi_app()

# serve
from wsgiref.simple_server import make_server

print("Serving on port 8080...")
httpd = make_server('', 8080, application)
httpd.serve_forever()

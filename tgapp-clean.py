from tg import expose, TGController
import webhelpers2
import webhelpers2.text
from tg.configurator.components.statics import StaticsConfigurationComponent
from tg.configurator.components.sqlalchemy import SQLAlchemyConfigurationComponent
from tg import MinimalApplicationConfigurator
from tg.util import Bunch
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime
from wsgiref.simple_server import make_server


DBSession = scoped_session(sessionmaker(autoflush=True, autocommit=False))

DeclarativeBase = declarative_base()

def init_model(engine):
    DBSession.configure(bind=engine)
    DeclarativeBase.metadata.create_all(engine) # Create tables if they do not exist

class Log(DeclarativeBase):
    __tablename__ = 'logs'

    uid = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    person = Column(String(50), nullable=False)


class RootController(TGController):
    
    @expose(content_type='text/plain')
    def index(self):
        logs = DBSession.query(Log).order_by(Log.timestamp.desc()).all()
        return 'Past Greetings\n' + '\n'.join(['%s - %s' % (l.timestamp, l.person) for l in logs])

    @expose('hello.xhtml')
    def hello(self, person=None):
        DBSession.add(Log(person=person or ''))
        DBSession.commit()
        return dict(person=person)


config = MinimalApplicationConfigurator()
config.register(StaticsConfigurationComponent) # for static files
config.register(SQLAlchemyConfigurationComponent)

# For TurboGears serve our controller we must create the actual application:
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
        'static_files': 'public'
    },
    'use_sqlalchemy': True,
    'sqlalchemy.url': 'sqlite:///devdata.db' # equivalent of url in SQLAlchemy tutourial in base.py
})

application = config.make_wsgi_app()

print("Serving on port 8080...")
httpd = make_server('', 8080, application)
httpd.serve_forever()

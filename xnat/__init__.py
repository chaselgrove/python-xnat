import os
import pyxnat

if 'PYTHON_XNAT_DEBUG' in os.environ:
    _debug_flag = True
    if os.environ['PYTHON_XNAT_DEBUG'] == 'pyxnat':
        pyxnat.interfaces.DEBUG = True
        pyxnat.cache.DEBUG = True
        pyxnat.resources.DEBUG = True
        pyxnat.select.DEBUG = True
else:
    _debug_flag = False

def _debug(message):
    if _debug_flag:
        print 'DEBUG (python-xnat): %s' % message
    return

class XNATError(Exception):
    "base class for XNAT errors"

class NotConnectedError(XNATError):
    "not connected"

class _BaseConnection(object):

    def _check_connected(self):
        if not self.is_connected():
            raise NotConnectedError
        return

    def is_connected(self):
        if self.pyxnat_interface:
            return True
        return False

    def close(self):
        self._check_connected()
        uri = self.pyxnat_interface._get_entry_point() + '/JSESSION'
        self.pyxnat_interface._exec(uri, 'DELETE')
        self.pyxnat_interface = None
        return

    @property
    def projects(self):
        if self._projects is None:
            self._check_connected()
            self._projects = {}
            for project_id in self.pyxnat_interface.select.projects().get():
                self._projects[project_id] = _Project(self, project_id)
        return self._projects

    def get_subject(self, id):
        if id not in self._subjects:
            cols = ['xnat:subjectData/PROJECT']
            crit = [('xnat:subjectData/SUBJECT_ID', '=', id)]
            i = self.pyxnat_interface
            res = i.select('xnat:subjectData', cols).where(crit)
            if not len(res):
                raise ValueError, id
            project_id = res.items()[0][0]
            project = self.projects[project_id]
            self._subjects[id] = _UnboundSubject(project, id)
        return self._subjects[id]

class Connection(_BaseConnection):

    def __init__(self, uri=None, user=None, password=None):
        self.pyxnat_interface = None
        if uri is not None:
            self.uri = uri
        elif 'XNAT_URI' in os.environ:
            self.uri = os.environ['XNAT_URI']
        else:
            raise ValueError('no URI specified')
        if user is not None:
            self.user = user
        elif 'XNAT_USER' in os.environ:
            self.user = os.environ['XNAT_USER']
        else:
            raise ValueError('no user specified')
        if password is not None:
            pass
        elif 'XNAT_PASSWORD' in os.environ:
            user = os.environ['XNAT_PASSWORD']
        else:
            raise ValueError('no password specified')
        self.pyxnat_interface = pyxnat.Interface(self.uri.rstrip('/'), 
                                                 user=self.user, 
                                                 password=password)
        # force a check of the authentication
        self.pyxnat_interface._get_entry_point()
        self._projects = None
        self._subjects = {}
        return

    def __repr__(self):
        if not self.is_connected():
            return '<XNAT connection as %s to %s (closed)>' % (self.user, 
                                                               self.uri)
        return '<XNAT connection as %s to %s>' % (self.user, self.uri)

class AnonymousConnection(_BaseConnection):

    def __init__(self, uri=None):
        self.pyxnat_interface = None
        if uri is not None:
            self.uri = uri
        elif 'XNAT_URI' in os.environ:
            self.uri = os.environ['XNAT_URI']
        else:
            raise ValueError('no URI specified')
        self.pyxnat_interface = pyxnat.Interface(self.uri.rstrip('/'), 
                                                 anonymous=True)
        # force a check of the authentication
        self.pyxnat_interface._get_entry_point()
        self._projects = None
        self._subjects = {}
        return

    def __repr__(self):
        if not self.is_connected():
            return '<XNAT anonymous connection to %s (closed)>' % self.uri
        return '<XNAT anonymous connection to %s>' % self.uri

class _Project(object):

    def __init__(self, connection, id):
        self.id = id
        self.connection = connection
        self._pyxnat_project = None
        self._attributes = None
        self._subjects = None
        return

    def __repr__(self):
        return '<Project %s>' % self.id

    def _get_attribute(self, name):
        if self._attributes is None:
            names = ('secondary_ID', 'name', 'description')
            values = self.pyxnat_project.attrs.mget(names)
            lower_names = [ n.lower() for n in names ]
            self._attributes = dict(zip(lower_names, values))
        return self._attributes[name]

    @property
    def pyxnat_project(self):
        if not self._pyxnat_project:
            self.connection._check_connected()
            p = self.connection.pyxnat_interface.select.project(self.id)
            assert p.exists()
            self._pyxnat_project = p
        return self._pyxnat_project

    @property
    def subjects(self):
        if self._subjects is None:
            self._subjects = {}
            for label in self.pyxnat_project.subjects().get('label'):
                self._subjects[label] = _BoundSubject(self, label)
        return self._subjects

    @property
    def label(self):
        return self.pyxnat_project.label()

    @property
    def name(self):
        return self._get_attribute('name')

    @property
    def description(self):
        return self._get_attribute('description')

    @property
    def secondary_id(self):
        return self._get_attribute('secondary_id')

    @property
    def xml(self):
        return self.pyxnat_project.get()

class _BaseSubject(object):

    @property
    def connection(self):
        return self._project.connection

    @property
    def xml(self):
        return self.pyxnat_subject.get()

    @property
    def projects(self):
        if self._projects is None:
            self._projects = []
            for sp in self.pyxnat_subject.shares():
                project_label = sp.label()
                # pyxnat_subject.shares() may give us private projects
                if project_label in self.connection.projects:
                    project = self.connection.projects[project_label]
                    self._projects.append(project)
        return self._projects

class _UnboundSubject(_BaseSubject):

    def __init__(self, project, id):
        self.id = id
        self._project = project
        self._pyxnat_subject = None
        self._projects = None
        self._attributes = None
        self._experiments = None
        return

    def __repr__(self):
        return '<Subject %s>' % self.id

    def _get_attribute(self, name):
        if self._attributes is None:
            names = ['project', 'label']
            values = self.pyxnat_subject.attrs.mget(names)
            self._attributes = dict(zip(names, values))
        return self._attributes[name]

    @property
    def pyxnat_subject(self):
        if not self._pyxnat_subject:
            pyxnat_project = self._project.pyxnat_project
            self._pyxnat_subject = pyxnat_project.subject(self.id)
            assert self._pyxnat_subject.exists()
        return self._pyxnat_subject

    @property
    def primary_project(self):
        return self._project

    @property
    def primary_label(self):
        return self._get_attribute('label')

    @property
    def experiments(self):
        if self._experiments is None:
            self._experiments = {}
            for id in self.pyxnat_subject.experiments().get():
                self._experiments[id] = _UnboundExperiment(self, id)
        return self._experiments

class _BoundSubject(_BaseSubject):

    def __init__(self, project, label):
        self.label = label
        self._project = project
        self._pyxnat_subject = None
        self._projects = None
        self._experiments = None
        return

    def __repr__(self):
        return '<Subject %s in Project %s>' % (self.id, self.project.id)

    @property
    def pyxnat_subject(self):
        if not self._pyxnat_subject:
            pyxnat_project = self._project.pyxnat_project
            self._pyxnat_subject = pyxnat_project.subject(self.label)
            assert self._pyxnat_subject.exists()
        return self._pyxnat_subject

    @property
    def project(self):
        return self._project

    @property
    def id(self):
        return self.pyxnat_subject.id()

    @property
    def primary_project(self):
        return self.connection.get_subject(self.id).primary_project

    @property
    def primary_label(self):
        return self.connection.get_subject(self.id).primary_label

    @property
    def experiments(self):
        if self._experiments is None:
            self._experiments = {}
            for label in self.pyxnat_subject.experiments().get('label'):
                self._experiments[label] = _BoundExperiment(self, label)
        return self._experiments

class _BaseExperiment(object):

    @property
    def connection(self):
        return self._subject.connection

    def xml(self):
        return self.pyxnat_experiment.get()

class _UnboundExperiment(_BaseExperiment):

    def __init__(self, subject, id):
        self.id = id
        self._subject = subject
        self._pyxnat_experiment = None
        return

class _BoundExperiment(_BaseExperiment):

    def __init__(self, subject, label):
        self.id = label
        self._subject = subject
        self._pyxnat_experiment = None
        return

# eof

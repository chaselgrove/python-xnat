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
            return '<Connection as %s to %s (closed)>' % (self.user, 
                                                               self.uri)
        return '<Connection as %s to %s>' % (self.user, self.uri)

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
            return '<Anonymous connection to %s (closed)>' % self.uri
        return '<Anonymous connection to %s>' % self.uri

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
                self._subjects[label] = _Subject(self, label)
        return self._subjects

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

class _Subject(object):

    def __init__(self, project, label):
        self.project = project
        self._projects = None
        self._experiments = None
        self.label = label
        self.pyxnat_subject = self.project.pyxnat_project.subject(self.label)
        self.id = self.pyxnat_subject.id()
        self.connection = self.project.connection
        self.primary_project = self.connection.projects[self.pyxnat_subject.attrs.get('project')]
        self.primary_label = self.primary_project.pyxnat_project.subject(self.id).label()
        return

    def __repr__(self):
        return '<Subject %s in Project %s>' % (self.label, self.project.label)

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

    @property
    def experiments(self):
        if self._experiments is None:
            self._experiments = {}
            for label in self.pyxnat_subject.experiments().get('label'):
                self._experiments[label] = _Experiment(self, label)
        return self._experiments

class _Experiment(object):

    def __init__(self, subject, label):
        self.label = label
        self.subject = subject
        self.project = self.subject.project
        self.pyxnat_experiment = self.subject.pyxnat_subject.experiment(self.label)
        self.id = self.pyxnat_experiment.id()
        self.primary_subject = self.subject.primary_project.subjects[self.subject.id]
        self.primary_label = self.primary_subject.pyxnat_subject.experiment(self.id).label()
        self.connection = self.subject.connection
        self._scans = None
        self._reconstructions = None
        self._assessments = None
        return

    def __repr__(self):
        return '<Experiment %s for Subject %s>' % (self.label, 
                                                   self.subject.label)

    @property
    def xml(self):
        return self.pyxnat_experiment.get()

    @property
    def scans(self):
        if self._scans is None:
            self._scans = {}
            for id in self.pyxnat_experiment.scans().get():
                self._scans[id] = _Scan(self, id)
        return self._scans

    @property
    def reconstructions(self):
        if self._reconstructions is None:
            self._reconstructions = {}
            for id in self.pyxnat_experiment.reconstructions().get():
                self._reconstructions[id] = _Reconstruction(self, id)
        return self._reconstructions

    @property
    def assessments(self):
        if self._assessments is None:
            self._assessments = {}
            for id in self.pyxnat_experiment.assessors().get():
                self._assessments[id] = _Assessment(self, id)
        return self._assessments

class _Scan(object):

    def __init__(self, experiment, id):
        self.experiment = experiment
        self.subject = self.experiment.subject
        self.project = self.subject.project
        self.connection = self.project.connection
        self.id = id
        self.pyxnat_scan = self.experiment.pyxnat_experiment.scan(self.id)
        return

    def __repr__(self):
        return '<Scan %s for Experiment %s>' % (self.id, self.experiment.label)

    @property
    def xml(self):
        return self.pyxnat_scan.get()

class _Reconstruction(object):

    def __init__(self, experiment, id):
        self.experiment = experiment
        self.subject = self.experiment.subject
        self.project = self.subject.project
        self.connection = self.project.connection
        self.id = id
        self.pyxnat_reconstruction = self.experiment.pyxnat_experiment.reconstruction(self.id)
        return

    def __repr__(self):
        return '<Reconstruction %s for Experiment %s>' % (self.id, 
                                                          self.experiment.label)

    @property
    def xml(self):
        return self.pyxnat_reconstruction.get()

class _Assessment(object):

    def __init__(self, experiment, id):
        self.experiment = experiment
        self.subject = self.experiment.subject
        self.project = self.subject.project
        self.connection = self.project.connection
        self.id = id
        self.pyxnat_assessment = self.experiment.pyxnat_experiment.assessor(self.id)
        return

    def __repr__(self):
        return '<Assessment %s for Experiment %s>' % (self.id, 
                                                      self.experiment.label)

    @property
    def xml(self):
        return self.pyxnat_assessment.get()

# eof

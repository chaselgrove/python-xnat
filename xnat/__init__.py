import os
try:
    import suds
except ImportError:
    suds = None
if suds:
    import urllib2
    import urlparse
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

class HTTPSudsPreprocessor(urllib2.BaseHandler):

    def http_request(self, req):
        req.add_header('Cookie', 'JSESSIONID=%s' % self.jsessionid)
        return req

    https_request = http_request

class _BaseConnection(object):

    def _check_connected(self):
        if not self.is_connected():
            raise NotConnectedError
        return

    def _check_suds(self):
        if suds is None:
            raise ImportError, 'Module suds not found'
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

    @property
    def _jsessionid(self):
        self._check_connected()
        return self.pyxnat_interface._jsession.split('=')[1]

    def _soap_call(self, jws, operation, inputs):
        self._check_suds()
        self._check_connected()
        if urlparse.urlparse(self.uri).scheme == 'https':
            t = suds.transport.https.HttpTransport()
        else:
            t = suds.transport.http.HttpTransport()
        t.urlopener = urllib2.build_opener(HTTPSudsPreprocessor)
        for h in t.urlopener.handlers:
            if isinstance(h, HTTPSudsPreprocessor):
                h.jsessionid = self._jsessionid
        ws_url = '%s/axis/%s' % (self.uri, jws)
        client = suds.client.Client('%s?wsdl' % ws_url, transport=t)
        client.add_prefix('se', 'http://schemas.xmlsoap.org/soap/encoding/')
        typed_inputs = []
        for var in inputs:
            if isinstance(var, basestring):
                ti = client.factory.create('se:string')
                ti.value = var
                typed_inputs.append(ti)
            else:
                raise TypeError, 'unsupported type for variable'
        client.set_options(location=ws_url)
        f = getattr(client.service, operation)
        return f(*typed_inputs)

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
        self._resources = None
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

    @property
    def resources(self):
        if self._resources is None:
            self._resources = {}
            for label in self.pyxnat_project.resources().get('label'):
                self._resources[label] = _ProjectResource(self, label)
        return self._resources

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
        self._resources = None
        return

    def __repr__(self):
        return '<Subject %s in Project %s>' % (self.label, self.project.id)

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

    @property
    def resources(self):
        if self._resources is None:
            self._resources = {}
            for label in self.pyxnat_subject.resources().get('label'):
                self._resources[label] = _SubjectResource(self, label)
        return self._resources

class _Experiment(object):

    def __init__(self, subject, label):
        self.label = label
        self.subject = subject
        self.project = self.subject.project
        self.pyxnat_experiment = self.subject.pyxnat_subject.experiment(self.label)
        self.id = self.pyxnat_experiment.id()
        primary_subject_label = self.subject.primary_project.pyxnat_project.subject(self.subject.id).label()
        self.primary_subject = self.subject.primary_project.subjects[primary_subject_label]
        self.primary_label = self.primary_subject.pyxnat_subject.experiment(self.id).label()
        self.connection = self.subject.connection
        self._scans = None
        self._reconstructions = None
        self._assessments = None
        self._resources = None
        self._workflows = None
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
            for id in self.pyxnat_experiment.assessors().get('label'):
                self._assessments[id] = _Assessment(self, id)
        return self._assessments

    @property
    def workflows(self):
        if self._workflows is None:
            self._workflows = {}
            inputs = (self.connection._jsessionid, 
                      'wrk:workflowData.ID', 
                      '=', 
                      self.id, 
                      'wrk:workflowData')
            try:
                w_ids = self.connection._soap_call('GetIdentifiers.jws', 
                                                   'search', 
                                                   inputs)
            # this exception with this message is raised if there are no workflows
            except suds.WebFault, data:
                if not "Field not found: 'wrk:workflowData/label'" in str(data):
                    raise
                w_ids = []
            for w_id in w_ids:
                w_id = int(w_id)
                self._workflows[w_id] = _Workflow(self, w_id)
        return self._workflows

    @property
    def resources(self):
        if self._resources is None:
            self._resources = {}
            for label in self.pyxnat_experiment.resources().get('label'):
                self._resources[label] = _ExperimentResource(self, label)
        return self._resources

class _Scan(object):

    def __init__(self, experiment, id):
        self.experiment = experiment
        self.subject = self.experiment.subject
        self.project = self.subject.project
        self.connection = self.project.connection
        self.id = id
        self.pyxnat_scan = self.experiment.pyxnat_experiment.scan(self.id)
        self._resources = None
        return

    def __repr__(self):
        return '<Scan %s for Experiment %s>' % (self.id, self.experiment.label)

    @property
    def xml(self):
        return self.pyxnat_scan.get()

    @property
    def resources(self):
        if self._resources is None:
            self._resources = {}
            for label in self.pyxnat_scan.resources().get('label'):
                self._resources[label] = _ScanResource(self, label)
        return self._resources

class _Reconstruction(object):

    def __init__(self, experiment, id):
        self.experiment = experiment
        self.subject = self.experiment.subject
        self.project = self.subject.project
        self.connection = self.project.connection
        self.id = id
        self.pyxnat_reconstruction = self.experiment.pyxnat_experiment.reconstruction(self.id)
        self._in_resources = None
        self._out_resources = None
        return

    def __repr__(self):
        return '<Reconstruction %s for Experiment %s>' % (self.id, 
                                                          self.experiment.label)

    @property
    def xml(self):
        return self.pyxnat_reconstruction.get()

    @property
    def in_resources(self):
        if self._in_resources is None:
            self._in_resources = {}
            for label in self.pyxnat_reconstruction.in_resources().get('label'):
                self._in_resources[label] = _ReconstructionInResource(self, label)
        return self._in_resources

    @property
    def out_resources(self):
        if self._out_resources is None:
            self._out_resources = {}
            for label in self.pyxnat_reconstruction.out_resources().get('label'):
                self._out_resources[label] = _ReconstructionOutResource(self, label)
        return self._out_resources

class _Assessment(object):

    def __init__(self, experiment, id):
        self.experiment = experiment
        self.subject = self.experiment.subject
        self.project = self.subject.project
        self.connection = self.project.connection
        self.id = id
        self.pyxnat_assessment = self.experiment.pyxnat_experiment.assessor(self.id)
        self._in_resources = None
        self._out_resources = None
        return

    def __repr__(self):
        return '<Assessment %s for Experiment %s>' % (self.id, 
                                                      self.experiment.label)

    @property
    def xml(self):
        return self.pyxnat_assessment.get()

    @property
    def in_resources(self):
        if self._in_resources is None:
            self._in_resources = {}
            for label in self.pyxnat_assessment.in_resources().get('label'):
                self._in_resources[label] = _AssessmentInResource(self, label)
        return self._in_resources

    @property
    def out_resources(self):
        if self._out_resources is None:
            self._out_resources = {}
            for label in self.pyxnat_assessment.out_resources().get('label'):
                self._out_resources[label] = _AssessmentOutResource(self, label)
        return self._out_resources

class _BaseResource(object):

    pass

class _ProjectResource(_BaseResource):

    def __init__(self, project, label):
        self.project = project
        self.label = label
        self.connection = project.connection
        self.pyxnat_resource = self.project.pyxnat_project.resource(self.label)
        self.id = int(self.pyxnat_resource.id())
        self._files = None
        return

    def __repr__(self):
        return '<Resource %s for Project %s>' % (self.label, self.project.id)

    @property
    def files(self):
        if self._files is None:
            self._files = {}
            for f in self.pyxnat_resource.files():
                path = f.attributes()['path']
                self._files[path] = _File(self, self, path)
        return self._files

class _SubjectResource(_BaseResource):

    def __init__(self, subject, label):
        self.subject = subject
        self.project = subject.project
        self.label = label
        self.connection = subject.connection
        self.pyxnat_resource = self.subject.pyxnat_subject.resource(self.label)
        self.id = int(self.pyxnat_resource.id())
        self._files = None
        return

    def __repr__(self):
        return '<Resource %s for Subject %s>' % (self.label, self.subject.label)

    @property
    def files(self):
        if self._files is None:
            self._files = {}
            for f in self.pyxnat_resource.files():
                path = f.attributes()['path']
                self._files[path] = _File(self, self, path)
        return self._files

class _ExperimentResource(_BaseResource):

    def __init__(self, experiment, label):
        self.experiment = experiment
        self.subject = experiment.subject
        self.project = self.subject.project
        self.label = label
        self.connection = experiment.connection
        self.pyxnat_resource = self.experiment.pyxnat_experiment.resource(self.label)
        self.id = int(self.pyxnat_resource.id())
        self._files = None
        return

    def __repr__(self):
        return '<Resource %s for Experiment %s>' % (self.label, self.experiment.label)

    @property
    def files(self):
        if self._files is None:
            self._files = {}
            for f in self.pyxnat_resource.files():
                path = f.attributes()['path']
                self._files[path] = _File(self, self, path)
        return self._files

class _ScanResource(_BaseResource):

    def __init__(self, scan, label):
        self.scan = scan
        self.experiment = scan.experiment
        self.subject = scan.subject
        self.project = scan.project
        self.connection = scan.connection
        self.label = label
        self._files = None
        self.pyxnat_resource = self.scan.pyxnat_scan.resource(self.label)
        self.id = int(self.pyxnat_resource.id())
        # 2011-12-02 bug: files are not returned for shared resources
        # so we set self._primary_scan, delay self._primary_resource until 
        # needed, and use that in self.files below
        # _File also uses this primary resource
        primary_subject = self.experiment.primary_subject
        primary_experiment_label = primary_subject.pyxnat_subject.experiment(self.experiment.id).label()
        primary_experiment = primary_subject.experiments[primary_experiment_label]
        self._primary_scan = primary_experiment.scans[self.scan.id]
        return

    def __repr__(self):
        return '<Resource %s for Scan %s>' % (self.label, self.scan.label)

    @property
    def _primary_resource(self):
        return self._primary_scan.resources[self.label]

    @property
    def files(self):
        if self._files is None:
            self._files = {}
            for f in self._primary_resource.pyxnat_resource.files():
                path = f.attributes()['path']
                self._files[path] = _File(self, self._primary_resource, path)
        return self._files

class _BaseReconstructionResource(_BaseResource):

    @property
    def files(self):
        if self._files is None:
            self._files = {}
            for f in self.pyxnat_resource.files():
                path = f.attributes()['path']
                self._files[path] = _File(self, self, path)
        return self._files

class _ReconstructionInResource(_BaseReconstructionResource):

    def __init__(self, reconstruction, label):
        self.reconstruction = reconstruction
        self.experiment = reconstruction.experiment
        self.subject = reconstruction.subject
        self.project = reconstruction.project
        self.connection = reconstruction.connection
        self.label = label
        self.pyxnat_resource = self.reconstruction.pyxnat_reconstruction.in_resource(self.label)
        self.id = int(self.pyxnat_resource.id())
        self._files = None
        return

    def __repr__(self):
        return '<Input resource %s for Reconstruction %s>' % (self.label, self.reconstruction.id)

class _ReconstructionOutResource(_BaseReconstructionResource):

    def __init__(self, reconstruction, label):
        self.reconstruction = reconstruction
        self.experiment = reconstruction.experiment
        self.subject = reconstruction.subject
        self.project = reconstruction.project
        self.connection = reconstruction.connection
        self.label = label
        self.pyxnat_resource = self.reconstruction.pyxnat_reconstruction.out_resource(self.label)
        self.id = int(self.pyxnat_resource.id())
        self._files = None
        return

    def __repr__(self):
        return '<Output resource %s for Reconstruction %s>' % (self.label, self.reconstruction.id)

class _BaseAssessmentResource(_BaseResource):

    @property
    def files(self):
        if self._files is None:
            self._files = {}
            for f in self.pyxnat_resource.files():
                path = f.attributes()['path']
                self._files[path] = _File(self, self, path)
        return self._files

class _AssessmentInResource(_BaseAssessmentResource):

    def __init__(self, assessment, label):
        self.assessment = assessment
        self.experiment = assessment.experiment
        self.subject = assessment.subject
        self.project = assessment.project
        self.connection = assessment.connection
        self.label = label
        self.pyxnat_resource = self.assessment.pyxnat_assessment.in_resource(self.label)
        self.id = int(self.pyxnat_resource.id())
        self._files = None
        return

    def __repr__(self):
        return '<Input resource %s for Assessment %s>' % (self.label, self.assessment.id)

class _AssessmentOutResource(_BaseAssessmentResource):

    def __init__(self, assessment, label):
        self.assessment = assessment
        self.experiment = assessment.experiment
        self.subject = assessment.subject
        self.project = assessment.project
        self.connection = assessment.connection
        self.label = label
        self.pyxnat_resource = self.assessment.pyxnat_assessment.out_resource(self.label)
        self.id = int(self.pyxnat_resource.id())
        self._files = None
        return


    def __repr__(self):
        return '<Output resource %s for Assessment %s>' % (self.label, self.assessment.id)

class _File(object):

    def __init__(self, resource, primary_resource, path):
        self.resource = resource
        self._primary_resource = primary_resource
        self.path = path
        self.connection = self.resource.connection
        self.pyxnat_file = self._primary_resource.pyxnat_resource.file(self.path)
        return

    def __repr__(self):
        return '<File %s for Resource %s>' % (self.path, self.resource.label)

    @property
    def size(self):
        return int(self.pyxnat_file.size())

    @property
    def last_modified(self):
        return self.pyxnat_file.last_modified()

    def read(self):
        fname = self.pyxnat_file.get()
        return open(fname).read()

class _Workflow(object):

    def __init__(self, experiment, id):
        self.experiment = experiment
        self.id = id
        return

# eof

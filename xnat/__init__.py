import os
import datetime
import xml.dom.minidom
import dateutil.parser
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

class DoesNotExistError(XNATError):
    "entity does not exist"

class _Dictionary:

    """ordered, immutable dictionary"""

    def __init__(self, t):
        self._keys = []
        self._dict = {}
        for (key, value) in t:
            if key in self._keys:
                self._keys.remove(key)
            self._keys.append(key)
            self._dict[key] = value
        return

    def __contains__(self, key):
        return key in self._dict

    def __getitem__(self, key):
        return self._dict[key]

    def __iter__(self):
        for key in self._keys:
            yield key
        return

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        parts = []
        for (key, value) in self.iteritems():
            parts.append('%s: %s' % (repr(key), repr(value)))
        parts = [ '%s: %s' % (repr(k), repr(v)) for (k, v) in self.iteritems() ]
        return '{%s}' % ', '.join(parts)

    def has_key(self, key):
        return key in self._dict

    def items(self):
        return [ v for v in self.iteritems() ]

    def iteritems(self):
        for key in self:
            yield (key, self._dict[key])
        return

    def iterkeys(self):
        for key in self:
            yield key
        return

    def keys(self):
        return [ key for key in self ]

    def itervalues(self):
        for key in self:
            yield self._dict[key]
        return

    def values(self):
        return [ v for v in self.itervalues() ]

class HTTPSudsPreprocessor(urllib2.BaseHandler):

    def http_request(self, req):
        req.add_header('Cookie', 'JSESSIONID=%s' % self.jsessionid)
        return req

    https_request = http_request

class _BaseConnection(object):

    def _check_connected(self):
        if not self.is_connected():
            raise NotConnectedError()
        return

    def _check_suds(self):
        if suds is None:
            raise ImportError('Module suds not found')
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
            projects = []
            for project_id in self.pyxnat_interface.select.projects().get():
                projects.append((project_id, _Project(self, project_id)))
            self._projects = _Dictionary(projects)
        return self._projects

    def find_subject(self, subject_id):
        cols =  ['xnat:subjectData/PROJECT']
        constraints = [('xnat:subjectData/ID', '=', subject_id)]
        res = self.pyxnat_interface.select('xnat:subjectData', cols).where(constraints)
        if len(res) == 0:
            raise ValueError()
        project = self.projects[res[0]['project']]
        return project.subjects_by_id[subject_id]

    def find_experiment(self, experiment_id):
        # we use a hybrid approach here:
        #     /data/experiments?ID=... will use XNAT's facility for finding 
        #     an experiment; this will give us an empty list if it is not 
        #     found (so we don't have to handle 404s)
        # but this doesn't give us the subject, so:
        #     pyxnat's resources.Experiment() on the URI returned in the 
        #     above to get and parse the XML with the subject ID
        entry_point = self.pyxnat_interface._get_entry_point()
        uri = '%s/experiments?ID=%s' % (entry_point, experiment_id)
        result = self.pyxnat_interface._get_json(uri)
        if not result:
            raise ValueError(experiment_id)
        uri = result[0]['URI']
        project = self.projects[result[0]['project']]
        pyxnat_experiment = pyxnat.core.resources.Experiment(uri, self.pyxnat_interface)
        subject_id = pyxnat_experiment.xpath('//xnat:subject_ID')[0].text
        subject = project.subjects_by_id[subject_id]
        return subject.experiments_by_id[experiment_id]

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
        xsd_url = 'http://schemas.xmlsoap.org/soap/encoding/'
        imp = suds.xsd.doctor.Import(xsd_url)
        doctor = suds.xsd.doctor.ImportDoctor(imp)
        client = suds.client.Client('%s?wsdl' % ws_url,
                                    transport=t,
                                    doctor=doctor)
        client.add_prefix('se', 'http://schemas.xmlsoap.org/soap/encoding/')
        typed_inputs = []
        for var in inputs:
            if isinstance(var, basestring):
                ti = client.factory.create('se:string')
                ti.value = var
                typed_inputs.append(ti)
            elif isinstance(var, bool):
                ti = client.factory.create('se:boolean')
                ti.value = var
                typed_inputs.append(ti)
            else:
                raise TypeError('unsupported type for variable')
        client.set_options(location=ws_url)
        f = getattr(client.service, operation)
        rv = f(*typed_inputs)
        # reset the pyxnat cache in case this is a write operation
        self.pyxnat_interface._memcache = {}
        return rv

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
        return

    def __repr__(self):
        if not self.is_connected():
            return '<Anonymous connection to %s (closed)>' % self.uri
        return '<Anonymous connection to %s>' % self.uri

class _Project(object):

    def __init__(self, connection, id):
        self._id = id
        self._connection = connection
        self._pyxnat_project = None
        self._attributes = None
        self._subjects = None
        self._subjects_by_id = None
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

    def _get_subjects(self):
        subjects = []
        subjects_by_id = []
        for s in self.pyxnat_project.subjects():
            label = s.label()
            subjects.append((label, _Subject(self, label)))
            subjects_by_id.append((s.id(), _Subject(self, label)))
        self._subjects = _Dictionary(subjects)
        self._subjects_by_id = _Dictionary(subjects_by_id)
        return

    def create_subject(self, label):
        if not self.pyxnat_project.exists():
            raise DoesNotExistError('Project %s does not exist' % self.id)
        pyxnat_subject = self.pyxnat_project.subject(label)
        if pyxnat_subject.exists():
            raise ValueError('subject %s exists for project %s' % (label, self.id))
        pyxnat_subject.create()
        assert pyxnat_subject.exists()
        self._subjects = None
        self._subjects_by_id = None
        return self.subjects[label]

    @property
    def id(self):
        return self._id

    @property
    def connection(self):
        return self._connection

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
            self._get_subjects()
        return self._subjects

    @property
    def subjects_by_id(self):
        if self._subjects_by_id is None:
            self._get_subjects()
        return self._subjects_by_id

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
            resources = []
            for label in self.pyxnat_project.resources().get('label'):
                resources.append((label, _ProjectResource(self, label)))
            self._resources = _Dictionary(resources)
        return self._resources

class _Subject(object):

    def __init__(self, project, label):
        self._project = project
        self._projects = None
        self._experiments = None
        self._experiments_by_id = None
        self._label = label
        self._pyxnat_subject = self.project.pyxnat_project.subject(self.label)
        self._id = self.pyxnat_subject.id()
        self._connection = self.project.connection
        self._primary_project = self.connection.projects[self.pyxnat_subject.attrs.get('project')]
        self._primary_label = self.primary_project.pyxnat_project.subject(self.id).label()
        self._resources = None
        return

    def __repr__(self):
        return '<Subject %s in Project %s>' % (self.label, self.project.id)

    @property
    def xml(self):
        return self.pyxnat_subject.get()

    def _set_experiments(self):
        experiments = []
        experiments_by_id = []
        for e in self.pyxnat_subject.experiments():
            label = e.label()
            experiments.append((label, _Experiment(self, label)))
            experiments_by_id.append((e.id(), _Experiment(self, label)))
        self._experiments = _Dictionary(experiments)
        self._experiments_by_id = _Dictionary(experiments_by_id)
        return

    @property
    def project(self):
        return self._project

    @property
    def label(self):
        return self._label

    @property
    def pyxnat_subject(self):
        return self._pyxnat_subject

    @property
    def id(self):
        return self._id

    @property
    def connection(self):
        return self._connection

    @property
    def primary_project(self):
        return self._primary_project

    @property
    def primary_label(self):
        return self._primary_label

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
            self._set_experiments()
        return self._experiments

    @property
    def experiments_by_id(self):
        if self._experiments_by_id is None:
            self._set_experiments()
        return self._experiments_by_id

    @property
    def resources(self):
        if self._resources is None:
            resources = []
            for label in self.pyxnat_subject.resources().get('label'):
                resources.append((label, _SubjectResource(self, label)))
            self._resources = _Dictionary(resources)
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
            scans = []
            for id in self.pyxnat_experiment.scans().get():
                scans.append((id, _Scan(self, id)))
            self._scans = _Dictionary(scans)
        return self._scans

    @property
    def reconstructions(self):
        if self._reconstructions is None:
            reconstructions = []
            for id in self.pyxnat_experiment.reconstructions().get():
                reconstructions.append((id, _Reconstruction(self, id)))
            self._reconstructions = _Dictionary(reconstructions)
        return self._reconstructions

    @property
    def assessments(self):
        if self._assessments is None:
            assessments = []
            for label in self.pyxnat_experiment.assessors().get('label'):
                assessments.append((label, _Assessment(self, label)))
            self._assessments = _Dictionary(assessments)
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
            w_ids = [ int(w_id) for w_id in w_ids ]
            workflows = [ _Workflow(self, w_id) for w_id in w_ids ]
            self._workflows = _Dictionary(zip(w_ids, workflows))
        return self._workflows

    @property
    def resources(self):
        if self._resources is None:
            resources = []
            for label in self.pyxnat_experiment.resources().get('label'):
                resources.append((label, _ExperimentResource(self, label)))
            self._resources = _Dictionary(resources)
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
            resources = []
            for label in self.pyxnat_scan.resources().get('label'):
                resources.append((label, _ScanResource(self, label)))
            self._resources = _Dictionary(resources)
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
            resources = []
            for label in self.pyxnat_reconstruction.in_resources().get('label'):
                resources.append((label, _ReconstructionInResource(self, label)))
            self._in_resources = _Dictionary(resources)
        return self._in_resources

    @property
    def out_resources(self):
        if self._out_resources is None:
            resources = []
            for label in self.pyxnat_reconstruction.out_resources().get('label'):
                resources.append((label, _ReconstructionOutResource(self, label)))
            self._out_resources = _Dictionary(resources)
        return self._out_resources

class _Assessment(object):

    def __init__(self, experiment, label):
        self.experiment = experiment
        self.subject = self.experiment.subject
        self.project = self.subject.project
        self.connection = self.project.connection
        self.label = label
        self.pyxnat_assessment = self.experiment.pyxnat_experiment.assessor(self.label)
        self.id = self.pyxnat_assessment.id()
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
            resources = []
            for label in self.pyxnat_assessment.in_resources().get('label'):
                resources.append((label, _AssessmentInResource(self, label)))
            self._in_resources = _Dictionary(resources)
        return self._in_resources

    @property
    def out_resources(self):
        if self._out_resources is None:
            resources = []
            for label in self.pyxnat_assessment.out_resources().get('label'):
                resources.append((label, _AssessmentOutResource(self, label)))
            self._out_resources = _Dictionary(resources)
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
            files = []
            for f in self.pyxnat_resource.files():
                path = f.attributes()['path']
                files.append((path, _File(self, self, path)))
            self._files = _Dictionary(files)
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
            files = []
            for f in self.pyxnat_resource.files():
                path = f.attributes()['path']
                files.append((path, _File(self, self, path)))
            self._files = _Dictionary(files)
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
            files = []
            for f in self.pyxnat_resource.files():
                path = f.attributes()['path']
                files.append((path, _File(self, self, path)))
            self._files = _Dictionary(files)
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
        return '<Resource %s for Scan %s>' % (self.label, self.scan.id)

    @property
    def _primary_resource(self):
        return self._primary_scan.resources[self.label]

    @property
    def files(self):
        if self._files is None:
            files = []
            for f in self._primary_resource.pyxnat_resource.files():
                path = f.attributes()['path']
                files.append((path, _File(self, self._primary_resource, path)))
            self._files = _Dictionary(files)
        return self._files

class _BaseReconstructionResource(_BaseResource):

    @property
    def files(self):
        if self._files is None:
            files = []
            for f in self.pyxnat_resource.files():
                path = f.attributes()['path']
                files.append((path, _File(self, self, path)))
            self._files = _Dictionary(files)
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
            files = []
            for f in self.pyxnat_resource.files():
                path = f.attributes()['path']
                files.append((path, _File(self, self, path)))
            self._files = _Dictionary(files)
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
        return dateutil.parser.parse(self.pyxnat_file.last_modified())

    def read(self):
        fname = self.pyxnat_file.get()
        return open(fname).read()

class _Workflow(object):

    def __init__(self, experiment, id):
        self.experiment = experiment
        self.subject = experiment.subject
        self.project = experiment.project
        self.connection = experiment.connection
        self.id = id
        self._reset()
        return

    def _reset(self):
        "reset the object's cache to force synchronization with XNAT"
        self._xml = None
        self._doc = None
        self._workflow_node = None
        return

    def _update_xnat(self):
        inputs = (self.connection._jsessionid, 
                  self.doc.toxml(), 
                  False, 
                  True)
        self.connection._soap_call('StoreXML.jws', 'store', inputs)
        self._reset()
        return

    def _remove_workflow_node_attribute(self, attr_name):
        try:
            self.workflow_node.removeAttribute(attr_name)
        except xml.dom.NotFoundErr:
            pass
        return

    @property
    def xml(self):
        if self._xml is None:
            uri = '/app/template/XMLSearch.vm/id/%d/data_type/wrk:workflowData' % self.id
            self._xml = self.connection.pyxnat_interface._exec(uri)
        return self._xml

    @property
    def doc(self):
        if self._doc is None:
            self._doc = xml.dom.minidom.parseString(self.xml)
        return self._doc

    @property
    def workflow_node(self):
        if self._workflow_node is None:
            self._workflow_node = self.doc.getElementsByTagName('wrk:Workflow')[0]
        return self._workflow_node

    def _attribute_or_none(self, attribute_name):
        val = self.workflow_node.getAttribute(attribute_name)
        if not val:
            return None
        return val

    @property
    def pipeline_name(self):
        return self.workflow_node.getAttribute('pipeline_name')

    @property
    def launch_time(self):
        s_val = self.workflow_node.getAttribute('launch_time')
        return dateutil.parser.parse(s_val)

    @property
    def status(self):
        return self.workflow_node.getAttribute('status')

    @status.setter
    def status(self, value):
        if not isinstance(value, basestring):
            raise TypeError('status must be a string')
        self.workflow_node.setAttribute('status', value)
        self._update_xnat()
        return

    @property
    def step_launch_time(self):
        s_val = self.workflow_node.getAttribute('current_step_launch_time')
        if not s_val:
            return None
        return dateutil.parser.parse(s_val)

    @step_launch_time.setter
    def step_launch_time(self, value):
        if value is None:
            self._remove_workflow_node_attribute('current_step_launch_time')
        elif not isinstance(value, datetime.datetime):
            raise TypeError('step_launch_time must be a dateime.datetime instance or None')
        if value is not None:
            self.workflow_node.setAttribute('current_step_launch_time', value.strftime('%Y-%m-%dT%H:%M:%S'))
        self._update_xnat()
        return

    @property
    def step_id(self):
        return self._attribute_or_none('current_step_id')

    @step_id.setter
    def step_id(self, value):
        if value is None:
            self._remove_workflow_node_attribute('current_step_id')
        elif not isinstance(value, basestring):
            raise TypeError('step_id must be a string or None')
        if value is not None:
            self.workflow_node.setAttribute('current_step_id', value)
        self._update_xnat()
        return

    @property
    def step_description(self):
        return self._attribute_or_none('step_description')

    @step_description.setter
    def step_description(self, value):
        if value is None:
            self._remove_workflow_node_attribute('step_description')
        elif not isinstance(value, basestring):
            raise TypeError('step_description must be a string or None')
        if value is not None:
            self.workflow_node.setAttribute('step_description', value)
        self._update_xnat()
        return

    @property
    def percent_complete(self):
        s_val = self.workflow_node.getAttribute('percentageComplete')
        if not s_val:
            return None
        return float(s_val)

    @percent_complete.setter
    def percent_complete(self, value):
        if value is None:
            self._remove_workflow_node_attribute('percentageComplete')
        elif not isinstance(value, (int, float)):
            raise TypeError('percent_complete must be an int or float or None')
        if value is not None:
            self.workflow_node.setAttribute('percentageComplete', str(value))
        self._update_xnat()
        return

    def update(self, step_id, step_description, percent_complete):
        if step_id is None:
            self._remove_workflow_node_attribute('current_step_id')
        elif not isinstance(step_id, basestring):
            raise TypeError('step_id must be a string or None')
        if step_description is None:
            self._remove_workflow_node_attribute('step_description')
        elif not isinstance(step_description, basestring):
            raise TypeError('step_description must be a string or None')
        if percent_complete is None:
            self._remove_workflow_node_attribute('percentageComplete')
        elif not isinstance(percent_complete, (int, float)):
            raise TypeError('percent_complete must be an int or float or None')
        if step_id is not None:
            self.workflow_node.setAttribute('current_step_id', step_id)
        if step_description is not None:
            self.workflow_node.setAttribute('step_description', step_description)
        if percent_complete is not None:
            self.workflow_node.setAttribute('percentageComplete', str(percent_complete))
        t = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        self.workflow_node.setAttribute('status', 'Running')
        self.workflow_node.setAttribute('current_step_launch_time', t)
        self._update_xnat()
        return

    def complete(self):
        t = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        self.workflow_node.setAttribute('status', 'Complete')
        self.workflow_node.setAttribute('current_step_launch_time', t)
        self.workflow_node.setAttribute('percentageComplete', '100.0')
        self._remove_workflow_node_attribute('current_step_id')
        self._remove_workflow_node_attribute('step_description')
        self._update_xnat()

    def fail(self, step_description=None):
        if step_description is None:
            self._remove_workflow_node_attribute('step_description')
        elif not isinstance(step_description, basestring):
            raise TypeError('step_description must be a string or None')
        if step_description is not None:
            self.workflow_node.setAttribute('step_description', step_description)
        self.workflow_node.setAttribute('status', 'Failed')
        self._update_xnat()
        return

# eof

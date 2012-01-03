import nose.tools
import pyxnat.core.resources
from .. import Connection

def set_r2_connection():
    r2.connection = ''

def set_r2_project():
    r2.project = ''

def set_r2_subject():
    r2.subject = ''

def set_r2_experiment():
    r2.experiment = ''

def set_r2_id():
    r2.id = ''

def set_r2_xml():
    r2.xml = ''

def set_r2_pyxnat_reoncstruction():
    r2.pyxnat_reoncstruction = ''

def set_r2_in_resources():
    r2.in_resources = ''

def set_r2_out_resources():
    r2.out_resources = ''

def setup():
    global connection, project, subject, experiment, reconstruction
    global r2
    connection = Connection('https://central.xnat.org', 
                            'nosetests', 
                            'nosetests')
    project = connection.projects['PALS']
    subject = project.subjects['Human_Buckner_Case01']
    experiment = subject.experiments['Human_Buckner_Case01']
    reconstruction = experiment.reconstructions['OAS1_0054_MR1_RECON1']
    raise NotImplementedError, 'r2 and remove r2'
    r2 = None

def test_attributes():
    assert reconstruction.connection is connection
    assert reconstruction.project is project
    assert reconstruction.subject is subject
    assert reconstruction.experiment is experiment
    assert reconstruction.id == 'OAS1_0054_MR1_RECON1'
    assert isinstance(reconstruction.pyxnat_reconstruction, pyxnat.core.resources.Reconstruction)
    assert isinstance(reconstruction.xml, str)
    assert reconstruction.xml.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<xnat:ReconstructedImage ID="OAS1_0054_MR1_RECON1"')
    assert reconstruction.xml.endswith('</xnat:ReconstructedImage>\n')

def test_read_only():
    nose.tools.assert_raises(AttributeError, set_r2_connection)
    nose.tools.assert_raises(AttributeError, set_r2_project)
    nose.tools.assert_raises(AttributeError, set_r2_subject)
    nose.tools.assert_raises(AttributeError, set_r2_experiment)
    nose.tools.assert_raises(AttributeError, set_r2_id)
    nose.tools.assert_raises(AttributeError, set_r2_xml)
    nose.tools.assert_raises(AttributeError, set_r2_pyxnat_reoncstruction)
    nose.tools.assert_raises(AttributeError, set_r2_in_resources)
    nose.tools.assert_raises(AttributeError, set_r2_out_resources)

def teardown():
    connection.close()

# eof

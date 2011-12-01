import pyxnat.core.resources
from .. import Connection

def setup():
    global connection, project, subject, experiment, reconstruction
    connection = Connection('https://central.xnat.org', 
                            'nosetests', 
                            'nosetests')
    project = connection.projects['PALS']
    subject = project.subjects['Human_Buckner_Case01']
    experiment = subject.experiments['Human_Buckner_Case01']
    reconstruction = experiment.reconstructions['OAS1_0054_MR1_RECON1']

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

def teardown():
    connection.close()

# eof

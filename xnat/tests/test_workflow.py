import datetime
from .. import Connection

def setup():
    global connection, project, subject, experiment, workflow
    connection = Connection('https://central.xnat.org', 'nosetests', 'nosetests')
    project = connection.projects['Calib']
    subject = project.subjects['73213384']
    experiment = subject.experiments['73213384_DUKE']
    workflow = experiment.workflows[475]

def test_attributes():
    assert workflow.id == 475
    assert workflow.connection is connection
    assert workflow.project is project
    assert workflow.subject is subject
    assert workflow.experiment is experiment
    assert workflow.status == 'Complete'
    assert workflow.step_launch_time == datetime.datetime(2009, 04, 30, 12, 27, 25)
    assert workflow.step_id is None
    assert workflow.pipeline_name == 'xnat_tools/AutoRun.xml'
    assert workflow.step_description is None
    assert workflow.launch_time == datetime.datetime(2009, 04, 30, 12, 27, 13)
    assert workflow.percent_complete == 100.0
    assert workflow.xml.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<wrk:Workflow')
    assert workflow.xml.endswith('</wrk:Workflow>\n')

def teardown():
    connection.close()

# eof

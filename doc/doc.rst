====
xnat
====

Abstraction module for XNAT access using Python.

This module provides access to XNAT instances using an object model based on XNAT's hierarchy of concepts.  It is designed to be conceptually simple and easy to use, but does so at the expense of efficiency and power.  Objects in this model provide access to the underlying pyxnat objects allowing for easy access to the more powerful features of pyxnat, but the module can be used without using pyxnat directly.

The XNAT hierarchy can be navigated with this module in a manner analogous to that used when navigating an XNAT web site.  So subjects, for instance, are accessed from project objects using the subjects' label within that project.  The resulting subject object will have properties of the subject as it appears in that project, even if the subject is shared into the project and belongs to another project.  Labels are used for addressing where possible, and IDs are secondary.  (Some objects, like scans and reconstructions, have no labels, so their ID must be used for addressing.)

Debugging can be turned on by setting the environment variable PYTHON_XNAT_DEBUG.  Setting this variable to "pyxnat" will also turn on debugging in the underlying pyxnat module.

Connection Objects
------------------

A connection object is the basic connection to an XNAT instance, and is the entry point to all operations.  Connections may be authenticated, requiring a user name and password, or unauthenticated, which is analogous to visiting an XNAT instance without logging in.

The XNAT URI and (for authenticated connections) user name and password may be passed to the connection constructor or may be specified though the environment variables XNAT_URI, XNAT_USER, and XNAT_PASSWORD, respectively.

This module does not provide an interactive mode for connections.

The NotConnectedError exception is raised if an operation is attempted on a closed connection.

class Connection(uri=uri, user=user, password=password)
class AnonymousConnection(uri=uri)

Authenticated connection.  The connecting credentials are checked immediately and xnat.pyxnat.core.errors.OperationalError is raised on error.

pyxnat_interface
    The pyxnat Interface object used for the connection.

close()
    Close the connection.  This closes the session with XNAT so the JSESSIONID cannot be used again.  NotConnectedError is raised if an operation is attempted after close() is called.

is_connected()
    Returns True if the connection is active, or False if it has been closed.

projects
    A dictionary of projects.  Keys are project IDs, and values are project objects.

find_subject(subject_id)
    Return a subject object given a subject ID.  Raises ValueError if the subject cannot be found.


Project Objects
---------------

Project objects should not be instantiated directly, but should be accessed through the projects attribute of a connection object.

id (read only)
    The project ID.

connection (read only)
    The connection object for this project.

pyxnat_project (read only)
    The pyxnat Project object for this project.

name (read only)
    The project name.

description (read only)
    The project description.

secondary_id (read only)
    The project secondary ID.

xml (read only)
    The XML for the project.

subjects (read only)
    A dictionary of subjects in the project.  Keys are the subject labels.

subjects_by_id (read only)
    A dictionary of subjects in the project.  Keys are the subject IDs.

resources (read only)
    A dictionary of project resources.  Keys are resource labels.

Subject Objects
---------------

Subjects objects should not be instantiated directly, but should be accessed using the subjects or subject_by_id attributes of project objects or using the find_subject() method of connection objects.

This module handles a subject as the member of a single project, so a shared subject can be represented by several different subject objects, one for each project.  (This is analogous to the way the web front-end for XNAT works: what is displayed on a subject page depends on the project of interest.)  The label and project attributes will vary depending on the project of interest, but the id, primary_project, and primary_label attributes are the same for subjects in different projects.

>>> primary_subject = connection.projects['CENTRAL_OASIS_CS'].subjects['OAS1_0054']
>>> shared_subject = connection.projects['PALS'].subjects['Human_Buckner_Case01']
>>> primary_subject.id
'OAS1_0054'
>>> shared_subject.id
'OAS1_0054'
>>> primary_subject.project
<Project CENTRAL_OASIS_CS>
>>> primary_subject.label
'OAS1_0054'
>>> shared_subject.project
<Project PALS>
>>> shared_subject.label
'Human_Buckner_Case01'
>>> primary_subject.primary_project
<Project CENTRAL_OASIS_CS>
>>> primary_subject.primary_label
'OAS1_0054'
>>> shared_subject.primary_project
<Project CENTRAL_OASIS_CS>
>>> shared_subject.primary_label
'OAS1_0054'
>>> primary_subject.projects
[<Project CENTRAL_OASIS_CS>, <Project PALS>]
>>> secondary_subject.projects
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'secondary_subject' is not defined
>>> shared_subject.projects
[<Project CENTRAL_OASIS_CS>, <Project PALS>]

connection
    The connection object for this subject.

id
    The subject ID.

project
    The project to which this subject belongs.

label
    The label for this subject in the parent project.

pyxnat_subject
    The pyxnat Subject object for this subject.

xml
    The XML for this subject.

primary_project
    The subject's primary project.

primary_label
    The subject's primary label (the label of the subject in its primary project).

projects
    The list of projects this subject is in.

experiments
    A dictionary of experiments for the subject.  Keys are experiment labels.

experiments_by_id
    A dictionary of experiments for the subject.  Keys are experiment IDs.

resources
    A dictionary of subject resources.  Keys are resource labels.

Experiment Objects
------------------

Experiment objects should not be instantiated directly, but should be accessed using the experiments or experiments_by_id attributes of subject objects.

Similar to subjects, this module handles experiments as members of subjects, so a shared experiment can be represented by several different experiment objects, one for each subject.  The label and subject attributes will vary depending on the subject of interest, but the id, primary_subject, and primary_label attributes are the same for experiments in different subjects.

connection
    The connection object for the experiment.

project
    The project object for the experiment.

id
    The experiment ID.

pyxnat_experiment
    The pyxnat Experiment object for this experiment.

xml
    The XNAT XML for the experiment.

subject
    The subject to which this experiment belongs.

label
    The label for this experiment in the parent subject.

primary_subject
    The experiment's primary subject.

primary_label
    The experiment's primary label (the label of the experiment in the primary subject).

scans
    A dictionary of scans in this experiment.  Keys are scan ID.

reconstructions
    A dictionary of reconstructions in this experiment.  Keys are reconstruction IDs.

assessments
    A dictionary of assessments in this experiment.  Keys are assessment labels.

resources
    A dictionary of resources in this experiment.  Keys are resource labels.

workflows
    A dictionary of workflows in this experiment.  Keys are workflow IDs.

Scan Objects
------------

Scan objects should not be instantiated directly, but should be accessed using the scan attribute of experiment objects.

connection
project
subject
experiment
id
pyxnat_scan
xml
resources

Reconstruction Objects
----------------------

Reconstruction objects should not be instantiated directly, but should be accessed using the reconstruction attribute of experiment objects.

connection
project
subject
experiment
id
pyxnat_reconstruction
xml
in_resources
out_resources

Assessment Objects
------------------

Assessment objects should not be instantiated directly, but should be accessed using the assessment attribute of experiment objects.

connection
project
subject
experiment
id
pyxnat_assessment
xml
in_resources
out_resources
label

Workflow Objects
----------------

Workflow objects should not be instantiated directly, but should be accessed using the workflows attribute of experiment objects.

id (integer)
connection
project
subject
experiment
status
step_launch_time datetime.datetime
step_id
pipeline_name
step_description
launch_time datetime.datetime
percent_complete (float)
xml
update(step_id, step_description, percent_complete)
complete()
fail([step_description])

Resource Objects
----------------

Resource objects should not be instantiated directly, but should be accessed using the resources attributes of project, subject, experiment, and scan objects and the in_resources and out_resources attributes of reconstruction and assessment objects.

connection
project
subject
experiment
assessment
reconstruction
scan
pyxnat_resource
id (integer)
label
files

File Objects
------------

File objects should not be instantiated directly but should be accessed through the files attributes of resource objects.

connection
resource
pyxnat_file
path
size
last_modified datetime.datetime
read()

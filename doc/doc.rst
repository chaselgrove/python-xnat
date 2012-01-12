====
xnat
====

Abstraction module for XNAT access using Python.

This module provides access to XNAT instances using an object model based on XNAT's hierarchy of concepts.  It is designed to be conceptually simple and easy to use, but does so at the expense of efficiency and power.  Objects in this model provide access to the underlying pyxnat objects allowing for easy access to the more powerful features of pyxnat, but the module can be used without using pyxnat directly.

The XNAT hierarchy can be navigated with this module in a manner analogous to that used when navigating an XNAT web site.  So subjects, for instance, are accessed from project objects using the subjects' label within that project.  The resulting subject object will have properties of the subject as it appears in that project, even if the subject is shared into the project and belongs to another project.  Labels are used for addressing where possible, and IDs are secondary.  (Some objects, like scans and reconstructions, have no labels, so their ID must be used for addressing.)

All dictionaries containing child entities (such as _Project.subjects or _Subject.experiments_by_id) are implemented by immutable, ordered dictionaries.  Items cannot be added to or removed from these dictionaries, and iteration results in the order returned by XNAT (so scans, for example, are returned as expected).

Debugging can be turned on by setting the environment variable PYTHON_XNAT_DEBUG.  Setting this variable to "pyxnat" will also turn on debugging in the underlying pyxnat module.

Exceptions
----------

XNATError
    Base class for XNAT exceptions.

NotConnectedError
    Not connected.

DoesNotExistError
    Entity does not exist.

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

find_experiment(experiment_id)
    Return an experiment given an experiment ID.  Raises ValueError if the experiment cannot be found.

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

create_subject(label)
    Create a subject with the given label.  If the subject exists, raises ValueError.  If the project has been deleted, raises DoesNotExistError.

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

connection (read only)
    The connection object for this subject.

id (read only)
    The subject ID.

project (read only)
    The project to which this subject belongs.

label (read only)
    The label for this subject in the parent project.

pyxnat_subject (read only)
    The pyxnat Subject object for this subject.

xml (read only)
    The XML for this subject.

primary_project (read only)
    The subject's primary project.

primary_label (read only)
    The subject's primary label (the label of the subject in its primary project).

projects (read only)
    The list of projects this subject is in.

experiments (read only)
    A dictionary of experiments for the subject.  Keys are experiment labels.

experiments_by_id (read only)
    A dictionary of experiments for the subject.  Keys are experiment IDs.

resources (read only)
    A dictionary of subject resources.  Keys are resource labels.

create_experiment(label[, type])
    Create an experiment with the given label.  If the experiment exists, raises ValueError.  If the subject has been deleted, raises DoesNotExistError.  type is an XNAT experiment type (such as xnat:mrSession); default determined by pyxnat.

Experiment Objects
------------------

Experiment objects should not be instantiated directly, but should be accessed using the experiments or experiments_by_id attributes of subject objects.

Similar to subjects, this module handles experiments as members of subjects, so a shared experiment can be represented by several different experiment objects, one for each subject.  The label and subject attributes will vary depending on the subject of interest, but the id, primary_subject, and primary_label attributes are the same for experiments in different subjects.

connection (read only)
    The connection object for the experiment.

project (read only)
    The project object for the experiment.

id (read only)
    The experiment ID.

pyxnat_experiment (read only)
    The pyxnat Experiment object for this experiment.

xml (read only)
    The XNAT XML for the experiment.

subject (read only)
    The subject to which this experiment belongs.

label (read only)
    The label for this experiment in the parent subject.

primary_subject (read only)
    The experiment's primary subject.

primary_label (read only)
    The experiment's primary label (the label of the experiment in the primary subject).

scans (read only)
    A dictionary of scans in this experiment.  Keys are scan ID.

reconstructions (read only)
    A dictionary of reconstructions in this experiment.  Keys are reconstruction IDs.

assessments (read only)
    A dictionary of assessments in this experiment.  Keys are assessment labels.

resources (read only)
    A dictionary of resources in this experiment.  Keys are resource labels.

workflows (read only)
    A dictionary of workflows in this experiment.  Keys are workflow IDs.

create_scan(id[, type])
    Create a scan with the given ID.  If the scan exists, raises ValueError.  If the experiment has been deleted, raises DoesNotExistError.  type is an XNAT scan type (such as xnat:mrScan); default is determined by pyxnat.

Scan Objects
------------

Scan objects should not be instantiated directly, but should be accessed using the scan attribute of experiment objects.

connection (read only)
    The connection object for the scan.

project (read only)
    The project object for the scan.

subject (read only)
    The subject object for the scan.

experiment (read only)
    The experiment object for the scan.

id (read only)
    The scan ID.

pyxnat_scan (read only)
    The pyxnat Scan object for the scan.

xml (read only)
    The XNAT XML for the scan.

resources (read only)
    A dictionary of resources for this scan.  Keys are resource labels.

create_resource(label)
    Create a resource with the given label.  If the resource exists, raises ValueError.  If the scan (or an ancestor) has been deleted, raises DoesNotExistError.

Reconstruction Objects
----------------------

Reconstruction objects should not be instantiated directly, but should be accessed using the reconstruction attribute of experiment objects.

connection (read only)
    The connection object for this reconstruction.

project (read only)
    The project object for this reconstruction.

subject (read only)
    The subject object for this reconstruction.

experiment (read only)
    The experiment object for this reconstruction.

id (read only)
    The reconstruction ID.

pyxnat_reconstruction (read only)
    The pyxnat Reconstruction object for this reconstruction.

xml (read only)
    The XNAT XML for this reconstruction.

in_resources (read only)
    A dictionary of input resources for this reconstruction.  Keys are resource labels.

out_resources (read only)
    A dictionary of output resources for this reconstruction.  Keys are resource labels.

Assessment Objects
------------------

Assessment objects should not be instantiated directly, but should be accessed using the assessment attribute of experiment objects.

connection (read only)
    The connection object for this assessment.

project (read only)
    The project object for this assessment.

subject (read only)
    The subject object for this assessment.

experiment (read only)
    The experiment object for this assessment.

id (read only)
    The assessment ID.

label (read only)
    The assessment label.

pyxnat_assessment (read only)
    The pyxnat Assessor object for this assessment.

xml (read only)
    The XNAT XML for this assessment.

in_resources (read only)
    A dictionary of input resources for this assessment.  Keys are resource labels.

out_resources (read only)
    A dictionary of output resources for this assessment.  Keys are resource labels.

Workflow Objects
----------------

Workflow objects should not be instantiated directly, but should be accessed using the workflows attribute of experiment objects.

id
    The (integer) ID for the workflow.

connection
    The connection object for this workflow.

project
    The project object for this workflow.

subject
    The subject object for this workflow.

experiment
    The experiment object for this workflow.

status
The workflow status (Queued, Running, etc)

step_launch_time
    The (datetime.datetime) time that the current step started.

step_id
    The workflow step ID.

pipeline_name
    The pipeline name.

step_description
    The step description.

launch_time
    The (datetime.datetime) time that the pipeline started.

percent_complete
    The (float) percent complete.

xml
    The XNAT XML for the pipeline.

update(step_id, step_description, percent_complete)
    Update the workflow.  step_id and step_description must be strings, and percent_complete must be a float.  Status is set to Running and current_step_launch_time is updated.

complete()
    Mark the workflow successfully completed.  status is set to Complete, current_step_launch_time is updated, percent_complete is set to 100.0, and current_step_id and step_description are set to None (removed from the XNAT XML).

fail([step_description])
    Mark the workflow failed.  status is set to Failed.  If step_description is not given, step_description is set to None (removed from the XNAT XML).

Resource Objects
----------------

Resource objects should not be instantiated directly, but should be accessed using the resources attributes of project, subject, experiment, and scan objects and the in_resources and out_resources attributes of reconstruction and assessment objects.

connection
    The connection object for the resource.

project
    The project object for the resource.

subject
    The subject object for the resource (if applicable).

experiment
    The experiment object for the resource (if applicable).

assessment
    The assessment object for the resource (if applicable).

reconstruction
    The reconstruction object for the resource (if applicable).

scan
    The scan object for the resource (if applicable).

pyxnat_resource
    The pyxnat Resource object for the resource.

id
    The (integer) ID of the resource.

label
    The label of the resource.

files
    A list of File objects in the resource.

create_file(data, remote_path)
    Create a file in the resource from the passed data.  remote_path is the path of the file relative to the resource.  If the resource has been deleted, raises DoesNotExistError.  If the remote file exists, raises ValueError.

put_file(local_path, remote_path)
    Upload a local file to the resource.  r.put_file(local_path, remote_path) is equivalent to r.create_file(open(local_path).read(), remote_path).

File Objects
------------

File objects should not be instantiated directly but should be accessed through the files attributes of resource objects.

connection
    The connection object for this file.

resource
    The resource object for this file.

pyxnat_file
    The pyxnat File object for the file.

path
    The path of the file relative to the resource.

size
    The size in bytes of the file.  Raises DoesNotExistError if the file has already been deleted.

last_modified
    The (datetime.datetime) time of last modification.  Raises DoesNotExistError if the file has already been deleted.

read()
    Return the contents of the file.  Raises DoesNotExistError if the file has already been deleted.

get(local_path)
    Download the file.  f.get(local_path) is equivalent to open(local_path, 'w').write(f.read()).  Raises DoesNotExistError if the file has already been deleted.

delete()
    Removes the file from the server.  Raises DoesNotExistError if the file has already been deleted.

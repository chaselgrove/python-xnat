====
xnat
====

Abstraction module for XNAT access using Python.

This module provides access to XNAT instances using an object model based on XNAT's heirarchy of concepts.  It is designed to be conceptually simple and easy to use, but does so at the expense of efficiency and power.  Objects in this model provide access to the underlying pyxnat objects allowing for easy access to the more powerful features of pyxnat, but the module can be used without using pyxnat directly.

Debugging can be turned on by setting the environment variable PYTHON_XNAT_DEBUG.  Setting this variable to "pyxnat" will also turn on debugging in the underlying pyxnat module.

Connection Objects
------------------

A connection object is the basic connection to an XNAT instance, and is the entry point to all operations.  Connections may be authenticated, requiring a user name and password, or unauthenticated, which is analagous to visiting an XNAT instance without logging in.

The XNAT URI and (for authenticated connections) user name and password may be passed to the connection constructor or may be specified though the environment varialbles XNAT_URI, XNAT_USER, and XNAT_PASSWORD, respectively.

This module does not provide an interactive mode for connections.

The NotConnectedError exception is raised if an operation is attempted on a closed connection.

class Connection(uri=uri, user=user, password=password)
class AnonymousConnection(uri=uri)

Authenticated connection.  The connecting credentials are checked immediately.  (TODO: what's the exception?) // AnonymousConnection
pyxnat.core.errors.OperationalError: Authentication failed


pyxnat_interface
    The pyxnat Interface object used for the connection.

close()
    Close the connection.  This closes the session with XNAT so the JSESSIONID cannot be used again.  NotConnectedError is raised if an operation is attempted after close() is called.

is_connected()
    Returns True if the connection is active, or False if it has been closed.

projects
    A dictionary of projects.  Keys are project IDs, and values are project objects.


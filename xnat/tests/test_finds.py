import nose.tools
import pyxnat.core.resources
from .. import Connection, _Subject, _Experiment

def setup():
    global c
    c = Connection('https://central.xnat.org', 'nosetests', 'nosetests')

def test_find_subject():
    nose.tools.assert_raises(ValueError, lambda: c.find_subject('xxxxxxxx'))
    # Human_Buckner_Case01 is a label, not an ID
    nose.tools.assert_raises(ValueError, lambda: c.find_subject('Human_Buckner_Case01'))
    s = c.find_subject('OAS1_0054')
    assert isinstance(s, _Subject)
    assert s.id == 'OAS1_0054'
    assert s.project == c.projects['CENTRAL_OASIS_CS']

"""
def test_find_experiment():
    nose.tools.assert_raises(ValueError, lambda: c.find_experiment('xxxxxxxx'))
    # Human_Buckner_Case01 is a label, not an ID
    nose.tools.assert_raises(ValueError, lambda: c.find_experiment('Human_Buckner_Case01'))
    e = c.find_experiment('OAS1_0054_MR1')
    assert isinstance(_Experiment, e)
    assert e.id == 'OAS1_0054_MR1'
    assert e.project == c.projects['CENTRAL_OASIS_CS']
"""

def teardown():
    c.close()

# eof

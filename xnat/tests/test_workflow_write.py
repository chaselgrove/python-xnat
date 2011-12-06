import datetime
import nose.tools
from .. import Connection

def set_bad_status():
    w1.status = 1

def set_status_none():
    w1.status = None

def set_bad_step_id():
    w1.step_id = 1

def set_bad_step_description():
    w1.step_description = 1

def set_bad_percent_complete():
    w1.percent_complete = 'a'

def set_bad_step_launch_time():
    w1.step_launch_time = 'a'

def setup():
    global c1, c2, w1, w2
    c1 = Connection('https://central.xnat.org', 'nosetests', 'nosetests')
    c2 = Connection('https://central.xnat.org', 'nosetests', 'nosetests')
    w1 = c1.projects['nosetests'].subjects['workflow_test'].experiments['workflow_test_MR'].workflows[4586]
    w2 = c2.projects['nosetests'].subjects['workflow_test'].experiments['workflow_test_MR'].workflows[4586]

def test_status():
    w1.status = 'Running'
    assert w1.status == 'Running'
    w2._reset()
    assert w2.status == 'Running'
    w1.status = 'Queued'
    assert w1.status == 'Queued'
    w2._reset()
    assert w2.status == 'Queued'
    nose.tools.assert_raises(TypeError, set_bad_status)
    nose.tools.assert_raises(TypeError, set_status_none)

def test_step_id():
    w1.step_id = 's1'
    assert w1.step_id == 's1'
    w2._reset()
    assert w2.step_id == 's1'
    w1.step_id = 's2'
    assert w1.step_id == 's2'
    w2._reset()
    assert w2.step_id == 's2'
    w1.step_id = None
    assert w1.step_id is None
    w2._reset()
    assert w2.step_id is None
    nose.tools.assert_raises(TypeError, set_bad_step_id)

def test_step_description():
    w1.step_description = 'd1'
    assert w1.step_description == 'd1'
    w2._reset()
    assert w2.step_description == 'd1'
    w1.step_description = 'd2'
    assert w1.step_description == 'd2'
    w2._reset()
    assert w2.step_description == 'd2'
    w1.step_description = None
    assert w1.step_description is None
    w2._reset()
    assert w2.step_description is None
    nose.tools.assert_raises(TypeError, set_bad_step_description)

def test_percent_complete():
    w1.percent_complete = 0
    assert w1.percent_complete == 0.0
    w2._reset()
    assert w2.percent_complete == 0.0
    w1.percent_complete = 100.0
    assert w1.percent_complete == 100.0
    w2._reset()
    assert w2.percent_complete == 100.0
    w1.percent_complete = None
    assert w1.percent_complete is None
    w2._reset()
    assert w2.percent_complete is None
    nose.tools.assert_raises(TypeError, set_bad_percent_complete)

def test_step_launch_time():
    t1 = datetime.datetime(2009, 04, 30, 12, 27, 25)
    t2 = datetime.datetime(2010, 05, 01, 13, 10, 00)
    w1.step_launch_time = t1
    assert w1.step_launch_time == t1
    w2._reset()
    assert w2.step_launch_time == t1
    w1.step_launch_time = t2
    assert w1.step_launch_time == t2
    w2._reset()
    assert w2.step_launch_time == t2
    w1.step_launch_time = None
    assert w1.step_launch_time is None
    w2._reset()
    assert w2.step_launch_time is None
    nose.tools.assert_raises(TypeError, set_bad_step_launch_time)

def teardown():
    c1.close()
    c2.close()

# eof

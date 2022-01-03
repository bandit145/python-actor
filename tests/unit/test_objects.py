from actor.system.objects import *
import uuid

def test_pid():
	uu = uuid.uuid4()
	pid = Pid(int=uu.int)
	assert str(uu) == str(pid)
	assert pid.__repr__() == f"Pid('{pid}')"
from actor.actors import Supervisor
import actor.utils
import time

actor.utils.load_env(None, 'DEBUG')

def test_supervisor_start_stop():
	pid = spawn('actor.actors.Supervisor', 'debug')
	std_msg(data=dict(spawn='actor.actors.EchoActor', desired=3, log_level='debug')) > pid
	sup_state = info_msg(dump_state=True) >> pid
	assert len(sup_state['state']['processes']['actor.actors.EchoActor']['pids']) == 3
	print(sup_state)
	for p in sup_state['state']['processes']['actor.actors.EchoActor']['pids']:
		msg = info_msg(data={}) >> p
		assert msg['r_pid'] == p
	kill_msg() > pid

def test_supervisor_scale():
	pid = spawn('actor.actors.Supervisor', 'debug')
	std_msg(data=dict(spawn='actor.actors.EchoActor', desired=1, log_level='debug')) > pid
	sup_state = info_msg(dump_state=True) >> pid
	assert len(sup_state['state']['processes']['actor.actors.EchoActor']['pids']) == 1
	std_msg(data=dict(spawn='actor.actors.EchoActor', desired=3)) > pid
	sup_state = info_msg(dump_state=True) >> pid
	assert len(sup_state['state']['processes']['actor.actors.EchoActor']['pids']) == 3
	for p in sup_state['state']['processes']['actor.actors.EchoActor']['pids']:
		msg = info_msg(data={}) >> p
		assert msg['r_pid'] == p
		link_msg() >> p
	pids = sup_state['state']['processes']['actor.actors.EchoActor']['pids'].copy()
	std_msg(data=dict(spawn='actor.actors.EchoActor', desired=1)) > pid
	while len(pids) != 1:
		msg = MAILBOX.get()
		if msg['msg_type'] == "death_msg":
			assert msg['r_pid'] in pids
			pids = [x for x in pids if msg['r_pid'] != x]
			PROC_LOGGER.debug(f'pid list state {pids}')
	kill_msg() > pid

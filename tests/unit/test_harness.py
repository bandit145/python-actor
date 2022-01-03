from actor.harness import Harness
import actor.utils
import json
import pathlib

actor.utils.load_env()

def test_launch_harness():
	tst_msg = {'r_pid': str(PID), 'msg_type': actor.utils.INFO_MSG, 'sync': False, 'data': None}
	pid = actor.utils.spawn('actor.actors.EchoActor')
	path = pathlib.Path(f'{FIFO_DIR}/{pid}')
	while not path.exists:
		pass
	with FIFO.open(mode='r') as r_pipe:
		with path.open(mode='w') as s_pipe:
			json.dump(tst_msg, s_pipe)
			json.dump(tst_msg, s_pipe)
			json.dump({'r_pid': str(PID), 'msg_type': actor.utils.KILL_MSG}, s_pipe)
	data = json.load(r_pipe)
	print(data)
	#assert harn.actor.state['count'] == 3


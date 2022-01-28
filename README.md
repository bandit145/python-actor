# python-actor
Python actor system, heavily inspired by Erlang/OTP

This is a framework that implements the actor model for python and attempts to make it feel like it is part of the language. It currently supports spawning off processes sending messages between processes and linking processes.


###Features:

- Linking
- Message passing (sync/async)
- Actors

###Future features:

- Remote linking/spawning/msg spawning support
- Spawning support with just raw functions/lambdas
- Application specific isolation (fs namespaces probably).



## Usage

Lets take a look at a basic example

```python
#this loads the actor system; starting a FIFO pipe on the system and an event loop for accepting messages in a separate thread for this process,
>>> import actor.load
# This send a standard message type async (does not wait for a response) to the specified process ID. In this case it is our processes own pid "PID"
>>> std_msg(data=dict(hi="hey")) > PID
# pull the first item from the mailbox if it is not empty
>>> pop_mailbox()
#All message type contain the keys msg_type, ref, and r_pid. ref is for keeping track of messages for when you send a message synchronously (we will get to that in a second), and r_pid (response pid) is the pid of the process that has sent you the message.
{'data': {'hi': 'hey'}, 'msg_type': 'std_msg', 'ref': None, 'r_pid': Pid('67049a11-81f8-4c8c-8010-1f8380eb5754')}
# we are going to spawn an EchoActor (This is an actor that echos all standard and info messages sent to it)
>>> n_pid = spawn("actor.actors.EchoActor")
>>> n_pid
Pid('feeef5d3-6aaa-4b4f-9494-1ba324907054')
# send a std_msg to our EchoActor process
>>> std_msg(data=dict(hi="hey")) > n_pid
>>> pop_mailbox()
#we have received a message back with the same data but from our EchoActor process. Note it's r_pid is the same as n_pid from when we spawned the process.
{'data': {'hi': 'hey'}, 'msg_type': 'std_msg', 'ref': None, 'r_pid': Pid('feeef5d3-6aaa-4b4f-9494-1ba324907054')}
#Lets send the same message but synchronously. This will generate a Ref when it sends the message and block until it receives a message in the mailbox with the same Ref. You can see ref now contains a ref object in the response from other process.
>>> std_msg(data=dict(hi="hey")) >> n_pid
{'data': {'hi': 'hey'}, 'ref': Ref('a166ec94-b763-4a69-b125-4229326b64bd'), 'msg_type': 'std_msg', 'r_pid': Pid('feeef5d3-6aaa-4b4f-9494-1ba324907054')}

```

## Implementing an Actor
All actors should be subclassed from actor.actors.Actor. Let's look at how the EchoActor is implemented:

```python
class EchoActor(Actor):
    state = {"msg_cnt": 0}
    # start is run before any message processing occurs
    def start(self):
        print("test")
    # this is run whenever a standard message is received
    def std(self, pid, ref, msg):
        self.state["msg_cnt"] += 1
        if ref:
            std_msg(data=msg["data"], ref=ref) > pid
        else:
            std_msg(data=msg["data"]) > pid
    #run whenever an info_msg is recieved
    def info(self, pid, ref, msg):
        self.state["msg_cnt"] += 1
        if ref:
            info_msg(data=msg["data"], ref=ref) > pid
        else:
            info_msg(data=msg["data"]) > pid
```
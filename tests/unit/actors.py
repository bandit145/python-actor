from actor.actors import Actor


class EchoActor(Actor):
    state = {"msg_cnt": 0}

    def start(self):
        print("test")

    def info(self, pid, ref, msg):
        self.state["msg_cnt"] += 1
        if ref:
            info_msg(data=msg["data"], ref=ref) > pid

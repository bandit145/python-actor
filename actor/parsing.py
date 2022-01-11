import actor.system.objects
import uuid
import json


def decode_object_hook(json):
    return {k: check_for_objs(k, v) for (k, v) in json.items()}


def check_for_objs(key, value):
    if value:
        match key:
            case "pids":
                if isinstance(value, list):
                    return [actor.system.objects.Pid(x) for x in value if x]
                else:
                    return value
            case "r_pid":
                return actor.system.objects.Pid(value)
            case "pid":
                return actor.system.objects.Pid(value)
            case "ref":
                return actor.system.objects.Ref(value)
            case _:
                return value
    return value


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, uuid.UUID):
            return str(o)
        else:
            return json.JSONEncoder.default(self, o)

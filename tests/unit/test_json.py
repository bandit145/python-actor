from actor.parsing import decode_object_hook, JSONEncoder
import actor.system.objects
import uuid
import json


def test_custom_decode_hook():
    test_json = {
        "msg_type": "info_msg",
        "ref": str(uuid.uuid4()),
        "r_pid": str(uuid.uuid4()),
        "data": {
            "pid": str(uuid.uuid4()),
            "garbo": [1, 2, str(uuid.uuid4()), {"pids": [str(uuid.uuid4())]}],
        },
    }
    test_json = json.dumps(test_json)
    data = json.loads(test_json, object_hook=decode_object_hook)
    print(data)
    assert type(data["ref"]) == actor.system.objects.Ref
    assert type(data["r_pid"]) == actor.system.objects.Pid
    assert type(data["data"]["pid"]) == actor.system.objects.Pid
    assert type(data["data"]["garbo"][2]) == str
    assert type(data["data"]["garbo"][3]["pids"][0]) == actor.system.objects.Pid


def test_custom_json_encoder():
    test_json = {
        "msg_type": "info_msg",
        "ref": str(uuid.uuid4()),
        "r_pid": str(uuid.uuid4()),
        "data": {
            "pid": str(uuid.uuid4()),
            "garbo": [1, 2, str(uuid.uuid4()), {"pids": [str(uuid.uuid4())]}],
        },
    }
    data = json.dumps(test_json, cls=JSONEncoder)
    print(data)
    decode = json.loads(data, object_hook=decode_object_hook)
    assert type(decode["ref"]) == actor.system.objects.Ref
    assert type(decode["r_pid"]) == actor.system.objects.Pid
    assert type(decode["data"]["pid"]) == actor.system.objects.Pid
    assert type(decode["data"]["garbo"][2]) == str
    assert type(decode["data"]["garbo"][3]["pids"][0]) == actor.system.objects.Pid

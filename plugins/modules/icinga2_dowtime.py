#!/usr/bin/python

from __future__ import annotations

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

HAS_ICINGA2API = True
try:
    from icinga2apic.client import Client as Icinga2Client
    from icinga2apic.exceptions import Icinga2ApiException
except ImportError:
    ICINGA2API_IMP_ERR = traceback.format_exc()
    HAS_ICINGA2API = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_url=dict(required=True),
            api_user=dict(required=True, no_log=False),
            api_password=dict(required=True, no_log=True),
            api_timeout=dict(required=False, default=None),
            api_version=dict(default="1", choices=["1"]),
            all_services=dict(required=False, default=False, type="bool"),
            author=dict(required=False, default="Ansible"),
            comment=dict(required=False, default="Downtime scheduled by Ansible"),
            duration=dict(required=False, default=None, type="int"),
            end_time=dict(required=False, default=None),
            filter_vars=dict(required=False, default=None),
            filters=dict(required=False, default=None),
            fixed=dict(required=False, default=False, type="bool"),
            name=dict(required=False, default=None),
            object_type=dict(default="Host", choices=["Service", "Host", "Downtime"]),
            start_time=dict(required=False, default=None),
            state=dict(type="str", default="present", choices=["present", "absent"]),
            trigger_name=dict(required=False, default=None),
        ),
        supports_check_mode=False,
        required_if=(
            ("state", "present", ["start_time", "end_time", "filters"]),
            ("fixed", True, ["duration"]),
        ),
        required_one_of=[["filters", "name"]],
    )

    if not HAS_ICINGA2API:
        module.fail_json(
            msg=missing_required_lib("icinga2apic"), exception=ICINGA2API_IMP_ERR
        )

    config = {
        "url": module.params["api_url"],
        "username": module.params["api_user"],
        "password": module.params["api_password"],
    }
    if module.params["api_timeout"]:
        config["timeout"] = module.params["api_timeout"]

    client = Icinga2Client(**config)

    result = {}
    try:
        if module.params["state"] == "present":
            payload = schedule_downtime(module, client)
            result["changed"] = True
            result["results"] = payload["results"]
        elif module.params["state"] == "absent":
            payload = remove_downtime(module, client)
            result["changed"] = True
            result["results"] = payload["results"]
    except Icinga2ApiException as e:
        module.fail_json(msg=f"{e}", exception=traceback.format_exc())

    module.exit_json(**result)


def schedule_downtime(module, client):
    args = {
        "object_type": module.params["object_type"],
        "filters": module.params["filters"],
        "author": module.params["author"],
        "comment": module.params["comment"],
        "start_time": module.params["start_time"],
        "end_time": module.params["end_time"],
        "duration": module.params["duration"],
    }
    if module.params["all_services"]:
        args["all_services"] = module.params["all_services"]
    if module.params["filter_vars"]:
        args["filter_vars"] = module.params["filter_vars"]
    if module.params["fixed"]:
        args["fixed"] = module.params["fixed"]
    if module.params["trigger_name"]:
        args["trigger_name"] = module.params["trigger_name"]

    return client.actions.schedule_downtime(**args)


def remove_downtime(module, client):
    args = {
        "object_type": module.params["object_type"],
    }
    if module.params["name"]:
        args["name"] = module.params["name"]
    if module.params["filters"]:
        args["filters"] = module.params["filters"]
    if module.params["filter_vars"]:
        args["filter_vars"] = module.params["filter_vars"]

    return client.actions.remove_downtime(**args)


if __name__ == "__main__":
    main()

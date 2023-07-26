import json
import subprocess
import os
import threading
from threading import Lock
# internal test


def nginx_main_parser(nginx_config):
    nginx_config_info = {}
    level = 1
    max_level = 8
    key1, key2, key3, key4, key5, key6, key7, key8 = None, None, None, None, None, None, None, None
    find_location = False
    location_info = {}
    location_name = ""
    value = ""

    for i in range(len(nginx_config)):
        if not nginx_config[i].startswith("#"):
            if nginx_config[i] == "{":
                if find_location:
                    location_name = key3
                    if location_name not in location_info:
                        location_info[location_name] = {}

                level += 1
                if level > max_level:
                    print("level is too deep...")
                # Init level dict
                if level == 2:
                    nginx_config_info[key1] = {}
                elif level == 3:
                    nginx_config_info[key1][key2] = {}
                elif level == 4:
                    nginx_config_info[key1][key2][key3] = {}
                elif level == 5:
                    nginx_config_info[key1][key2][key3][key4] = {}
                elif level == 6:
                    nginx_config_info[key1][key2][key3][key4][key5] = {}
                elif level == 7:
                    nginx_config_info[key1][key2][key3][key4][key5][key6] = {}
                elif level == 8:
                    nginx_config_info[key1][key2][key3][key4][key5][key6][key7] = {}
            # level 1 process
            elif level == 1:
                if not key1:
                    key1 = nginx_config[i]
                elif nginx_config[i] == ";":
                    nginx_config_info[key1], key1, value = value, None, ""
                else:
                    value = nginx_config[i] if value == "" else value + " " + nginx_config[i]

            # level 2 process
            elif level == 2:
                if nginx_config[i] == "}":
                    level, key1, key2 = level - 1, None, None

                elif not key2:
                    key2 = nginx_config[i]
                elif nginx_config[i] == ";":
                    nginx_config_info[key1][key2], key2, value = value, None, ""
                else:
                    value = nginx_config[i] if value == "" else value + " " + nginx_config[i]

            # level 3 process
            elif level == 3:
                if find_location and "locations" not in nginx_config_info[key1][key2]:
                    nginx_config_info[key1][key2]["locations"] = []
                if nginx_config[i] == "}":
                    level, key2, key3 = level - 1, None, None
                elif not key3:
                    key3 = nginx_config[i]
                    if key3 == "location":
                        find_location = True
                elif nginx_config[i] == ";":
                    nginx_config_info[key1][key2][key3], key3, value = value, None, ""
                else:
                    value = nginx_config[i] if value == "" else value + " " + nginx_config[i]

            # level 4 process
            elif level == 4:
                if nginx_config[i] == "}":
                    if find_location:
                        nginx_config_info[key1][key2]["locations"].append(location_info)
                        find_location = False
                        location_name = ""
                    level, key3, key4 = level - 1, None, None

                elif not key4:
                    key4 = nginx_config[i]
                elif nginx_config[i] == ";":
                    if find_location:
                        location_info[location_name][key4] = value
                    else:
                        nginx_config_info[key1][key2][key3][key4] = value
                    value, key4 = "", None
                else:
                    value = nginx_config[i] if value == "" else value + " " + nginx_config[i]

            # level 5 process
            elif level == 5:
                if nginx_config[i] == "}":
                    level, key4, key5 = level - 1, None, None
                elif not key5:
                    key5 = nginx_config[i]
                elif nginx_config[i] == ";":
                    nginx_config_info[key1][key2][key3][key4][key5], key5, value = value, None, ""
                else:
                    value = nginx_config[i] if value == "" else value + " " + nginx_config[i]

            # level 6 process
            elif level == 6:
                if nginx_config[i] == "}":
                    level, key5, key6 = level - 1, None, None
                elif not key6:
                    key6 = nginx_config[i]
                elif nginx_config[i] == ";":
                    nginx_config_info[key1][key2][key3][key4][key5][key6], key6, value = value, None, ""
                else:
                    value = nginx_config[i] if value == "" else value + " " + nginx_config[i]

    return nginx_config_info


def nginx_server_parser(nginx_server_config):
    server_info_list = []
    server_info = {}
    level = 1
    max_level = 7
    key1 = key2 = key3 = key4 = key5 = key6 = None
    value = ""
    find_server = False
    find_location = False
    location_name = ""
    location_info = {}
    location_level = -1
    stack = []
    server_info["locations"] = []
    for i in range(len(nginx_server_config)):
        if not nginx_server_config[i].startswith("#"):
            if nginx_server_config[i] == "{" and find_server:
                if find_location:
                    if level == location_level:
                        location_name = value
                        value = ""
                level += 1
                if level > max_level:
                    print("level is too deep...")
                # Init level dict
                if level == 2:
                    server_info[key1] = {}
                elif level == 3:
                    server_info[key1][key2] = {}
                elif level == 4:
                    server_info[key1][key2][key3] = {}
                elif level == 5:
                    server_info[key1][key2][key3][key4] = {}
                elif level == 6:
                    server_info[key1][key2][key3][key4][key5] = {}
                elif level == 7:
                    server_info[key1][key2][key3][key4][key5][key6] = {}
            # ignore other blocks
            elif nginx_server_config[i] == "{" and not find_server:
                stack.append("{")
                level += 1
            elif nginx_server_config[i] == "}" and not find_server:
                stack.pop()
                level -= 1
                if len(stack) == 0:
                    key1 = None
            # level 1 process
            elif level == 1:
                if not key1:
                    key1 = nginx_server_config[i]
                    if key1 == "server":
                        find_server = True
                elif nginx_server_config[i] == ";":
                    server_info[key1], key1, value = value, None, ""
                else:
                    value = nginx_server_config[i] if value == "" else value + " " + nginx_server_config[i]

            # level 2 process
            elif level == 2 and find_server:
                if nginx_server_config[i] == "}":
                    level, key1, key2 = level - 1, None, None
                    find_server = False
                    server_info_list.append(server_info)
                    server_info = {'locations': []}

                elif not key2:
                    key2 = nginx_server_config[i]
                    if key2 == "location":
                        find_location = True
                        location_level = level

                elif nginx_server_config[i] == ";":
                    server_info[key1][key2], key2, value = value, None, ""
                else:
                    value = nginx_server_config[i] if value == "" else value + " " + nginx_server_config[i]

            # level 3 process
            elif level == 3:
                if nginx_server_config[i] == "}":
                    level, key2, key3 = level - 1, None, None
                    if find_location and level <= location_level:
                        find_location = False
                        server_info["locations"].append({location_name: location_info})
                        location_name = ""
                        location_info = {}
                elif not key3:
                    key3 = nginx_server_config[i]
                elif nginx_server_config[i] == ";":
                    if find_location:
                        if key3 in location_info:
                            if type(location_info[key3]) is list:
                                location_info[key3].append(value)
                            else:
                                previous_value = location_info[key3]
                                location_info[key3] = [previous_value, value]
                        else:
                            location_info[key3] = value

                    else:
                        server_info[key1][key2][key3] = value
                    value, key3 = "", None
                else:
                    value = nginx_server_config[i] if value == "" else value + " " + nginx_server_config[i]

            # level 4 process
            elif level == 4:
                if nginx_server_config[i] == "}":
                    level, key3, key4 = level - 1, None, None
                elif not key4:
                    key4 = nginx_server_config[i]
                elif nginx_server_config[i] == ";":
                    server_info[key1][key2][key3][key4], value = value, ""
                else:
                    value = nginx_server_config[i] if value == "" else value + " " + nginx_server_config[i]

            # level 5 process
            elif level == 5:
                if nginx_server_config[i] == "}":
                    level, key4, key5 = level - 1, None, None
                elif not key5:
                    key5 = nginx_server_config[i]
                elif nginx_server_config[i] == ";":
                    server_info[key1][key2][key3][key4][key5], value = value, ""
                else:
                    value = nginx_server_config[i] if value == "" else value + " " + nginx_server_config[i]

            # level 6 process
            elif level == 6:
                if nginx_server_config[i] == "}":
                    level, key5, key6 = level - 1, None, None
                elif not key6:
                    key6 = nginx_server_config[i]
                elif nginx_server_config[i] == ";":
                    server_info[key1][key2][key3][key4][key5][key6], value = value, ""
                else:
                    value = nginx_server_config[i] if value == "" else value + " " + nginx_server_config[i]

    return server_info_list


def nginx_upstream_parser(nginx_upstream_config):
    level = 1
    max_level = 2
    key1 = key2 = None
    value = ""
    upstream_dict = {}
    find_upstream = False
    find_server = False
    upstream_name = None
    stack = []

    for i in range(len(nginx_upstream_config)):
        if not nginx_upstream_config[i].startswith("#"):
            if nginx_upstream_config[i] == "{" and find_upstream:
                if level == 1:
                    upstream_name = value
                    upstream_dict[upstream_name] = {}
                    upstream_dict[upstream_name]["servers"] = []
                    value = ""
                level += 1
                if level > max_level:
                    print("level is too deep...")
            elif nginx_upstream_config[i] == "{" and not find_upstream:
                stack.append("{")
            elif nginx_upstream_config[i] == "}" and not find_upstream:
                stack.pop()
                if len(stack) == 0:
                    key1 = None
            # level 1 process
            elif level == 1:
                if not key1:
                    key1 = nginx_upstream_config[i]
                    if key1 == "upstream": find_upstream = True
                elif find_upstream:
                    value = nginx_upstream_config[i] if value == "" else value + " " + nginx_upstream_config[i]

            # level 2 process
            elif level == 2 and find_upstream:
                if nginx_upstream_config[i] == "}":
                    level -= 1
                    key1, key2, find_upstream, upstream_name = None, None, False, None
                elif not key2:
                    key2 = nginx_upstream_config[i]
                    if key2 == "server":
                        find_server = True
                elif nginx_upstream_config[i] == ";":
                    if find_server:
                        upstream_dict[upstream_name]["servers"].append({"server": value})
                        find_server = False
                    else:
                        upstream_dict[upstream_name][key2] = value
                    key2, value = None, ""
                else:
                    value = nginx_upstream_config[i] if value == "" else value + " " + nginx_upstream_config[i]

    return upstream_dict


def nginx_server_info_parser(file, upstreams, server_infos_queue, lock):
    res = subprocess.run("crossplane lex '%s'" % file, shell=True, capture_output=True)
    nginx_server = json.loads(res.stdout.decode(encoding="utf8").strip())
    upstream_info = nginx_upstream_parser(nginx_server)
    lock.acquire()
    for upstream in upstream_info:

        upstreams[upstream] = list()
        for server in upstream_info[upstream]['servers']:
            for k in server:
                upstreams[upstream].append(server[k])

    server_infos_queue.append(nginx_server_parser(nginx_server))
    lock.release()


def parser():
    if os.getenv("LOCAL_DEBUG") == "True":
        nginx_conf_path = "/Users/wanyongzhen/kuaishou/gitlab/ee-gateway-nginx-test/conf.d/*.conf"
    else:
        nginx_conf_path = "./conf.d/*.conf"
    run_cmd = "ls " + nginx_conf_path
    files = subprocess.run(run_cmd, shell=True,
                           capture_output=True)
    files = files.stdout.decode(encoding="utf8").split("\n")
    servers_on_nginx = {}
    upstreams = {}
    is_fatal = False

    server_infos_queue = []
    lock = Lock()
    threads = []
    for file in files[:-1]:
        t = threading.Thread(target=nginx_server_info_parser, args=(file, upstreams, server_infos_queue, lock))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    for server_infos in server_infos_queue:
        for server_info in server_infos:
            for domain in server_info['server']['server_name'].split():
                servers_on_nginx[domain] = []
            for location in server_info['locations']:
                for path in location:
                    if "proxy_pass" in location[path]:
                        for domain in server_info['server']['server_name'].split():
                            proxy_pass = location[path]['proxy_pass']
                            if proxy_pass.startswith("http://"):
                                proxy_pass = proxy_pass[7:]
                            if proxy_pass.startswith("https://"):
                                proxy_pass = proxy_pass[8:]
                            if "$cloud" in proxy_pass:
                                servers_on_nginx[domain].append([path, proxy_pass, "kns"])
                            elif "kuaishou.com" in proxy_pass or "gifshow.com" in proxy_pass or "." in proxy_pass:
                                servers_on_nginx[domain].append([path, proxy_pass, "domain"])
                            else:
                                servers_on_nginx[domain].append([path, proxy_pass, "normal"])
    if is_fatal:
        exit(1)
    return servers_on_nginx, upstreams


import platform, subprocess, os, datetime, base64, json


def arch_suffix():
    machine = platform.machine().lower()
    if machine.startswith('i386') or machine.startswith('i686'):
        return '386'
    elif machine.startswith(('x86_64', 'amd64')):
        return 'amd64'
    elif machine.startswith(('armv8', 'arm64', 'aarch64')):
        return 'arm64'
    elif machine.startswith('s390x'):
        return 's390x'
    else:
        raise ValueError("Unsupported CPU architecture")


def export_bestIPS(r_path):
    best_ips = []

    with open(r_path, 'r') as csv_file:
        next(csv_file)
        c = 0
        for line in csv_file:
            best_ips.append(line.split(',')[0])
            c += 1
            if c == 2:
                break

    with open('best_IPS.txt', 'w') as f:
        for ip in best_ips:
            f.write(f"{ip}\n")
    os.remove("warp")
    return best_ips


def export_Hiddify(ips, r_path):
    creation_time = os.path.getctime(r_path)
    formatted_time = datetime.datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
    config_prefix = f'warp://{ips[0]}?ifp=10-20&ifps=20-60&ifpd=5-10&ifpm=m4#Warp-IR&&detour=warp://{ips[1]}?ifp=10-20&ifps=20-60&ifpd=5-10#Warp-IN-Warp'

    title = "//profile-title: base64:" + base64.b64encode('Women Life Freedom ✌️'.encode('utf-8')).decode('utf-8') + "\n"
    update_interval = "//profile-update-interval: 1\n"
    sub_info = "//subscription-userinfo: upload=0; download=0; total=10737418240000000; expire=2546249531\n"
    profile_web = "//profile-web-page-url: https://github.com/ByteMysticRogue\n"
    last_modified = "//last update on: " + formatted_time + "\n"

    with open('warp.json', 'w') as f:
        f.write(title + update_interval + sub_info + profile_web + last_modified + config_prefix)


def generate_conf():
    print("Generating Warp Conf")
    command = 'wget -N "https://gitlab.com/fscarmen/warp/-/raw/main/api.sh" && sudo bash api.sh -r'
    prc = subprocess.run(command, capture_output=True, text=True, shell=True)
    output = prc.stdout

    if (prc.returncode == 0) and output:
        conf = json.loads(output)
        os.remove("api.sh")
        return conf
    return None

def singbox_wg(tag, ips, detour):
    wg = {
        "tag": f"{tag}",
        "type": "wireguard",
        "server": f"{ips.split(':')[0]}",
        "server_port": int(ips.split(':')[1]),
        "local_address": [
            "172.16.0.2/32",
            "2606:4700:110:8735:bb29:91bc:1c82:aa73/128"
        ],
        "private_key": f"{wg_config['private_key']}",
        "peer_public_key": "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=",
        "mtu": 1384,
        "reserved": wg_config['config']['reserved'],
        "detour": f"{detour}",
        "workers": 2
    }
    return wg

def export_SingBox(t_ips):
    with open('Template/singbox_template.json', 'r') as f:
        data = json.load(f)
    
    data['outbounds'][0]['outbounds'].extend(['WARP-MAIN', 'WARP-WIW'])
    data['outbounds'][1]['outbounds'].extend(['WARP-MAIN', 'WARP-WIW'])
    
    main_wg = singbox_wg('WARP-MAIN', t_ips[0], "direct")
    data["outbounds"].insert(2, main_wg)
    wiw_wg = singbox_wg('WARP-WIW', t_ips[1], "WARP-MAIN")
    data["outbounds"].insert(3, wiw_wg)
    
    with open('sing-box.json', 'w') as f:
        json.dump(data, f, indent=4)

def export_xray(ips):
    xray_wg = {
      "protocol": "wireguard",
      "settings": {
        "address": [
          "172.16.0.2/32",
          "2606:4700:110:8735:bb29:91bc:1c82:aa73/128"
        ],
        "mtu": 1280,
        "peers": [
          {
            "endpoint": f"{ips[0]}",
            "publicKey": "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo="
          }
        ],
        "reserved": wg_config['config']['reserved'],
        "secretKey": f"{wg_config['private_key']}"
      },
        "streamSettings": {
            "sockopt": {
            "dialerProxy": "noise"
            }
        },
      "tag": "proxy"
    }
    noise = {
        "protocol": "freedom",
        "settings": {
        "noises":[
            {
                "type":"base64",
                "packet":"7nQBAAABAAAAAAAABnQtcmluZwZtc2VkZ2UDbmV0AAABAAE=",
                "delay":"30-60"
            }
            ]
        },
        "tag": "noise"
    }
    with open('Template/xray_template.json', 'r') as f:
        data = json.load(f)
    data['remarks'] = "WarpNoise"
    data['outbounds'].insert(0, xray_wg)
    data['outbounds'].insert(1, noise)
    
    with open('xray.json', 'w') as f:
        json.dump(data, f, indent=4)
    

def main():
    arch = arch_suffix()
    print("Fetch warp program...")
    url = f"https://gitlab.com/Misaka-blog/warp-script/-/raw/main/files/warp-yxip/warp-linux-{arch}"
    subprocess.run(["wget", url, "-O", "warp"])
    os.chmod("warp", 0o755)
    command = "./warp >/dev/null 2>&1"
    print("Scanning ips...")
    process = subprocess.Popen(command, shell=True)
    process.wait()
    if process.returncode != 0:
        print("Error: Warp execution failed.")
    else:
        print("Warp executed successfully.")

    script_directory = os.path.dirname(__file__)
    result_path = os.path.join(script_directory, 'result.csv')
    top_ips = export_bestIPS(result_path)
    export_Hiddify(top_ips, result_path)
    export_SingBox(top_ips)
    export_xray(top_ips)

    os.remove(result_path)


if __name__ == '__main__':
    wg_config = generate_conf()
    main()
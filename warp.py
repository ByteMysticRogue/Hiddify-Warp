import platform, subprocess, os, datetime, base64


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


def export_bestIPS(path):
    best_ips = []

    with open(path, 'r') as csv_file:
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

    return best_ips


def export_Hiddify(t_ips, f_ips):
    creation_time = os.path.getctime(f_ips)
    formatted_time = datetime.datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
    config_prefix = f'warp://{t_ips[0]}?ifp=10-20&ifps=20-60&ifpd=5-10#Warp-IR&&detour=warp://{t_ips[1]}?ifp=10-20&ifps=20-60&ifpd=5-10#Warp-IN-Warp'

    title = "//profile-title: base64:" + base64.b64encode('Women Life Freedom ✌️'.encode('utf-8')).decode(
        'utf-8') + "\n"
    update_interval = "//profile-update-interval: 1\n"
    sub_info = "//subscription-userinfo: upload=0; download=0; total=10737418240000000; expire=2546249531\n"
    profile_web = "//profile-web-page-url: https://github.com/ByteMysticRogue\n"
    last_modified = "//last update on: " + formatted_time + "\n"

    with open('warp.json', 'w') as op:
        op.write(title + update_interval + sub_info + profile_web + last_modified + config_prefix)


def main(script_dir):
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

    result_path = os.path.join(script_dir, 'result.csv')
    top_ips = export_bestIPS(result_path)
    export_Hiddify(t_ips=top_ips, f_ips=result_path)

    os.remove("warp")
    os.remove(result_path)


if __name__ == '__main__':
    script_directory = os.path.dirname(__file__)
    main(script_directory)
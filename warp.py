import platform
import subprocess
import os
import datetime
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# تابع برای رمزنگاری داده‌ها با AES
def encrypt_data(key, data):
    backend = default_backend()
    iv = os.urandom(16)  # برای تولید یک بردار IV تصادفی
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return iv + ciphertext

# تابع برای رمزگشایی داده‌ها با AES
def decrypt_data(key, data):
    backend = default_backend()
    iv = data[:16]  # بردار IV قبل از داده‌های رمزنگاری شده
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(data[16:]) + decryptor.finalize()
    return plaintext

# تابع ارسال داده‌های رمزنگاری شده
def send_encrypted_data(socket, data):
    encrypted_data = encrypt_data(key, data)
    socket.send(encrypted_data)

# تابع دریافت و رمزگشایی داده‌ها
def receive_decrypted_data(socket):
    encrypted_data = socket.recv(1024)
    decrypted_data = decrypt_data(key, encrypted_data)
    return decrypted_data

# کلید برای رمزنگاری و رمزگشایی (باید در محیط اجرایی خود به امانت نگهداری شود)
key = b'16_byte_secret_k'

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


def toSingBox(tag, clean_ip, detour):
    print("Generating Warp Conf")
    config_url = "https://api.zeroteam.top/warp?format=warp-go"
    conf_name = 'warp.conf'
    subprocess.run(["wget", config_url, "-O", f"{conf_name}"])
    cmd = ["./warp-go", f"--config={conf_name}", "--export-singbox=proxy.json"]
    process = subprocess.run(cmd, capture_output=True, text=True)
    output = process.stdout

    if (process.returncode == 0) and output:
        with open('proxy.json', 'r') as f:
            data = json.load(f)
            wg = data["outbounds"][0]
            wg['server'] = clean_ip.split(':')[0]
            wg['server_port'] = int(clean_ip.split(':')[1])
            wg['mtu'] = 1384
            wg['workers'] = 2
            wg['detour'] = detour
            wg['tag'] = tag
        return wg
    else:
        return None


def export_SingBox(t_ips, arch):
    with open('Sing-Box Template/template.json', 'r') as f:
        data = json.load(f)

    warp_go_url = f"https://gitlab.com/Misaka-blog/warp-script/-/raw/main/files/warp-go/warp-go-latest-linux-{arch}"
    subprocess.run(["wget", warp_go_url, "-O", "warp-go"])
    os.chmod("warp-go", 0o755)

    main_wg = toSingBox('WARP-MAIN', t_ips[0], "direct")
    data["outbounds"].insert(1, main_wg)
    wiw_wg = toSingBox('WARP-WIW', t_ips[1], "WARP-MAIN")
    data["outbounds"].insert(2, wiw_wg)

    with open('sing-box.json', 'w') as f:
        f.write(json.dumps(data, indent=4))

    os.remove("warp.conf")
    os.remove("proxy.json")
    os.remove("warp-go")


def main(script_dir):
    arch = arch_suffix()
    print("Fetch warp program...")
    url = f"https://gitlab.com/Misaka-blog/warp-script/-/raw/main/files/warp-yxip/warp-linux-{arch

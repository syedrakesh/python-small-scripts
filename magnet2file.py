import subprocess
import sys
import os
import shutil

def install_aria2():
    """Try to install aria2c depending on the platform."""
    import platform
    system = platform.system()

    if shutil.which("aria2c"):
        return True  # Already installed

    print("aria2c not found. Attempting to install...")

    try:
        if system == "Linux":
            subprocess.check_call(["sudo", "apt-get", "install", "-y", "aria2"])
        elif system == "Darwin":
            subprocess.check_call(["brew", "install", "aria2"])
        elif system == "Windows":
            subprocess.check_call(["winget", "install", "aria2"])
        return shutil.which("aria2c") is not None
    except Exception:
        return False

def download_magnet(magnet_link, save_path=None):
    if save_path is None:
        save_path = os.path.dirname(os.path.abspath(__file__))

    if not install_aria2():
        print("❌ Could not install aria2c automatically.")
        print("Install manually:")
        print("  Linux:   sudo apt install aria2")
        print("  macOS:   brew install aria2")
        print("  Windows: winget install aria2  OR  https://github.com/aria2/aria2/releases")
        sys.exit(1)

    os.makedirs(save_path, exist_ok=True)
    print(f"📁 Saving to: {save_path}")
    print(f"🚀 Starting download via aria2c...")

    cmd = [
        "aria2c",
        "--dir", save_path,
        "--seed-time=0",           # Don't seed after download
        "--max-connection-per-server=16",
        "--split=16",
        "--min-split-size=1M",
        "--console-log-level=notice",
        "--summary-interval=5",
        magnet_link
    ]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n✅ Download complete!")
        print(f"📁 Saved to: {save_path}")
    else:
        print(f"\n❌ aria2c exited with code {result.returncode}")

if __name__ == "__main__":
    magnet = (
        "magnet:?xt=urn:btih:2235DB8AB94EB76910235A747E3E045FB9EAC9E0"
        "&dn=Avatar+Fire+and+Ash+2025+2160p+AMZN+WEB-DL+DDP5.1+HDR10%2B+HEVC-KyoGo"
        "&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce"
        "&tr=udp%3A%2F%2Fopentracker.io%3A6969%2Fannounce"
        "&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce"
        "&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce"
        "&tr=udp%3A%2F%2Fbandito.byterunner.io%3A6969%2Fannounce"
        "&tr=udp%3A%2F%2Ftracker.qu.ax%3A6969%2Fannounce"
        "&tr=http%3A%2F%2Ftracker.renfei.net%3A8080%2Fannounce"
        "&tr=udp%3A%2F%2Fopen.free-tracker.ga%3A6969%2Fannounce"
        "&tr=http%3A%2F%2Ftracker.ipv6tracker.org%2Fannounce"
        "&tr=udp%3A%2F%2Ftracker2.dler.org%3A80%2Fannounce"
        "&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce"
        "&tr=udp%3A%2F%2Fopen.tracker.cl%3A1337%2Fannounce"
        "&tr=http%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce"
        "&tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce"
        "&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce"
        "&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce"
        "&tr=udp%3A%2F%2Fcoppersurfer.tk%3A6969%2Fannounce"
        "&tr=udp%3A%2F%2Ftracker.zer0day.to%3A1337%2Fannounce"
    )

    download_magnet(magnet)

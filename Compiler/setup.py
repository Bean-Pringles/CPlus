import os
import sys
import platform
import subprocess
import tempfile
from PIL import Image

# ---------------- CONFIG ----------------
EXT = ".cpx"
TYPE_NAME = "CPlus.Source"
FRIENDLY_NAME = "C+ Source File"

WINDOWS_SIZES = [16, 24, 32, 48, 64, 128, 256]
LINUX_SIZES = [16, 24, 32, 48, 64, 128, 256, 512]
MAC_SIZES = [16, 32, 64, 128, 256, 512, 1024]

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
# ----------------------------------------


# ================ ICON GENERATION ================
def load_image(path):
    img = Image.open(path)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img


def make_windows_ico(img, out_path):
    img.save(out_path, format="ICO", sizes=[(s, s) for s in WINDOWS_SIZES])
    print(f"[✓] Windows ICO: {out_path}")


def make_linux_icons(img, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for size in LINUX_SIZES:
        resized = img.resize((size, size), Image.LANCZOS)
        resized.save(os.path.join(out_dir, f"{size}x{size}.png"))
    print(f"[✓] Linux icons: {out_dir}/")


def make_macos_icns(img, out_path):
    """macOS .icns creation using iconutil"""
    with tempfile.TemporaryDirectory() as tmp:
        iconset = os.path.join(tmp, "icon.iconset")
        os.makedirs(iconset)

        for size in MAC_SIZES:
            normal = img.resize((size, size), Image.LANCZOS)
            normal.save(os.path.join(iconset, f"icon_{size}x{size}.png"))

            if size <= 512:
                retina = img.resize((size * 2, size * 2), Image.LANCZOS)
                retina.save(os.path.join(iconset, f"icon_{size}x{size}@2x.png"))

        subprocess.run(
            ["iconutil", "-c", "icns", iconset, "-o", out_path],
            check=True
        )

    print(f"[✓] macOS ICNS: {out_path}")


def generate_icons(source_image):
    """Generate icons for the current OS only"""
    base = "cpx"
    img = load_image(source_image)
    os_name = platform.system()

    if os_name == "Windows":
        make_windows_ico(img, os.path.join(SCRIPT_DIR, f"{base}.ico"))
    elif os_name == "Linux":
        make_linux_icons(img, os.path.join(SCRIPT_DIR, f"{base}_linux_icons"))
    elif os_name == "Darwin":
        make_macos_icns(img, os.path.join(SCRIPT_DIR, f"{base}.icns"))


# ================ LAUNCHER CREATION ================
def create_launcher():
    """Create platform-specific launcher"""
    compiler_script = os.path.join(SCRIPT_DIR, "compiler.py")
    
    if platform.system() == "Windows":
        bat_path = os.path.join(SCRIPT_DIR, "cpx.bat")
        if os.path.exists(bat_path):
            print("[*] cpx.bat already exists, skipping creation.")
        else:
            with open(bat_path, "w") as f:
                f.write(f'@echo off\npython "{compiler_script}" %*\n')
            print(f"[+] Created launcher: {bat_path}")
    else:
        sh_path = os.path.join(SCRIPT_DIR, "cpx")
        if os.path.exists(sh_path):
            print("[*] cpx launcher already exists, skipping creation.")
        else:
            with open(sh_path, "w") as f:
                f.write(f'#!/bin/bash\npython3 "{compiler_script}" "$@"\n')
            os.chmod(sh_path, 0o755)
            print(f"[+] Created launcher: {sh_path}")


# ================ PATH MANAGEMENT ================
def update_path_windows():
    """Update PATH on Windows"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             '[Environment]::GetEnvironmentVariable("Path","User")'],
            capture_output=True, text=True
        )
        current_path = result.stdout.strip()
        paths = [p.strip() for p in current_path.split(";") if p.strip()]
        
        if SCRIPT_DIR not in paths:
            new_path = current_path + (';' if current_path else '') + SCRIPT_DIR
            subprocess.run([
                'powershell', '-Command',
                f"[Environment]::SetEnvironmentVariable('Path', '{new_path}', 'User')"
            ], check=True)
            print(f"[+] Added {SCRIPT_DIR} to the user PATH.")
            print("[*] Restart your terminal for changes to apply.")
        else:
            print("[*] Directory already in PATH.")
    except Exception as e:
        print(f"[!] Failed to update PATH: {e}")


def update_path_unix():
    """Update PATH on Linux/macOS"""
    home = os.path.expanduser("~")
    
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        rc_file = os.path.join(home, ".zshrc")
    elif "bash" in shell:
        rc_file = os.path.join(home, ".bashrc")
    else:
        rc_file = os.path.join(home, ".profile")
    
    path_export = f'export PATH="$PATH:{SCRIPT_DIR}"\n'
    
    try:
        if os.path.exists(rc_file):
            with open(rc_file, "r") as f:
                content = f.read()
                if SCRIPT_DIR in content:
                    print("[*] Directory already in PATH configuration.")
                    return
        
        with open(rc_file, "a") as f:
            f.write(f"\n# Added by cpx installer\n{path_export}")
        
        print(f"[+] Added {SCRIPT_DIR} to PATH in {rc_file}")
        print(f"[*] Run 'source {rc_file}' or restart your terminal for changes to apply.")
        
    except Exception as e:
        print(f"[!] Failed to update PATH: {e}")
        print(f"[*] Manual setup: Add 'export PATH=\"$PATH:{SCRIPT_DIR}\"' to your {rc_file}")


# ================ FILE TYPE REGISTRATION ================
def register_windows():
    """Register .cpx file type on Windows"""
    import winreg
    import ctypes

    ico_path = os.path.join(SCRIPT_DIR, "cpx.ico")
    if not os.path.exists(ico_path):
        raise FileNotFoundError("cpx.ico not found - run icon generation first")

    def set_key(root, path, name, value):
        key = winreg.CreateKey(root, path)
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)

    # Register extension
    set_key(winreg.HKEY_CLASSES_ROOT, EXT, "", TYPE_NAME)
    
    # Register type
    set_key(winreg.HKEY_CLASSES_ROOT, TYPE_NAME, "", FRIENDLY_NAME)
    
    # Register icon
    set_key(winreg.HKEY_CLASSES_ROOT, TYPE_NAME + r"\DefaultIcon", "", ico_path)
    
    # Notify Windows of the change
    SHCNE_ASSOCCHANGED = 0x08000000
    SHCNF_IDLIST = 0x0000
    try:
        ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
        print("[✓] Windows registry updated for .cpx")
        print("[*] Explorer notified - changes should appear immediately")
    except:
        print("[✓] Windows registry updated for .cpx")
        print("[!] Could not notify Explorer - you may need to restart Explorer or reboot")


def register_macos():
    """Register .cpx file type on macOS"""
    icns_path = os.path.join(SCRIPT_DIR, "cpx.icns")
    if not os.path.exists(icns_path):
        raise FileNotFoundError("cpx.icns not found - run icon generation first")

    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>cpx</string>
            </array>
            <key>CFBundleTypeName</key>
            <string>{FRIENDLY_NAME}</string>
            <key>CFBundleTypeRole</key>
            <string>Editor</string>
            <key>CFBundleTypeIconFile</key>
            <string>cpx</string>
        </dict>
    </array>
</dict>
</plist>
"""

    with tempfile.TemporaryDirectory() as tmp:
        app = os.path.join(tmp, "CPlusIcons.app")
        os.makedirs(os.path.join(app, "Contents", "Resources"))

        with open(os.path.join(app, "Contents", "Info.plist"), "w") as f:
            f.write(plist)

        os.system(f"cp '{icns_path}' '{app}/Contents/Resources/cpx.icns'")

        subprocess.run([
            "/System/Library/Frameworks/CoreServices.framework"
            "/Frameworks/LaunchServices.framework"
            "/Support/lsregister",
            "-f",
            app
        ])

    print("[✓] macOS LaunchServices updated for .cpx")


def register_linux():
    """Register .cpx file type on Linux"""
    icon_dir = os.path.join(SCRIPT_DIR, "cpx_linux_icons")
    if not os.path.isdir(icon_dir):
        raise FileNotFoundError("cpx_linux_icons directory not found - run icon generation first")

    mime_dir = os.path.expanduser("~/.local/share/mime/packages")
    app_dir = os.path.expanduser("~/.local/share/applications")
    icon_target = os.path.expanduser("~/.local/share/icons/hicolor")

    os.makedirs(mime_dir, exist_ok=True)
    os.makedirs(app_dir, exist_ok=True)

    mime_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="text/x-cpx">
    <comment>{FRIENDLY_NAME}</comment>
    <glob pattern="*.cpx"/>
  </mime-type>
</mime-info>
"""

    mime_file = os.path.join(mime_dir, "cpx.xml")
    with open(mime_file, "w") as f:
        f.write(mime_xml)

    subprocess.run(["update-mime-database", os.path.expanduser("~/.local/share/mime")])

    for file in os.listdir(icon_dir):
        size = file.replace(".png", "")
        target = os.path.join(icon_target, size, "mimetypes")
        os.makedirs(target, exist_ok=True)
        subprocess.run([
            "cp",
            os.path.join(icon_dir, file),
            os.path.join(target, "text-x-cpx.png")
        ])

    subprocess.run(["gtk-update-icon-cache", icon_target], stderr=subprocess.DEVNULL)

    print("[✓] Linux MIME + icon registered for .cpx")


# ================ MAIN ================
def main():
    os_name = platform.system()
    print(f"[*] Detected OS: {os_name}")
    print(f"[*] Installation directory: {SCRIPT_DIR}")
    
    # Check for icon source
    icon_source = os.path.join(SCRIPT_DIR, "icon.png")
    if os.path.exists(icon_source):
        print("\n=== GENERATING ICONS ===")
        try:
            generate_icons(icon_source)
        except Exception as e:
            print(f"[!] Icon generation failed: {e}")
            print("[*] Continuing with installation...")
    else:
        print(f"[*] No icon.png found at {icon_source}, skipping icon generation")
    
    # Create launcher
    print("\n=== CREATING LAUNCHER ===")
    create_launcher()
    
    # Update PATH
    print("\n=== UPDATING PATH ===")
    if os_name == "Windows":
        update_path_windows()
    else:
        update_path_unix()
    
    # Register file type
    print("\n=== REGISTERING FILE TYPE ===")
    try:
        if os_name == "Windows":
            register_windows()
        elif os_name == "Darwin":
            register_macos()
        elif os_name == "Linux":
            register_linux()
        else:
            print("[!] Unsupported OS for file type registration")
    except Exception as e:
        print(f"[!] File type registration failed: {e}")
        print("[*] You may need to run with elevated privileges")
    
    print("\n[✓] Installation complete!")
    print("\n[*] Next steps:")
    print("    1. Restart your terminal")
    print("    2. Test with: cpx -v")


if __name__ == "__main__":
    main()

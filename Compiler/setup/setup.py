import os
import sys
import platform
import subprocess
import tempfile

# ---------------- CONFIG ----------------
EXT = ".cpx"
TYPE_NAME = "CPlus.Source"
FRIENDLY_NAME = "C+ Source File"

WINDOWS_SIZES = [16, 24, 32, 48, 64, 128, 256]
LINUX_SIZES = [16, 24, 32, 48, 64, 128, 256, 512]
MAC_SIZES = [16, 32, 64, 128, 256, 512, 1024]

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SETUP_DIR = os.path.abspath(os.path.dirname(__file__))
# ----------------------------------------


# ================ DEPENDENCY CHECKING ================
def check_python_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def install_python_package(package_name):
    """Install a Python package using pip"""
    print(f"[*] Installing {package_name}...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package_name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[+] Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError:
        print(f"[!] Failed to install {package_name}")
        return False


def check_gcc():
    """Check if GCC is installed"""
    try:
        result = subprocess.run(
            ["gcc", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_gcc():
    """Automatically install GCC based on OS"""
    os_name = platform.system()
    
    print("\n[!] GCC compiler not found!")
    print("[*] Attempting automatic installation...")
    
    if os_name == "Windows":
        print("[*] Checking for package managers...")
        
        # Try Chocolatey first
        try:
            result = subprocess.run(["choco", "--version"], capture_output=True)
            if result.returncode == 0:
                print("[*] Found Chocolatey, installing MinGW...")
                subprocess.run(["choco", "install", "mingw", "-y"], check=True)
                print("[+] MinGW installed via Chocolatey")
                print("[*] Please restart your terminal for changes to take effect")
                return True
        except:
            pass
        
        # Try winget
        try:
            result = subprocess.run(["winget", "--version"], capture_output=True)
            if result.returncode == 0:
                print("[*] Found winget, installing MinGW...")
                subprocess.run(["winget", "install", "-e", "--id", "GnuWin32.MinGW"], check=True)
                print("[+] MinGW installed via winget")
                print("[*] Please restart your terminal for changes to take effect")
                return True
        except:
            pass
        
        # Manual instructions if no package manager found
        print("""
[!] No package manager found. Please install GCC manually:
    1. Install Chocolatey from: https://chocolatey.org/install
       Then run: choco install mingw
    2. Or install MinGW-w64 from: https://www.mingw-w64.org/
    3. Or install MSYS2 from: https://www.msys2.org/
       Then run: pacman -S mingw-w64-x86_64-gcc
        """)
        return False
            
    elif os_name == "Darwin":
        print("[*] Installing Xcode Command Line Tools...")
        try:
            # Try xcode-select install
            result = subprocess.run(["xcode-select", "--install"], capture_output=True, text=True)
            
            if "already installed" in result.stderr.lower():
                print("[*] Xcode tools already installed but GCC not found")
                print("[*] Trying to install GCC via Homebrew...")
            else:
                print("[*] Xcode Command Line Tools installation started")
                print("[*] Please follow the prompts in the dialog box")
                print("[*] After installation completes, re-run this installer")
                return False
            
            # Try Homebrew as fallback
            result = subprocess.run(["brew", "--version"], capture_output=True)
            if result.returncode == 0:
                print("[*] Found Homebrew, installing GCC...")
                subprocess.run(["brew", "install", "gcc"], check=True)
                print("[+] GCC installed via Homebrew")
                return True
            else:
                print("[!] Homebrew not found")
                print("[*] Install Homebrew from: https://brew.sh")
                print("[*] Then run: brew install gcc")
                return False
                
        except FileNotFoundError:
            print("[!] xcode-select not found")
            print("[*] Please install Xcode Command Line Tools manually")
            return False
        except Exception as e:
            print(f"[!] Installation failed: {e}")
            return False
            
    elif os_name == "Linux":
        print("[*] Detecting package manager...")
        
        # Debian/Ubuntu
        if os.path.exists("/usr/bin/apt-get"):
            print("[*] Detected apt, installing build-essential...")
            try:
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "build-essential"], check=True)
                print("[+] GCC installed via apt")
                return True
            except subprocess.CalledProcessError:
                print("[!] Installation failed. Try manually: sudo apt-get install build-essential")
                return False
        
        # Fedora/RHEL
        elif os.path.exists("/usr/bin/dnf"):
            print("[*] Detected dnf, installing gcc...")
            try:
                subprocess.run(["sudo", "dnf", "install", "-y", "gcc", "gcc-c++", "make"], check=True)
                print("[+] GCC installed via dnf")
                return True
            except subprocess.CalledProcessError:
                print("[!] Installation failed. Try manually: sudo dnf install gcc")
                return False
        
        # Arch
        elif os.path.exists("/usr/bin/pacman"):
            print("[*] Detected pacman, installing gcc...")
            try:
                subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "gcc", "make"], check=True)
                print("[+] GCC installed via pacman")
                return True
            except subprocess.CalledProcessError:
                print("[!] Installation failed. Try manually: sudo pacman -S gcc")
                return False
        
        # openSUSE
        elif os.path.exists("/usr/bin/zypper"):
            print("[*] Detected zypper, installing gcc...")
            try:
                subprocess.run(["sudo", "zypper", "install", "-y", "gcc", "gcc-c++", "make"], check=True)
                print("[+] GCC installed via zypper")
                return True
            except subprocess.CalledProcessError:
                print("[!] Installation failed. Try manually: sudo zypper install gcc")
                return False
        
        else:
            print("[!] Unknown package manager")
            print("[*] Please install GCC manually for your distribution")
            return False
    
    return False


def check_dependencies():
    """Check and install all required dependencies"""
    print("\n=== CHECKING DEPENDENCIES ===")
    
    all_satisfied = True
    
    # Check standard library modules (these should always be available)
    stdlib_modules = ["re", "sys", "os", "subprocess", "platform", "tempfile"]
    print("[*] Checking Python standard library modules...")
    for mod in stdlib_modules:
        if check_python_package(mod):
            print(f"    [+] {mod}")
        else:
            print(f"    [!] {mod} missing (this is unusual)")
            all_satisfied = False
    
    # Check Pillow
    print("\n[*] Checking third-party packages...")
    if not check_python_package("Pillow", "PIL"):
        print("    [!] Pillow not installed")
        if install_python_package("Pillow"):
            all_satisfied = all_satisfied and True
        else:
            print("    [!] Please install manually: pip install Pillow")
            all_satisfied = False
    else:
        print("    [+] Pillow")
    
    # Check GCC
    print("\n[*] Checking command-line tools...")
    if check_gcc():
        print("    [+] GCC compiler")
    else:
        print("    [!] GCC compiler not found")
        if install_gcc():
            # Verify installation
            if check_gcc():
                print("    [+] GCC compiler installed successfully")
            else:
                print("    [!] GCC installed but not found in PATH")
                print("    [*] You may need to restart your terminal")
                all_satisfied = False
        else:
            all_satisfied = False
    
    if not all_satisfied:
        print("\n[!] Some dependencies are missing. Please install them before continuing.")
        print("[*] You can re-run this installer after installing dependencies.")
        return False
    
    print("\n[+] All dependencies satisfied!")
    return True


# ================ ICON GENERATION ================
def load_image(path):
    from PIL import Image
    img = Image.open(path)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img


def make_windows_ico(img, out_path):
    img.save(out_path, format="ICO", sizes=[(s, s) for s in WINDOWS_SIZES])
    print(f"[+] Windows ICO: {out_path}")


def make_linux_icons(img, out_dir):
    from PIL import Image
    os.makedirs(out_dir, exist_ok=True)
    for size in LINUX_SIZES:
        resized = img.resize((size, size), Image.LANCZOS)
        resized.save(os.path.join(out_dir, f"{size}x{size}.png"))
    print(f"[+] Linux icons: {out_dir}/")


def make_macos_icns(img, out_path):
    """macOS .icns creation using iconutil"""
    from PIL import Image
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

    print(f"[+] macOS ICNS: {out_path}")


def generate_icons(source_image):
    """Generate icons for the current OS only"""
    base = "cpx"
    img = load_image(source_image)
    os_name = platform.system()

    if os_name == "Windows":
        make_windows_ico(img, os.path.join(SETUP_DIR, f"{base}.ico"))
    elif os_name == "Linux":
        make_linux_icons(img, os.path.join(SETUP_DIR, f"{base}_linux_icons"))
    elif os_name == "Darwin":
        make_macos_icns(img, os.path.join(SETUP_DIR, f"{base}.icns"))


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

    ico_path = os.path.join(SETUP_DIR, "cpx.ico")
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
        print("[+] Windows registry updated for .cpx")
        print("[*] Explorer notified - changes should appear immediately")
    except:
        print("[+] Windows registry updated for .cpx")
        print("[!] Could not notify Explorer - you may need to restart Explorer or reboot")


def register_macos():
    """Register .cpx file type on macOS"""
    icns_path = os.path.join(SETUP_DIR, "cpx.icns")
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

    print("[+] macOS LaunchServices updated for .cpx")


def register_linux():
    """Register .cpx file type on Linux"""
    icon_dir = os.path.join(SETUP_DIR, "cpx_linux_icons")
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

    print("[+] Linux MIME + icon registered for .cpx")


def parse_bool(value):
    """Convert string argument to boolean"""
    if isinstance(value, bool):
        return value
    if value.lower() in ('true', '1', 'yes', 'y', 'on'):
        return True
    if value.lower() in ('false', '0', 'no', 'n', 'off'):
        return False
    raise ValueError(f"Invalid boolean value: {value}")


# ================ MAIN ================
def main():
    os_name = platform.system()
    
    # Parse command line arguments
    if len(sys.argv) != 6:
        print("[!] Error: Invalid number of arguments")
        print("[*] Usage: python setup.py [dependencies] [icons] [launcher] [path] [register]")
        print("[*] Example: python setup.py True True True True True")
        sys.exit(1)
    
    try:
        run_dependencies = parse_bool(sys.argv[1])
        run_icons = parse_bool(sys.argv[2])
        run_launcher = parse_bool(sys.argv[3])
        run_path = parse_bool(sys.argv[4])
        run_register = parse_bool(sys.argv[5])
    except ValueError as e:
        print(f"[!] Error: {e}")
        print("[*] Arguments must be True/False or 1/0")
        sys.exit(1)
    
    print(f"[*] Detected OS: {os_name}")
    print(f"[*] Installation directory: {SCRIPT_DIR}")
    
    # 1. Check dependencies
    if run_dependencies:
        if not check_dependencies():
            print("\n[!] Installation cannot continue until dependencies are satisfied.")
            sys.exit(1)
    
    # 2. Generate icons
    if run_icons:
        icon_source = os.path.join(SETUP_DIR, "icon.png")
        if os.path.exists(icon_source):
            print("\n=== GENERATING ICONS ===")
            try:
                generate_icons(icon_source)
            except Exception as e:
                print(f"[!] Icon generation failed: {e}")
        else:
            print(f"\n[!] No icon.png found at {icon_source}")
            if run_register:
                print("[!] Cannot register file type without icons")
                run_register = False
    
    # 3. Create launcher
    if run_launcher:
        print("\n=== CREATING LAUNCHER ===")
        create_launcher()
    
    # 4. Update PATH
    if run_path:
        print("\n=== UPDATING PATH ===")
        if os_name == "Windows":
            update_path_windows()
        else:
            update_path_unix()
    
    # 5. Register file type
    if run_register:
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
    
    print("\n[+] Installation complete!")


if __name__ == "__main__":
    main()
    print("")
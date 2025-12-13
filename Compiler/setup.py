import os
import subprocess
import sys
import platform

base_dir = os.path.dirname(os.path.abspath(__file__))
compiler_script = os.path.join(base_dir, "compiler.py")

def is_windows():
    return platform.system() == "Windows"

def is_linux():
    return platform.system() == "Linux"

def is_macos():
    return platform.system() == "Darwin"

def create_launcher():
    """Create platform-specific launcher"""
    if is_windows():
        # Windows: Create .bat file
        bat_path = os.path.join(base_dir, "cpx.bat")
        if os.path.exists(bat_path):
            print("[*] cpx.bat already exists, skipping creation.")
        else:
            with open(bat_path, "w") as f:
                f.write(f'@echo off\npython "{compiler_script}" %*\n')
            print(f"[+] Created launcher: {bat_path}")
    else:
        # Linux/macOS: Create shell script
        sh_path = os.path.join(base_dir, "cpx")
        if os.path.exists(sh_path):
            print("[*] cpx launcher already exists, skipping creation.")
        else:
            with open(sh_path, "w") as f:
                f.write(f'#!/bin/bash\npython3 "{compiler_script}" "$@"\n')
            # Make executable
            os.chmod(sh_path, 0o755)
            print(f"[+] Created launcher: {sh_path}")

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
        
        if base_dir not in paths:
            new_path = current_path + (';' if current_path else '') + base_dir
            subprocess.run([
                'powershell', '-Command',
                f"[Environment]::SetEnvironmentVariable('Path', '{new_path}', 'User')"
            ], check=True)
            print(f"[+] Added {base_dir} to the user PATH.")
            print("[*] Restart your terminal for changes to apply.")
        else:
            print("[*] Directory already in PATH.")
    except Exception as e:
        print(f"[!] Failed to update PATH: {e}")

def update_path_unix():
    """Update PATH on Linux/macOS"""
    home = os.path.expanduser("~")
    
    # Determine which shell config file to use
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        rc_file = os.path.join(home, ".zshrc")
    elif "bash" in shell:
        rc_file = os.path.join(home, ".bashrc")
    else:
        rc_file = os.path.join(home, ".profile")
    
    path_export = f'export PATH="$PATH:{base_dir}"\n'
    
    try:
        # Check if already in config file
        if os.path.exists(rc_file):
            with open(rc_file, "r") as f:
                content = f.read()
                if base_dir in content:
                    print("[*] Directory already in PATH configuration.")
                    return
        
        # Append to config file
        with open(rc_file, "a") as f:
            f.write(f"\n# Added by cpx installer\n{path_export}")
        
        print(f"[+] Added {base_dir} to PATH in {rc_file}")
        print(f"[*] Run 'source {rc_file}' or restart your terminal for changes to apply.")
        
    except Exception as e:
        print(f"[!] Failed to update PATH: {e}")
        print(f"[*] Manual setup: Add 'export PATH=\"$PATH:{base_dir}\"' to your {rc_file}")

def main():
    print(f"[*] Detected OS: {platform.system()}")
    print(f"[*] Installation directory: {base_dir}")
    
    # Create launcher
    create_launcher()
    
    # Update PATH based on OS
    if is_windows():
        update_path_windows()
    else:
        update_path_unix()
    
    print("\n[✓] Installation complete!")

if __name__ == "__main__":
    main()


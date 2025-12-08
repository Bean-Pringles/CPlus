import os
import subprocess

base_dir = os.path.dirname(os.path.abspath(__file__))
compiler_script = os.path.join(base_dir, "compiler.py")
bat_path = os.path.join(base_dir, "cpc.bat")

# Create launcher batch file safely
if os.path.exists(bat_path):
    print("[*] cpc.bat already exists, skipping creation.")
else:
    with open(bat_path, "w") as f:
        f.write(f'@echo off\npython "{compiler_script}" %*\n')
    print(f"[+] Created launcher: {bat_path}")

# Update PATH (user-level)
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
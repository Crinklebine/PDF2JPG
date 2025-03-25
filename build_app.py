import os
import shutil
import subprocess

# 🔹 Customize the output EXE name
output_exe_name = "PDFtoJPG.exe"  # Change this to your desired EXE name

# 🔹 Paths
script_name = "main-threaded.py"  # Change if your script has a different name
icon_path = "icon/pdftojpg.ico"
build_dir = "build"
dist_dir = "dist"
spec_file = f"{os.path.splitext(script_name)[0]}.spec"

# 🔹 Ensure the icon exists
if not os.path.exists(icon_path):
    print(f"❌ Error: Icon file '{icon_path}' not found! Please place it in the 'icon/' directory.")
    exit(1)

# 🔹 Clean up old builds
def clean_old_builds():
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)  # Remove old build directory
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)  # Remove old dist directory
    if os.path.exists(spec_file):
        os.remove(spec_file)  # Remove old spec file
    print("✅ Cleaned up old builds.")

# 🔹 Run PyInstaller with a custom EXE name
def build_exe():
    print(f"🚀 Building the EXE: {output_exe_name} ...")

    command = [
        "pyinstaller",
        "--onefile",  # Creates a single EXE file
        "--windowed",  # Prevents the console from opening
        f"--add-data={icon_path};icon",  # Ensures the icon file is bundled
        f"--icon={icon_path}",  # Sets the EXE’s icon
        f"--name={output_exe_name.replace('.exe', '')}",  # Custom EXE name
        script_name  # The Python script to compile
    ]

    result = subprocess.run(command, shell=True)

    if result.returncode == 0:
        print(f"🎉 Build successful! EXE is located at: dist/{output_exe_name}")
    else:
        print("❌ Build failed. Check the output above for errors.")

if __name__ == "__main__":
    clean_old_builds()
    build_exe()

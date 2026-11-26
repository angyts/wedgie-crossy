"""Build a bytecode-only Wedgie installation package from readable sources."""
import argparse
import json
import pathlib
import subprocess
import tempfile
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", default="mpy-cross")
    args = parser.parse_args()
    version = subprocess.check_output([args.compiler, "--version"], text=True).strip()
    print(version)
    if "v1.29.0" not in version.split():
        raise SystemExit("Use mpy-cross built from MicroPython v1.29.0, matching the device.")
    manifest = json.loads((ROOT / "wedgie.json").read_text())
    with tempfile.TemporaryDirectory(dir=ROOT) as temp:
        stage = pathlib.Path(temp)
        for app in manifest["apps"]:
            files = []
            for name in app["files"]:
                source = ROOT / "src" / name
                if not source.is_file():
                    raise SystemExit("Missing source: " + str(source))
                if source.read_bytes() != (ROOT / name).read_bytes():
                    raise SystemExit("Source copies differ: " + name + "; reconcile before building")
                output = source.with_suffix(".mpy").name
                subprocess.run([args.compiler, "-o", str(stage / output), str(source)], check=True)
                if (stage / output).read_bytes()[:1] != b"M":
                    raise SystemExit("Invalid bytecode: " + output)
                files.append(output)
            app["files"] = files
        (stage / "wedgie.json").write_text(json.dumps(manifest, indent=2) + "\n")
        dest = ROOT / "build" / "mpy"
        dest.parent.mkdir(exist_ok=True)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(stage, dest)
    print("Built:", dest)
    print("Install with: python wedgie.py install build/mpy")

if __name__ == "__main__":
    main()

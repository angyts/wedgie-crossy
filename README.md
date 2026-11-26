# Wedgie Crossy Road

When you are in Hanoi, you see the road, and you try to cross it. Yes that's crossy road except that they will just flatten you. And now we are porting it to the wedgie.

## Development and installation (macOS)

From the repository directory, activate the existing virtual environment:

```bash
source .venv/bin/activate
```

If it does not exist yet, create it with `python3 -m venv .venv` first.

### Fix Python SSL certificate verification errors

If `wedgie.py` fails fetching the firmware manifest with
`CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`,
activate the virtual environment and run:

```bash
python -m pip install --upgrade certifi
export SSL_CERT_FILE="$(python -m certifi)"
```

The export applies to the current terminal session; repeat it in a new terminal.
This keeps HTTPS certificate verification enabled. If pip itself cannot connect
or the error persists, check the local CA trust configuration rather than
disabling certificate verification.

### Update, test and install

```bash
git pull origin main
python -m unittest discover -s tests -v
python wedgie.py install .
```

To leave the virtual environment, run `deactivate`.

## Experimental precompiled deployment (MicroPython 1.29.0)

Readable application sources are in `src/`. Root Python copies remain temporarily
for existing host tests; the builder refuses to compile if copies differ.

Build the matching compiler on macOS (requires git, make and a C compiler):

```bash
git clone --branch v1.29.0 --depth 1 https://github.com/micropython/micropython.git ../micropython-1.29
make -C ../micropython-1.29/mpy-cross
python tools/build_mpy.py --compiler ../micropython-1.29/mpy-cross/build/mpy-cross
```

The generated `build/mpy/` contains only application bytecode and a manifest.
Before installing, uninstall the old Crossy app using the device's supported
app removal workflow and verify with `python wedgie.py debug` that its old
crossy*.py files are gone. Do not delete firmware files.

```bash
python wedgie.py install build/mpy
```

This installer path and bytecode compatibility still require physical verification.
Do not install the root source manifest for the compiled trial. If the matching
compiler tag or installer is unavailable, stop and report the error rather than
using a mismatched compiler. Keep the source installation as a rollback option.

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

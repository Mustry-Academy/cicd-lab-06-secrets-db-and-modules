#!/usr/bin/env python3
"""Mint Ignition 8.3 embedded-secret ciphertexts using this repo's seed keys.

Instructor tooling — used to (re)generate the seeded db-connection password
ciphertexts without clicking through the gateway UI. Requires `jwcrypto`
(pip install jwcrypto).

Key chain (all files under services/config/ignition/keys/):
  passphrase --PBES2-HS512+A256KW--> root.json  -> root JWK
  root JWK   --A256KW-------------> kek.json   -> KEK JWK Set (primary first)
  KEK        --A256KW+A256GCM+DEF--> the password JWE

Usage:
  mint-embedded-secret.py <repo_root> <root_key_passphrase> <plaintext>

Prints the flattened-JSON JWE. Paste it as the `data` object of
  "password": { "type": "Embedded", "data": { ...printed object... } }
in the target resource's config.json, then scan (scripts/scan.sh config).

Only gateways holding these key files (i.e. the LOCAL lab gateway, which
boots with IGNITION_ROOT_KEY_PASSWORD) can decrypt the result — that
asymmetry is the whole point of the lab's seeded warm-up state.
"""
import json
import sys
import time

from jwcrypto import jwa, jwe, jwk

jwa.default_max_pbkdf2_iterations = 1_000_000  # Ignition uses p2c=210000


def decrypt_flat(flat: dict, key: jwk.JWK) -> bytes:
    e = jwe.JWE()
    e.deserialize(json.dumps(flat), key=key)
    return e.payload


def load_jwk(jwk_dict: dict) -> jwk.JWK:
    d = dict(jwk_dict)
    # Ignition writes key_ops: [wrapKey, unwrapKey]; jwcrypto's JWE layer
    # asks the key for encrypt/decrypt, so drop the restriction.
    d.pop("key_ops", None)
    return jwk.JWK(**d)


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    repo, passphrase, plaintext = sys.argv[1:4]
    keys_dir = f"{repo}/services/config/ignition/keys"

    root_flat = json.load(open(f"{keys_dir}/root.json"))
    root_key = load_jwk(json.loads(decrypt_flat(root_flat, jwk.JWK.from_password(passphrase))))

    kek_flat = json.load(open(f"{keys_dir}/kek.json"))
    kek_set = json.loads(decrypt_flat(kek_flat, root_key))
    kek_entries = kek_set["keys"] if isinstance(kek_set, dict) and "keys" in kek_set else [kek_set]
    kek = load_jwk(kek_entries[0])
    sys.stderr.write(f"KEK ids: {[k.get('kid') for k in kek_entries]}\n")

    protected = {
        "alg": "A256KW",
        "enc": "A256GCM",
        "iat": int(time.time()),
        "zip": "DEF",  # jwcrypto applies the DEF compression itself
    }
    if kek_entries[0].get("kid"):
        protected["kid"] = kek_entries[0]["kid"]

    token = jwe.JWE(plaintext=plaintext.encode(), protected=protected, recipient=kek)
    flat = json.loads(token.serialize(compact=False))
    flat.pop("header", None)
    print(json.dumps(flat, indent=2))


if __name__ == "__main__":
    main()

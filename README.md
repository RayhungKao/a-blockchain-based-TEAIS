# a-blockchain-based-TEAIS

> **Archived.** This research continues in
> [blockchain-based-teais-js](https://github.com/RayhungKao/blockchain-based-teais-js), which has the
> current implementation, tests, and research notes.

Third iteration (2024) of a blockchain-based triple-entry accounting information system, in
Python. It reads asset transfers from `at.xlsx`, hashes each row with SHA-256, encrypts the
amounts with Paillier (`phe`), and compares the homomorphic sum with an encryption of the plain
sum.

Known problems, left as they were:

- `generate_zkp` / `verify_zkp` are not a zero-knowledge proof, and `verify_zkp` always returns
  `False`: it compares a Paillier ciphertext with `0`. The current version replaces this with a
  publicly verifiable opening of each company's encrypted total.
- `generate_hashes` joins fields without a separator, so `["1", "23"]` and `["12", "3"]` hash the
  same. The current version hashes a canonical JSON encoding.
- There is no blockchain component yet.

## Setup

```sh
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
python3 main.py
```

Leave the values in `.env` empty: on the first run `main.py` generates a Paillier key pair and an
RSA key pair and writes them there. Never commit `.env`.

import os
import json
from phe import paillier
from dotenv import set_key

def generate_and_store_keys():
    public_key, private_key = paillier.generate_paillier_keypair()
    set_key('.env.sample', 'PUBLIC_KEY_N', str(public_key.n))
    set_key('.env.sample', 'PRIVATE_KEY_P', str(private_key.p))
    set_key('.env.sample', 'PRIVATE_KEY_Q', str(private_key.q))
    return public_key, private_key

def get_keys():
    if os.getenv('PUBLIC_KEY_N') and os.getenv('PRIVATE_KEY_P') and os.getenv('PRIVATE_KEY_Q'):
        public_key = paillier.PaillierPublicKey(int(os.getenv('PUBLIC_KEY_N')))
        private_key = paillier.PaillierPrivateKey(public_key, int(os.getenv('PRIVATE_KEY_P')), int(os.getenv('PRIVATE_KEY_Q')))
    else:
        public_key, private_key = generate_and_store_keys()
    return public_key, private_key

def encrypt_list(public_key, data_list):
    return [public_key.encrypt(x) for x in data_list]

def decrypt_list(private_key, encrypted_list):
    return [private_key.decrypt(x) for x in encrypted_list]

def serialize_encrypted_list(encrypted_list):
    return json.dumps([{'ciphertext': enc.ciphertext(), 'exponent': enc.exponent} for enc in encrypted_list])

def deserialize_encrypted_list(public_key, encrypted_list_json):
    deserialized = json.loads(encrypted_list_json)
    return [paillier.EncryptedNumber(public_key, enc['ciphertext'], enc['exponent']) for enc in deserialized]
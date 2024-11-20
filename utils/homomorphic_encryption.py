import json
from phe import paillier
from dotenv import load_dotenv, set_key, get_key
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Random import get_random_bytes

# Load environment variables from .env file
load_dotenv()

def generate_and_store_keys():
    # Generate homomorphic encryption key pair
    he_public_key, he_private_key = paillier.generate_paillier_keypair()
    set_key('.env', 'HE_PUBLIC_KEY_N', str(he_public_key.n))
    set_key('.env', 'HE_PRIVATE_KEY_P', str(he_private_key.p))
    set_key('.env', 'HE_PRIVATE_KEY_Q', str(he_private_key.q))
    
    # Generate RSA key pair for ZKP
    rsa_key = RSA.generate(2048)
    rsa_private_key = rsa_key.export_key().decode('utf-8')
    rsa_public_key = rsa_key.publickey().export_key().decode('utf-8')

    set_key('.env', 'RSA_PRIVATE_KEY', rsa_private_key)
    set_key('.env', 'RSA_PUBLIC_KEY', rsa_public_key)
    
    return (he_public_key, he_private_key), (rsa_public_key, rsa_private_key)

def get_keys():
    he_public_key_n = get_key('.env', 'HE_PUBLIC_KEY_N')
    he_private_key_p = get_key('.env', 'HE_PRIVATE_KEY_P')
    he_private_key_q = get_key('.env', 'HE_PRIVATE_KEY_Q')
    rsa_private_key = get_key('.env', 'RSA_PRIVATE_KEY')
    rsa_public_key = get_key('.env', 'RSA_PUBLIC_KEY')

    if he_public_key_n and he_private_key_p and he_private_key_q and rsa_private_key and rsa_public_key:
        he_public_key = paillier.PaillierPublicKey(int(he_public_key_n))
        he_private_key = paillier.PaillierPrivateKey(he_public_key, int(he_private_key_p), int(he_private_key_q))
        
        # Import the RSA key pair
        rsa_private_key = RSA.import_key(rsa_private_key)
        rsa_public_key = RSA.import_key(rsa_public_key)
    else:
        (he_public_key, he_private_key), (rsa_public_key, rsa_private_key) = generate_and_store_keys()
    
    return (he_public_key, he_private_key), (rsa_public_key, rsa_private_key)

def encrypt_list(public_key, data_list):
    return [public_key.encrypt(x) for x in data_list]

def decrypt_list(private_key, encrypted_list):
    return [private_key.decrypt(x) for x in encrypted_list]

# Function to convert encrypted data to JSON.
def serialize_encrypted_list(encrypted_list):
    serialized_data = []
    for enc in encrypted_list:
        if isinstance(enc, paillier.EncryptedNumber):
            serialized_data.append({
                'type': 'EncryptedNumber',
                'data': {
                    'ciphertext': enc.ciphertext(),
                    'exponent': enc.exponent
                }
            })
        else:
            serialized_data.append({
                'type': 'bytes',
                'value': enc.hex()
            })
    return json.dumps(serialized_data)

# Function to convert JSON back to encrypted data.
def deserialize_encrypted_list(public_key, encrypted_list_json):
    deserialized = json.loads(encrypted_list_json)
    restored_list = []
    for enc in deserialized:
        if enc['type'] == 'EncryptedNumber':
            restored_list.append(
                paillier.EncryptedNumber(public_key, enc['data']['ciphertext'], enc['data']['exponent'])
            )
        else:
            restored_list.append(
                bytes.fromhex(enc['value'])
            )
    return restored_list

def generate_zkp(rsa_public_key, encrypted_a, encrypted_b):
    # Generate a random value r
    r = get_random_bytes(16)

    # Encrypt r using the rsa_public_key
    cipher_rsa = PKCS1_OAEP.new(rsa_public_key)
    encrypted_r = cipher_rsa.encrypt(r)

    # Compute the difference between encrypted_a and encrypted_b
    encrypted_difference = encrypted_a - encrypted_b

    # Compute the proof: encrypted_difference + int.from_bytes(encrypted_r, byteorder='big')
    proof = encrypted_difference + int.from_bytes(r, byteorder='big')

    return proof, encrypted_r

def verify_zkp(rsa_private_key, proof, encrypted_r):
    # Decrypt the encrypted_r using the rsa_private_key
    cipher_rsa = PKCS1_OAEP.new(rsa_private_key)
    decrypted_r = cipher_rsa.decrypt(encrypted_r)
    
    # Convert decrypted_r from bytes to an integer
    decrypted_r_int = int.from_bytes(decrypted_r, byteorder='big')
    
    # Decrypt the proof
    decrypted_proof = proof - decrypted_r_int
    
    # Calculate the maximum possible value for R
    max_possible_R = (2 ** (rsa_private_key.size_in_bits() // 8)) - 1
    
    # Check if decrypted_r is within the expected range
    if not 0 <= decrypted_r_int <= max_possible_R:
        print(f"Warning: Decrypted R value {decrypted_r_int} is out of range. Expected range: [0, {max_possible_R}]")
        return False
    
    # Check if the decrypted proof equals zero
    if decrypted_proof != 0:
        print(f"Warning: Decrypted proof {decrypted_proof} does not equal zero")
        return False
    
    # If all checks pass, the ZKP is valid
    return True
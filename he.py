import json
import os
import pandas as pd
from phe import paillier
from dotenv import load_dotenv, set_key

# Load environment variables from .env file
load_dotenv()

# Function to generate and store keys in .env file
def generate_and_store_keys():
    public_key, private_key = paillier.generate_paillier_keypair()
    set_key('.env', 'PUBLIC_KEY_N', str(public_key.n))
    set_key('.env', 'PRIVATE_KEY_P', str(private_key.p))
    set_key('.env', 'PRIVATE_KEY_Q', str(private_key.q))
    return public_key, private_key

# Retrieve keys from .env file or generate them if they don't exist
if os.getenv('PUBLIC_KEY_N') and os.getenv('PRIVATE_KEY_P') and os.getenv('PRIVATE_KEY_Q'):
    public_key = paillier.PaillierPublicKey(int(os.getenv('PUBLIC_KEY_N')))
    private_key = paillier.PaillierPrivateKey(public_key, int(os.getenv('PRIVATE_KEY_P')), int(os.getenv('PRIVATE_KEY_Q')))
else:
    public_key, private_key = generate_and_store_keys()

# Print the public and private keys for development usage
print("Public Key:", public_key)
print("Private Key:", private_key)

# Step 2: Read product amounts from Excel file
df = pd.read_excel('at.xlsx')
print("DataFrame contents:\n", df)
print("DataFrame columns:", df.columns)

# Verify the column name and handle empty DataFrame or missing column
if 'product_amounts' in df.columns and not df.empty:
    product_amounts = df['product_amounts'].tolist()
else:
    print("The column 'product_amounts' does not exist or the Excel file is empty. Using dummy array.")
    product_amounts = [10, 20, 30, 40, 50]  # Dummy array

print("product_amounts:", product_amounts)

# Step 3: Encrypt the list
encrypted_amounts = [public_key.encrypt(x) for x in product_amounts]

# Serialize the encrypted amounts
# Convert each EncryptedNumber to a dictionary with ciphertext and exponent
serialized_encrypted_amounts = [
    {'ciphertext': enc.ciphertext(), 'exponent': enc.exponent}
    for enc in encrypted_amounts
]

# Convert the list of dictionaries to JSON
encrypted_amounts_json = json.dumps(serialized_encrypted_amounts)

# Print the JSON representation of the encrypted amounts
print("Encrypted amounts JSON:", encrypted_amounts_json)

# Deserialize the encrypted amounts
# Convert the JSON back to a list of dictionaries
deserialized_encrypted_amounts = json.loads(encrypted_amounts_json)
encrypted_amounts_restored = [
    paillier.EncryptedNumber(public_key, enc['ciphertext'], enc['exponent'])
    for enc in deserialized_encrypted_amounts
]

# Step 4: Decrypt the list
decrypted_amounts = [private_key.decrypt(x) for x in encrypted_amounts_restored]

# Step 5: Encrypt the sum of the original amounts
encrypted_sum = sum(encrypted_amounts_restored)

# Step 6: Decrypt the encrypted sum
decrypted_sum = private_key.decrypt(encrypted_sum)

# Step 7: Print the original, encrypted, and decrypted lists
print("Original amounts:", product_amounts)
print("Encrypted amounts:", encrypted_amounts_restored)
print("Decrypted amounts:", decrypted_amounts)

# Step 8: Print the sum of the original amounts and the decrypted sum
print("Sum of original amounts:", sum(product_amounts))
print("Decrypted sum of encrypted amounts:", decrypted_sum)

# Verify the type of each encrypted amount
print("Type of each encrypted amount:", type(encrypted_amounts_restored[0]))
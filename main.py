from dotenv import load_dotenv
from utils.hashing import generate_hashes
from utils.homomorphic_encryption import generate_zkp, verify_zkp, generate_and_store_keys, get_keys, encrypt_list, decrypt_list, serialize_encrypted_list, deserialize_encrypted_list
from utils.excel_operations import read_excel_file, write_to_excel, generate_and_add_hashes, update_column

# Constants
EXCEL_FILE_NAME = 'at.xlsx'
SHEET_NAME = 'AT_list'
COLUMNS_TO_HASH = ['#', 'seller', 'buyer', 'date', 'quantity', 'unit', 'unit-price', 'amount', 'item-description']
HASHED_COLUMN_NAME = 'hashed-AT-info'
AMOUNT_COLUMN = 'amount'
HE_COLUMN_NAME = 'HE_pk_sender(amount)'

# Load environment variables from .env file
load_dotenv()

# Retrieve keys from .env file or generate them if they don't exist
(he_public_key, he_private_key), (rsa_public_key, rsa_private_key) = get_keys()

def encrypt_and_serialize_amounts(public_key, amounts):
    encrypted_amounts = encrypt_list(public_key, amounts)
    print("encrypted_amounts", encrypted_amounts)

    # Serialize the list of encrypted amounts
    serialized_encrypted_amounts = serialize_encrypted_list(encrypted_amounts)
    return serialized_encrypted_amounts

def read_and_prepare_excel(file_name, sheet_name, columns_to_hash, hashed_column_name):
    df = read_excel_file(file_name, sheet_name)
    print("DataFrame columns:", df.columns)
    print("DataFrame contents:\n", df)
    df = generate_and_add_hashes(df, columns_to_hash, hashed_column_name, generate_hashes)
    return df

def update_and_write_excel(df, file_name, sheet_name, updates):
    for column_name, data in updates.items():
        df = update_column(df, column_name, data)
    write_to_excel(df, file_name, sheet_name)
    print(f"Results written to {file_name} in columns {', '.join(updates.keys())}")

def decrypt_and_compare_sums(public_key, serialized_encrypted_amounts, original_amounts):
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")
    encrypted_amounts_restored = deserialize_encrypted_list(public_key, serialized_encrypted_amounts)
    print("Deserialized:", encrypted_amounts_restored)
    original_sum = sum(original_amounts)
    encrypted_original_sum = public_key.encrypt(original_sum)
    encrypted_total_sum = sum(encrypted_amounts_restored)
    print("Encrypted original sum:", encrypted_original_sum)
    print("Total of encrypted amounts:", encrypted_total_sum)
    
    # Generate ZKP
    proof, encrypted_r = generate_zkp(rsa_public_key, encrypted_original_sum, encrypted_total_sum)
    
    # Serialize the encrypted sums and proof
    serialized_encrypted_original_sum = serialize_encrypted_list([encrypted_original_sum])
    serialized_encrypted_total_sum = serialize_encrypted_list([encrypted_total_sum])
    serialized_proof = serialize_encrypted_list([proof])
    serialized_encrypted_r = serialize_encrypted_list([encrypted_r])
    
    # Print the serialized encrypted sums and proof
    print("Serialized Encrypted Original Sum:", serialized_encrypted_original_sum)
    print("Serialized Encrypted Total Sum:", serialized_encrypted_total_sum)
    print("Serialized Proof:", serialized_proof)
    print("Serialized Encrypted R:", serialized_encrypted_r)

    # Verify the ZKP
    is_valid = verify_zkp(rsa_private_key, proof, encrypted_r)
    
    print("Original amounts:", original_amounts)
    print("Encrypted amounts:", encrypted_amounts_restored)
    print("Sum of original amounts:", original_sum)
    # print("Encrypted original sum:", encrypted_original_sum)
    # print("Total of encrypted amounts:", encrypted_total_sum)
    print("Proof:", proof)
    print("Encrypted R:", encrypted_r)
    print("ZKP is valid:", is_valid)
    
    if is_valid:
        print("The homomorphic encryption and ZKP worked correctly!")
    else:
        print("There seems to be an issue with the homomorphic encryption or ZKP.")
    
    return {
        'homomorphic_original_sum': [encrypted_original_sum] * len(original_amounts),
        'homomorphic_total_sum': [encrypted_total_sum] * len(original_amounts),
    }

def main():
    df = read_and_prepare_excel(EXCEL_FILE_NAME, SHEET_NAME, COLUMNS_TO_HASH, HASHED_COLUMN_NAME)
    
    if AMOUNT_COLUMN in df.columns and not df.empty:
        product_amounts = df[AMOUNT_COLUMN].tolist()
    else:
        print(f"The column '{AMOUNT_COLUMN}' does not exist or the Excel file is empty. Using dummy array.")
        product_amounts = [10, 20, 30, 40, 50]  # Dummy array

    print("product_amounts:", product_amounts)
    
    serialized_encrypted_amounts = encrypt_and_serialize_amounts(he_public_key, product_amounts)
    # Print the serialized results
    print("Serialized encrypted amounts:", serialized_encrypted_amounts)
    
    df = update_column(df, HE_COLUMN_NAME, serialized_encrypted_amounts)
    # write_to_excel(df, EXCEL_FILE_NAME, SHEET_NAME)
    print(f"Encrypted amounts written to {EXCEL_FILE_NAME} in column '{HE_COLUMN_NAME}'")
    
    updates = decrypt_and_compare_sums(he_public_key, serialized_encrypted_amounts, product_amounts)
    # update_and_write_excel(df, EXCEL_FILE_NAME, SHEET_NAME, updates)

if __name__ == "__main__":
    main()
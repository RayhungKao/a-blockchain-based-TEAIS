# a-blockchain-based-TEAIS

## Setup Instructions

1. **Create a virtual environment**:
    ```sh
    python3.12 -m venv .venv
    ```

2. **Activate the virtual environment**:
    ```sh
    source .venv/bin/activate
    ```

3. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Copy the `.env.sample` file to create a `.env` file**:
    ```sh
    cp .env.sample .env
    ```

5. **Open the `.env` file and replace the placeholder values with your actual keys**:
    ```properties
    PUBLIC_KEY_N='your_public_key_n_here'
    PRIVATE_KEY_P='your_private_key_p_here'
    PRIVATE_KEY_Q='your_private_key_q_here'
    ```

6. **Run the main Python file**:
    ```sh
    python3 main.py
    ```

7. **Deactivate the virtual environment**:
    ```sh
    deactivate
    ```
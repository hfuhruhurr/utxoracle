import os
import subprocess
import sys

def get_cli_options() -> list[str]:
    # Get the CLI options.
    options = []
    options.append(f"-rpcconnect={os.getenv("RPC_CONNECT")}")
    options.append(f"-rpcport={os.getenv("RPC_PORT")}")
    options.append(f"-rpcuser={os.getenv("RPC_USER")}")
    options.append(f"-rpcpassword={os.getenv("RPC_PASSWORD")}")
    
    return options 

def ask_node(command: list[str]) -> None:
    # Build the text of the command to be run.
    bitcoin_cli_options = get_cli_options()
    full_command = ["bitcoin-cli"] + bitcoin_cli_options + command
    
    print(f"Issuing bitcoin-cli command: {command}")
    try:
        response = subprocess.check_output(full_command)
        return response.decode().strip()
    except Exception as e:
        print("Error connecting to your node. Troubleshooting steps:\n")
        print("\t1) Make sure bitcoin-cli is working: try 'bitcoin-cli getblockcount'")
        print("\t2) Make sure bitcoind is running (and server=1 in bitcoin.conf)")
        print("\t3) If needed, set rpcuser/rpcpassword or point to the .cookie file")
        print("\nThe full command was:", " ".join(full_command))
        print("\nThe error from bitcoin-cli was:\n", e)
        sys.exit()

if __name__ == '__main__':
    print('-' * 80)
    print('Let\'s go!')
    block_hash = ask_node(['getblockhash', '777777'])
    response = ask_node(['getblockheader', block_hash, 'true'])
    print(f"type: {type(response)}")
    print(response)
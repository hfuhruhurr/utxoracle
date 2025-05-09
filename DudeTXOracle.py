import os
import subprocess
import sys

def issue_cli_command(command: list[str]) -> None:
    print("Issuing cli command...")
    # Build CLI options if specified in conf file
    bitcoin_cli_options = []
    bitcoin_cli_options.append(f"-rpcconnect={os.getenv("RPC_CONNECT")}")
    bitcoin_cli_options.append(f"-rpcport={os.getenv("RPC_PORT")}")
    bitcoin_cli_options.append(f"-rpcuser={os.getenv("RPC_USER")}")
    bitcoin_cli_options.append(f"-rpcpassword={os.getenv("RPC_PASSWORD")}")
    
    full_command = ["bitcoin-cli"] + bitcoin_cli_options + command

    try:
        response = subprocess.check_output(full_command)
        #subprocess.run('echo "\\033]0;UTXOracle\\007"', shell=True)
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
    block_hash = issue_cli_command(['getblockhash', '777777'])
    response = issue_cli_command(['getblockheader', block_hash, 'true'])
    print(f"type: {type(response)}")
    print(response)
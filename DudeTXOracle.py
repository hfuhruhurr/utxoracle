import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
import json 


NUM_BLOCKS_FOR_CONSENSUS = 6

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
    
    # print(f"Issuing bitcoin-cli command: {command}")
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
    print('-' * 80)

    # -------------------------------------------------------------------------
    # Part 3: Get the latest consensus block to determine the latest price
    #         we can use.
    #
    #         We define "latest" as one day before the consensus block.
    # -------------------------------------------------------------------------
    print("Part 3...")
    consensus_block_height = int(ask_node(['getblockcount'])) - NUM_BLOCKS_FOR_CONSENSUS
    consensus_block_hash = ask_node(['getblockhash', str(consensus_block_height)])
    consensus_block_header = json.loads(ask_node(['getblockheader', consensus_block_hash, 'true']))
    consensus_datetime = datetime.fromtimestamp(consensus_block_header['time'], tz=timezone.utc)
    consensus_midnight = consensus_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    latest_price_datetime = consensus_datetime - timedelta(days=1)

    # print(f"    consensus_block_height: {consensus_block_height}")
    # print(f"    consensus_block_hash  : {consensus_block_hash}")
    # print(f"    consensus_block_header: {consensus_block_header}")
    # print(f"    consensus_datetime    : {consensus_datetime}")
    # print(f"    consensus_midnight    : {consensus_midnight}")
    # print(f"    latest_price_datetime : {latest_price_datetime}")
    
    # -------------------------------------------------------------------------
    # Part 4: If the user supplied a data argument, proccess it.
    # -------------------------------------------------------------------------
    print("Part 4...")

    print(datetime(2025, 5, 8, 0, 0, 0, tzinfo=timezone.utc))
    print(datetime(2025, 5, 8, 0, 0, 0, tzinfo=timezone.utc).timestamp())
    print(consensus_midnight)
    print(consensus_midnight - timedelta(days=1))

    print('-' * 80)
    print('Done!')
    print('-' * 80)
    
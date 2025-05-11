import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
import json 


NUM_BLOCKS_FOR_CONSENSUS = 6
EXPECTED_BLOCKS_PER_DAY = 144

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

def get_block_time(height: int) -> int:
    block_hash = ask_node(['getblockhash', str(height)])
    block_header = ask_node(['getblockheader', block_hash, 'true'])
    block_header = json.loads(block_header)

    return block_header['time']

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
    consensus_block_ts = datetime.fromtimestamp(get_block_time(consensus_block_height), tz=timezone.utc)
    consensus_block_midnight = consensus_block_ts.replace(hour=0, minute=0, second=0, microsecond=0)
    latest_price_datetime = consensus_block_ts - timedelta(days=1)

    print(f"    consensus_block_height  : {consensus_block_height}")
    # print(f"    consensus_block_hash    : {consensus_block_hash}")
    # print(f"    consensus_block_header  : {consensus_block_header}")
    print(f"    consensus_block_ts      : {consensus_block_ts}")
    print(f"    consensus_block_midnight: {consensus_block_midnight}")
    # print(f"    latest_price_datetime   : {latest_price_datetime}")
    
    # -------------------------------------------------------------------------
    # Part 4: If the user supplied a data argument, proccess it.
    # -------------------------------------------------------------------------
    print("Part 4...")

    # if there is no specified cli date argument then...
    target_date = consensus_block_midnight - timedelta(1)
    target_date = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    # if there is a cli date argument then...
    # split on "/" since it's entered as YYYY/MM/DD
    # target_date = datetime(YYYY, MM, DD, 0, 0, 0, timezone.utc)
    # must pass two checks:
    #   1. target_date < consensus_midnight 
    #      (confusing explanation: "Date is after the latest avaiable. We need 6 blocks after UTC midnight.")
    #   2. target_date >= 2023/12/15
    # otherwise, print error message and abort

    print(f"    target_date: {target_date}")
    # -------------------------------------------------------------------------
    # Part 5: Find all blocks on the target day (or in the last 144 blocks)
    # -------------------------------------------------------------------------
    print("Part 5...")
    
    def find_first_block_of_day(target_date: datetime, max_block_height: int) -> int:
        buffer = 10
        n_rpc_calls = 0

        target_ts = int(target_date.timestamp())
        current_ts = get_block_time(max_block_height)

        # Estimate starting block based on 10-minute block time
        blocks_diff = (current_ts - target_ts) // 600  # Approx blocks in 10-min intervals
        est_height = max(1, max_block_height - blocks_diff)

        # print(f"    target_ts : {target_ts}")
        # print(f"    current_ts: {current_ts}")
        # print(f"    est_height: {est_height}")

        # Binary search with buffer to account for block time variance
        low = max(1, est_height - buffer)
        high = min(max_block_height, est_height + buffer)
        first_block = None

        while low <= high:
            mid = (low + high) // 2
            block_ts = get_block_time(mid)
            n_rpc_calls += 2    

            if target_ts <= block_ts < target_ts + 86400:
                first_block = mid
                high = mid - 1
            elif block_ts < target_ts:
                low = mid + 1
            else:
                high = mid - 1

        return first_block, n_rpc_calls
        
    fbod, n_rpc_calls = find_first_block_of_day(target_date, consensus_block_height)
    print(f"    fbod: {fbod}")
    print(f"    n_rpc_calls: {n_rpc_calls}")

    # -------------------------------------------------------------------------
    # Part 6:
    # -------------------------------------------------------------------------
    # print("Part 6...")
    
    # -------------------------------------------------------------------------
    # Part 7:
    # -------------------------------------------------------------------------
    # print("Part 7...")
    
    # -------------------------------------------------------------------------
    # Part 8:
    # -------------------------------------------------------------------------
    # print("Part 8...")
    
    # -------------------------------------------------------------------------
    # Part 9:
    # -------------------------------------------------------------------------
    # print("Part 9...")
    
    # -------------------------------------------------------------------------
    # Part 10.1:
    # -------------------------------------------------------------------------
    # print("Part 10.1...")
    
    # -------------------------------------------------------------------------
    # Part 10.2:
    # -------------------------------------------------------------------------
    # print("Part 10.2...")
    
    # -------------------------------------------------------------------------
    # Part 11:
    # -------------------------------------------------------------------------
    # print("Part 11...")
    
    # -------------------------------------------------------------------------
    # Part 12:
    # -------------------------------------------------------------------------
    # print("Part 12...")
    
    
    print('-' * 80)
    print('Done!')
    print('-' * 80)
    
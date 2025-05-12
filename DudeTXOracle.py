import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
import json 
import paramiko  # Part 6
from typing import List

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

    print("Part 1...")
    data_dir = '/home/umbrel/umbrel/app-data/bitcoin-knots/data/bitcoin/'
    blocks_dir = os.path.join(data_dir, "blocks")
    print(f"    data_dir  : {data_dir}")
    print(f"    blocks_dir: {blocks_dir}")
    
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

    # print(f"    consensus_block_height  : {consensus_block_height}")
    # print(f"    consensus_block_hash    : {consensus_block_hash}")
    # print(f"    consensus_block_header  : {consensus_block_header}")
    # print(f"    consensus_block_ts      : {consensus_block_ts}")
    # print(f"    consensus_block_midnight: {consensus_block_midnight}")
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

    # print(f"    target_date: {target_date}")
    # -------------------------------------------------------------------------
    # Part 5: Find all blocks on the target day (or in the last 144 blocks)
    # -------------------------------------------------------------------------
    print("Part 5...")
    
    def check_fbod(fbod):
        print(f"    fbod           : {fbod}")
        print(f"    fbod (date)    : {datetime.fromtimestamp(get_block_time(fbod), tz=timezone.utc)}")
        print(f"    fbod - 1 (date): {datetime.fromtimestamp(get_block_time(fbod - 1), tz=timezone.utc)}")

    def find_first_block_of_day(target_date: datetime, max_block_height: int) -> int:
        # TODO: binary search is slower, not faster

        buffer = 500
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
        
    def same_day(dt1: datetime, dt2: datetime) -> bool:
        return dt1.date() == dt2.date()
    
    def find_last_block_of_day(target_date: datetime, first_block: int) -> int:
        jump = 100  # Assume at least 100 blocks in a day
        block = first_block + jump  
        block_dt = datetime.fromtimestamp(get_block_time(block), tz=timezone.utc)
        
        i = 1
        while same_day(target_date, block_dt):
            print(f"    block: {block} @ {block_dt} {i}")
            # Trying to be smart about which block to check next.
            if block_dt.hour < 22:
                jump = (23 - block_dt.hour) * 5
            elif block_dt.hour == 22:
                jump = 4
            else:
                jump = 1
            block += jump
            i += 1
            block_dt = datetime.fromtimestamp(get_block_time(block), tz=timezone.utc)
        
        return block - 1
    
    fbod, n_rpc_calls = find_first_block_of_day(target_date, consensus_block_height)
    check_fbod(fbod)
    print(f"    n_rpc_calls: {n_rpc_calls}")
    lbod = find_last_block_of_day(target_date, fbod)
    print(f"    lbod: {lbod}")

    # -------------------------------------------------------------------------
    # Part 6:
    # -------------------------------------------------------------------------
    sys.exit()
    print("Part 6...")
    
    def get_block_files(blocks_dir: str) -> List[str]:
        # SSH connection details
        host = os.getenv("UMBREL_HOST_IP")
        username = os.getenv("UMBREL_USER")
        password = os.getenv("UMBREL_PASSWORD")

        if not all([host, username, password]):
            raise ValueError("Missing environment variables: UMBREL_HOST_IP, UMBREL_USER, or UMBREL_PASSWORD")

        # Establish SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username=username, password=password)
            # Use SFTP to list remote directory
            sftp = ssh.open_sftp()
            try:
                block_files = sorted(
                    [f for f in sftp.listdir(blocks_dir) if f.startswith('blk') and f.endswith('.dat')],
                    key=lambda f: int(f[3:8])
                )
            except FileNotFoundError:
                print(f"Directory {blocks_dir} not found on {host}")
                block_files = []
            sftp.close()
        except paramiko.SSHException as e:
            print(f"SSH connection failed: {e}")
            block_files = []
        finally:
            ssh.close()

        return block_files

    get_block_files(blocks_dir)
    
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
    
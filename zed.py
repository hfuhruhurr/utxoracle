# from datetime import datetime, timedelta, timezone
import datetime
import json
import os
import platform
import subprocess
import sys
import warnings
from hashlib import sha256
from typing import Dict, List, Tuple


def part_1a_process_args() -> Tuple[str, str]:
    print("Starting Part 1a, processing arguments...")
    date_mode = True
    date_entered = ""

    # print help text for the user if needed
    def print_help():
        help_text = """
        Usage: python script.py [options]

        Options:
          -h               Show this help message
          -d YYYY/MM/DD    Specify a UTC date to evaluate
          -p /path/to/dir  Specify the data directory for blk files
          -rb              Use last 144 recent blocks instead of date mode
        """
        print(help_text)
        sys.exit(0)

    # did use ask for help
    if "-h" in sys.argv:
        print_help()

    # did user specify a date?
    if "-d" in sys.argv:
        h_index = sys.argv.index("-d")
        if h_index + 1 < len(sys.argv):
            date_entered = sys.argv[h_index + 1]

    # did user specify a data path?
    if "-p" in sys.argv:
        d_index = sys.argv.index("-p")
        if d_index + 1 < len(sys.argv):
            data_dir = sys.argv[d_index + 1]

    # did user specify blocks instead of a date?
    if "-rb" in sys.argv:
        date_mode = False

    run_mode = "date" if date_mode else "block"

    print("  Returning:")
    print(f"    run_mode ({run_mode}) and date_entered ({date_entered})...")
    return run_mode, date_entered


def part_1b_initializing() -> Tuple[str, str, List[str]]:
    print("Starting Part 1b, initializing...")

    # print the current version and disable warnings
    print("  UTXOracle version 9.0")
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # set platform dependent data paths and clear terminal
    data_dir = []
    system = platform.system()
    if system == "Darwin":  # macOS
        data_dir = os.path.expanduser("~/Library/Application Support/Bitcoin")
        # os.system('clear')
    elif system == "Windows":
        data_dir = os.path.join(os.environ.get("APPDATA", ""), "Bitcoin")
        # os.system('cls')
    else:  # Linux or others
        data_dir = os.path.expanduser("~/.bitcoin")
        # os.system('clear')

    if True:  # True whilst testing
        blocks_dir = os.path.join(data_dir, "blocks")
        bitcoin_cli_options = []
        print("  Returning:")
        print(f"    data_dir     :{data_dir}")
        print(f"    blocks_dir   :{blocks_dir}")
        print(f"    bcli_options :{bitcoin_cli_options}")
        bitcoin_cli_options = []
        return data_dir, blocks_dir, bitcoin_cli_options
    else:
        # initialize variables for blocks and dates
        # block_start_num = 0
        # block_finish_num = 0
        # block_nums_needed = []
        # block_hashes_needed = []
        # block_times_needed = []

        # Validate bitcoin.conf in data_dir
        conf_path = os.path.join(data_dir, "bitcoin.conf")
        if not os.path.exists(conf_path):
            print(f"Invalid Bitcoin data directory: {data_dir}")
            print("Expected to find 'bitcoin.conf' in this directory.")
            sys.exit(1)

        # parse the conf file for the blocks dir and rpc credentials
        conf_path = os.path.join(data_dir, "bitcoin.conf")
        conf_settings = {}
        if os.path.exists(conf_path):
            with open(conf_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        conf_settings[key.strip()] = value.strip().strip('"')

        # Set blocks directory from default or user specified
        blocks_dir = os.path.expanduser(
            conf_settings.get("blocksdir", os.path.join(data_dir, "blocks"))
        )

        # Build CLI options if specified in conf file
        bitcoin_cli_options = []
        if "rpcuser" in conf_settings and "rpcpassword" in conf_settings:
            bitcoin_cli_options.append(f"-rpcuser={conf_settings['rpcuser']}")
            bitcoin_cli_options.append(f"-rpcpassword={conf_settings['rpcpassword']}")
        else:
            cookie_path = conf_settings.get(
                "rpccookiefile", os.path.join(data_dir, ".cookie")
            )
            if os.path.exists(cookie_path):
                bitcoin_cli_options.append(f"-rpccookiefile={cookie_path}")

        for opt in ["rpcconnect", "rpcport"]:
            if opt in conf_settings:
                bitcoin_cli_options.append(f"-{opt}={conf_settings[opt]}")

    return data_dir, blocks_dir, bitcoin_cli_options


def part_2_ask_node(bitcoin_cli_options: List[str], command) -> bytes:
    print("Starting Part 2, asking node for data...")
    # full_command = ["bitcoin-cli"] + bitcoin_cli_options + command

    print("  Returning:")
    print(f"    subprocess output byte string")

    # try:
    #     rv = subprocess.check_output(full_command)
    #     #subprocess.run('echo "\\033]0;UTXOracle\\007"', shell=True)
    #     return rv
    # except Exception as e:
    #     print("Error connecting to your node. Troubleshooting steps:\n")
    #     print("\t1) Make sure bitcoin-cli is working: try 'bitcoin-cli getblockcount'")
    #     print("\t2) Make sure bitcoind is running (and server=1 in bitcoin.conf)")
    #     print("\t3) If needed, set rpcuser/rpcpassword or point to the .cookie file")
    #     print("\nThe full command was:", " ".join(full_command))
    #     print("\nThe error from bitcoin-cli was:\n", e)
    #     sys.exit()


def part_3_get_consensus_block_timestamp() -> datetime:
    print("Starting Part 3, getting the timestamp of the consensus block...")
    # # Doing a lot of shit when you really only need the timestamp
    # # of the consensus block
    # block_count = int(part_2_ask_node(["getblockcount"]))
    # consensus_block = block_count - 6

    # # get block header from current block height
    # consensus_block_hash = (
    #     part_2_ask_node(["getblockhash", str(consensus_block)]).decode().strip()
    # )
    # consensus_block_header = json.loads(
    #     part_2_ask_node(["getblockheader", consensus_block_hash, "true"])
    # )

    # # get the date and time of the current block height
    # consensus_block_timestamp = datetime.fromtimestamp(
    #     consensus_block_header["time"],
    #     tz=datetime.UTC,
    # )

    # # get the date/time of utc midnight on the latest day
    # latest_year = int(time_datetime.strftime("%Y"))
    # latest_month = int(time_datetime.strftime("%m"))
    # latest_day = int(time_datetime.strftime("%d"))
    # latest_utc_midnight = datetime(
    #     latest_year, latest_month, latest_day, 0, 0, 0, tzinfo=timezone.utc
    # )

    # # assign the day before as the latest possible price date
    # seconds_in_a_day = 60 * 60 * 24
    # yesterday_seconds = latest_time_in_seconds - seconds_in_a_day
    # latest_price_day = datetime.fromtimestamp(yesterday_seconds, tz=timezone.utc)
    # latest_price_date = latest_price_day.strftime("%Y-%m-%d")

    # # print completion update
    # print("5% done", flush=True)

    consensus_block_timestamp = datetime.datetime(
        2025, 9, 3, 12, 24, 0, tzinfo=datetime.UTC
    )
    print("  Returning:")
    print(f"    Timestamp of consensus block: {consensus_block_timestamp}.")

    return consensus_block_timestamp


def part_4_set_target_date(run_mode, target_date) -> datetime:
    print("Starting Part 4...")
    print(f"  Run mode: {run_mode}")
    print(f"  Date entered: {target_date}")
    if run_mode == "date":
        print("  Date mode is enabled...set target date to most recent price date")
    else:
        print(
            "  Date mode is disabled...check the entered date is sufficiently in the past."
        )
        print(
            "  Date mode is disabled...check the entered date is sufficiently recent."
        )
    print("  Returning:")
    target_date = datetime.datetime(2025, 5, 22, tzinfo=datetime.UTC)
    print(f"    Target date: {target_date}.")

    ###############################################################################
    # Part 4) Check that the date entered is an acceptable date
    ###############################################################################

    # if date_mode:
    #     # run latest day if hit enter
    #     if date_entered == "":
    #         datetime_entered = latest_utc_midnight + timedelta(days=-1)

    #     # user entered a specific date
    #     else:
    #         # check to see if this is a good date
    #         try:
    #             year = int(date_entered.split("/")[0])
    #             month = int(date_entered.split("/")[1])
    #             day = int(date_entered.split("/")[2])

    #             # make sure this date is less than the max date
    #             datetime_entered = datetime(
    #                 year, month, day, 0, 0, 0, tzinfo=timezone.utc
    #             )
    #             if datetime_entered.timestamp() >= latest_utc_midnight.timestamp():
    #                 print(
    #                     "\nDate is after the latest avaiable. We need 6 blocks after UTC midnight."
    #                 )
    #                 print("Run UTXOracle.py -rb for the most recent blocks")

    #                 sys.exit()

    #             # make sure this date is after the min date
    #             dec_15_2023 = datetime(2023, 12, 15, 0, 0, 0, tzinfo=timezone.utc)
    #             if datetime_entered.timestamp() < dec_15_2023.timestamp():
    #                 print("\nThe date entered is before 2023-12-15, please try again")
    #                 sys.exit()

    #         except:
    #             print(
    #                 "\nError interpreting date. Please try again. Make sure format is YYYY/MM/DD"
    #             )
    #             sys.exit()

    #     # get the seconds and printable date string of date entered
    #     price_day_seconds = int(datetime_entered.timestamp())
    #     price_day_date_utc = datetime_entered.strftime("%b %d, %Y")
    #     price_date_dash = datetime_entered.strftime("%Y-%m-%d")

    return target_date


def get_block_time(height):
    block_hash_b = part_2_ask_node(["getblockhash", str(height)])
    block_header_b = part_2_ask_node(["getblockheader", block_hash_b[:64], "true"])
    block_header = json.loads(block_header_b)

    return (block_header["time"], block_hash_b[:64].decode())


def part_5_get_target_block_heights(
    run_mode: str, target_date: datetime
) -> Tuple[int, int, List[str]]:
    print("Starting Part 5...")
    print(f"  Run mode: {run_mode}")
    print(f"  Target date: {target_date}")
    if run_mode == "date":
        print("  Date mode is enabled...get all block on target date")
    else:
        print("  Block mode is enabled...get the last 144 blocks")
    print(
        "  Returning start and end target block numbers, as well as their block hashes..."
    )

    target_block_start = 88027
    target_block_end = 88171
    target_block_hashes_needed = []

    # # if block mode add the blocks and hashes to a list
    # if block_mode:
    #     print("\nFinding the last 144 blocks", flush=True)

    #     # get the last block number of the day
    #     block_finish_num = block_count
    #     block_start_num = block_finish_num - 144

    #     # append needed block nums and hashes needed
    #     block_num = block_start_num
    #     time_in_seconds, hash_end = get_block_time(block_start_num)
    #     print_every = 0
    #     while block_num < block_finish_num:
    #         # print update
    #         if (
    #             block_num - block_start_num
    #         ) / 144 * 100 > print_every and print_every < 100:
    #             print(str(print_every) + "%..", end="", flush=True)
    #             print_every += 20
    #         block_nums_needed.append(block_num)
    #         block_hashes_needed.append(hash_end)
    #         block_times_needed.append(time_in_seconds)
    #         block_num += 1
    #         time_in_seconds, hash_end = get_block_time(block_num)

    #     print("100%\t\t\t25% done", flush=True)

    # # if date mode search for all the blocks on this day
    # elif date_mode:
    #     print(
    #         "\nFinding all blocks on " + datetime_entered.strftime("%b %d, %Y"),
    #         flush=True,
    #     )
    #     print("0%..", end="", flush=True)
    #     # first estimate of the block height of the price day
    #     seconds_since_price_day = latest_time_in_seconds - price_day_seconds
    #     blocks_ago_estimate = round(
    #         144 * float(seconds_since_price_day) / float(seconds_in_a_day)
    #     )
    #     price_day_block_estimate = block_count_consensus - blocks_ago_estimate

    #     # check the time of the price day block estimate
    #     time_in_seconds, hash_end = get_block_time(price_day_block_estimate)

    #     # get new block estimate from the seconds difference using 144 blocks per day
    #     print("20%..", end="", flush=True)
    #     seconds_difference = time_in_seconds - price_day_seconds
    #     block_jump_estimate = round(
    #         144 * float(seconds_difference) / float(seconds_in_a_day)
    #     )

    #     # iterate above process until it oscillates around the correct block
    #     last_estimate = 0
    #     last_last_estimate = 0

    #     print("40%..", end="", flush=True)
    #     while block_jump_estimate > 6 and block_jump_estimate != last_last_estimate:
    #         # when we oscillate around the correct block, last_last_estimate = block_jump_estimate
    #         last_last_estimate = last_estimate
    #         last_estimate = block_jump_estimate

    #         # get block header or new estimate
    #         price_day_block_estimate = price_day_block_estimate - block_jump_estimate

    #         # check time of new block and get new block jump estimate
    #         time_in_seconds, hash_end = get_block_time(price_day_block_estimate)
    #         seconds_difference = time_in_seconds - price_day_seconds
    #         block_jump_estimate = round(
    #             144 * float(seconds_difference) / float(seconds_in_a_day)
    #         )

    #     print("60%..", end="", flush=True)
    #     # the oscillation may be over multiple blocks so we add/subtract single blocks
    #     # to ensure we have exactly the first block of the target day
    #     if time_in_seconds > price_day_seconds:
    #         # if the estimate was after price day look at earlier blocks
    #         while time_in_seconds > price_day_seconds:
    #             # decrement the block by one, read new block header, check time
    #             price_day_block_estimate = price_day_block_estimate - 1
    #             time_in_seconds, hash_end = get_block_time(price_day_block_estimate)

    #         # the guess is now perfectly the first block before midnight
    #         price_day_block_estimate = price_day_block_estimate + 1

    #     # if the estimate was before price day look for later blocks
    #     elif time_in_seconds < price_day_seconds:
    #         while time_in_seconds < price_day_seconds:
    #             # increment the block by one, read new block header, check time
    #             price_day_block_estimate = price_day_block_estimate + 1
    #             time_in_seconds, hash_end = get_block_time(price_day_block_estimate)

    #     print("80%..", end="", flush=True)
    #     # assign the estimate as the price day block since it is correct now
    #     price_day_block = price_day_block_estimate

    #     # get the day of the month
    #     time_in_seconds, hash_start = get_block_time(price_day_block)
    #     day1 = get_day_of_month(time_in_seconds)

    #     # get the last block number of the day
    #     price_day_block_end = price_day_block
    #     time_in_seconds, hash_end = get_block_time(price_day_block_end)
    #     day2 = get_day_of_month(time_in_seconds)

    #     print("100%\t\t\t25% done", flush=True)
    #     print("\nDetermining the correct order of blocks", flush=True)

    #     # load block nums and hashes needed
    #     block_num = 0
    #     print_next = 0
    #     while day1 == day2:
    #         # print progress update
    #         block_num += 1
    #         if block_num / 144 * 100 > print_next:
    #             print(str(print_next) + "%..", end="", flush=True)
    #             print_next += 20

    #         # append needed block
    #         block_nums_needed.append(price_day_block_end)
    #         block_hashes_needed.append(hash_end)
    #         block_times_needed.append(time_in_seconds)
    #         price_day_block_end += 1  # assume 30+ blocks this day
    #         time_in_seconds, hash_end = get_block_time(price_day_block_end)
    #         day2 = get_day_of_month(time_in_seconds)

    #     # complete print update status
    #     while print_next < 100:
    #         print(str(print_next) + "%..", end="", flush=True)
    #         print_next += 20

    #     # set start and end block numbers
    #     block_start_num = price_day_block
    #     block_finish_num = price_day_block_end

    #     print("100%\t\t\t50% done", flush=True)

    return target_block_start, target_block_end, target_block_hashes_needed


def sha256d(b: bytes) -> bytes:
    return sha256(sha256(b).digest()).digest()


def part_6_create_target_block_binaries_index(block_hashes_needed: List[str]) -> Dict:
    print("Starting Part 6...")
    print(
        "  For each target date block identified by its block hash, extract data from its binary file:"
    )
    print("    1. binary file name that contains the target block")
    print("    2. byte offset of the target block in the binary file")
    print("    3. size of the target block in bytes")
    print("    4. timestamp of the target block")
    print("  Returning a dictionary of the above data for each target block hash...")

    found_blocks = {}  # what we will return (data from the binaries)

    # ##############################################################################
    # # Part 6) Build a map of the binary block files
    # ##############################################################################

    # # In this section we find the byte-wise location of all the block data
    # # that we need in terms of where it's stored on the user's hard drive
    # print(" Mapping block locations in raw block files", flush=True)

    # # standard variables for block readind and estiamted blocks per binary .blk file
    # blocks_per_file = 50  # generous, likely much more
    # Mainnet_flag = b"\xf9\xbe\xb4\xd9"
    # Header_size = 80

    # # Get all .blk files sorted by index
    # block_hashes_needed = set(block_hashes_needed)
    # found_blocks = {}
    # blk_files = sorted(
    #     [
    #         f
    #         for f in os.listdir(blocks_dir)
    #         if f.startswith("blk") and f.endswith(".dat")
    #     ],
    #     key=lambda f: int(f[3:8]),
    # )

    # # conservatively estimate the first and last blk file needed
    # block_depth_start = block_count_consensus - block_nums_needed[0]
    # last_blk_file_num = int(blk_files[-1][3:8])
    # start_blk_index = (
    #     last_blk_file_num - int(block_depth_start / blocks_per_file + 1) - 1
    # )
    # end_blk_index_est = last_blk_file_num - int(int(block_depth_start / 128))

    # # read a swath of block files looking for the block hashes needeed
    # blk_files = [f for f in blk_files if int(f[3:8]) >= start_blk_index]
    # print_next = 0
    # block_file_num = 0
    # for blk_file in blk_files:
    #     # path to the next blk file
    #     path = os.path.join(blocks_dir, blk_file)

    #     # print progress update
    #     block_file_num += 1
    #     if block_file_num / (end_blk_index_est - start_blk_index) * 100 > print_next:
    #         if print_next < 100:
    #             print(str(print_next) + "%..", end="", flush=True)
    #             print_next += 20

    #     # read the blk file
    #     with open(path, "rb") as f:
    #         while True:
    #             # read the headers to the block
    #             start = f.tell()
    #             magic = f.read(4)
    #             if not magic or len(magic) < 4:
    #                 break
    #             if magic != Mainnet_flag:
    #                 f.seek(start + 1)
    #                 continue
    #             size_bytes = f.read(4)
    #             if len(size_bytes) < 4:
    #                 break
    #             block_size = int.from_bytes(size_bytes, "little")
    #             header = f.read(Header_size)
    #             if len(header) < Header_size:
    #                 break

    #             # read the block hash and time stamp
    #             block_hash = sha256d(header)[::-1]  # big-endian
    #             block_hash_hex = block_hash.hex()
    #             timestamp = int.from_bytes(header[68:72], "little")

    #             # add block to the list if a needed block
    #             if block_hash_hex in block_hashes_needed:
    #                 found_blocks[block_hash] = {
    #                     "file": blk_file,
    #                     "offset": start,
    #                     "block_size": block_size,
    #                     "time": timestamp,
    #                 }
    #                 if len(found_blocks) == len(block_hashes_needed):
    #                     break

    #             # find the next block in the blk file
    #             f.seek(start + 8 + block_size)

    #     # stop if all blocks found
    #     if len(found_blocks) == len(block_hashes_needed):
    #         break

    # # error if all blocks found, if good print progress update
    # if len(found_blocks) != len(block_hashes_needed):
    #     print("Error: Reached end of blk files without finding all target blocks.")
    #     sys.exit()
    # else:
    #     while print_next < 100:
    #         print(str(print_next) + "%..", end="", flush=True)
    #         print_next += 20
    #     print("100% \t\t\t75% done", flush=True)

    return found_blocks


def part_7_build_bins() -> List[float]:
    print("Starting Part 7...")
    print("  Building the logarithmic bins for the utxo amounts distribution...")
    print("  In the exponent range of -6 to 6, with 200 bins per 10x range")
    print("  Returning an indexed list of bins...")

    # Make the first bin 0
    bins = [0.0]

    # Create 200 bins in each 10x range from 1e-6 thru 1e5
    for exponent in range(-6, 6):
        for b in range(0, 200):
            bin_value = 10 ** (exponent + b / 200)
            bins.append(bin_value)

    return bins


def remaining_parts():
    ##############################################################################

    #  Part 8) Get all output amounts from all block on target day

    ##############################################################################

    # This section of the program will take the most time as it requests all
    # blocks from the node on the price day. It readers every transaction (tx)
    # from those blocks and places each tx output value into the bell curve.
    # New in version 8 are filters that disallow the following types of transactions
    # as they have been found to be unlikely to be round p2p usd transactions: coinbase,
    # greater than 5 inputs, greater than 2 outputs, only one output, has op_return,
    # has witness data > 500 bytes, and has an input created on the same day.

    print("\nLoading every transaction from every block", flush=True)

    # shortcut for reading bytes of data from the block file
    import hashlib
    import struct
    from math import log10

    def read_varint(f):
        i = f.read(1)
        if not i:
            return 0
        i = i[0]
        if i < 0xFD:
            return i
        elif i == 0xFD:
            val = struct.unpack("<H", f.read(2))[0]
        elif i == 0xFE:
            val = struct.unpack("<I", f.read(4))[0]
        else:
            val = struct.unpack("<Q", f.read(8))[0]
        return val

    # shortcut for encoding variable size integers to bytes
    from io import BytesIO

    def encode_varint(i: int) -> bytes:
        assert i >= 0
        if i < 0xFD:
            return i.to_bytes(1, "little")
        elif i <= 0xFFFF:
            return b"\xfd" + i.to_bytes(2, "little")
        elif i <= 0xFFFFFFFF:
            return b"\xfe" + i.to_bytes(4, "little")
        else:
            return b"\xff" + i.to_bytes(8, "little")

    # shortcut for computing the txid because blk files don't store txids
    def compute_txid(raw_tx_bytes: bytes) -> bytes:
        stream = BytesIO(raw_tx_bytes)

        # Read version
        version = stream.read(4)

        # Peek at marker/flag to detect SegWit
        marker = stream.read(1)
        flag = stream.read(1)
        is_segwit = marker == b"\x00" and flag == b"\x01"

        if not is_segwit:
            # Legacy tx: rewind and hash full raw tx
            stream.seek(0)
            stripped_tx = stream.read()
        else:
            # Start stripped tx with version
            stripped_tx = bytearray()
            stripped_tx += version

            # Inputs
            input_count = read_varint(stream)
            stripped_tx += encode_varint(input_count)
            for _ in range(input_count):
                stripped_tx += stream.read(32)  # prev txid
                stripped_tx += stream.read(4)  # vout index
                script_len = read_varint(stream)
                stripped_tx += encode_varint(script_len)
                stripped_tx += stream.read(script_len)
                stripped_tx += stream.read(4)  # sequence

            # Outputs
            output_count = read_varint(stream)
            stripped_tx += encode_varint(output_count)
            for _ in range(output_count):
                stripped_tx += stream.read(8)  # value
                script_len = read_varint(stream)
                stripped_tx += encode_varint(script_len)
                stripped_tx += stream.read(script_len)

            # Skip witness data
            for _ in range(input_count):
                stack_count = read_varint(stream)
                for _ in range(stack_count):
                    item_len = read_varint(stream)
                    stream.read(item_len)

            # Locktime
            stripped_tx += stream.read(4)

        return hashlib.sha256(hashlib.sha256(stripped_tx).digest()).digest()[::-1]

    # initialize output lists and variables
    from struct import unpack

    todays_txids = set()
    raw_outputs = []
    block_heights_dec = []
    block_times_dec = []
    print_next = 0
    block_num = 0

    # loop through all found blocks
    for block_hash, meta in found_blocks.items():
        # init variables for next block
        block_num += 1
        num_block_txs = 0
        txs_to_add = []

        # print progress update
        if block_num / len(block_nums_needed) * 100 > print_next:
            print(str(print_next) + "%..", end="", flush=True)
            print_next += 20

        # get the location of the block on the hard drive
        file_path = os.path.join(blocks_dir, meta["file"])
        with open(file_path, "rb") as f:
            # get tx count in this block
            f.seek(meta["offset"])
            f.read(8)  # skip magic + block size
            f.read(80)  # skip block header
            tx_count = read_varint(f)

            # loop through all transactions
            for tx_index in range(tx_count):
                num_block_txs += 1

                # read tx version type
                start_tx = f.tell()
                version = f.read(4)

                # Segwit check
                marker_flag = f.read(2)
                is_segwit = marker_flag == b"\x00\x01"
                if not is_segwit:
                    f.seek(start_tx + 4)  # rewind if legacy

                # read input count
                input_count = read_varint(f)
                inputs = []
                has_op_return = False
                witness_exceeds = False
                is_coinbase = False
                input_txids = []

                # loop through inputs
                for _ in range(input_count):
                    prev_txid = f.read(32)
                    prev_index = f.read(4)
                    script_len = read_varint(f)
                    script = f.read(script_len)
                    f.read(4)  # sequence

                    # add input txids to a list
                    input_txids.append(prev_txid[::-1].hex())

                    # check for coinbase tx
                    if prev_txid == b"\x00" * 32 and prev_index == b"\xff\xff\xff\xff":
                        is_coinbase = True

                    # add input scripts to a list
                    inputs.append({"script": script})

                # read number of outputs
                output_count = read_varint(f)
                output_values = []

                # loop through outputs
                for _ in range(output_count):
                    value_sats = unpack("<Q", f.read(8))[0]
                    script_len = read_varint(f)
                    script = f.read(script_len)

                    # check for op_returns
                    if script and script[0] == 0x6A:  # OP_RETURN in output
                        has_op_return = True

                    # check for amount out of range
                    value_btc = value_sats / 1e8
                    if 1e-5 < value_btc < 1e5:
                        output_values.append(value_btc)

                # if segqt, check witness data
                if is_segwit:
                    for input_data in inputs:
                        stack_count = read_varint(f)
                        total_witness_len = 0
                        for _ in range(stack_count):
                            item_len = read_varint(f)
                            total_witness_len += item_len
                            f.read(item_len)
                            if item_len > 500:
                                witness_exceeds = True

                        # check it witness data larger than reasonable
                        if total_witness_len > 500:
                            witness_exceeds = True

                # calculate the TXID of this transaction and add it to list
                f.read(4)
                end_tx = f.tell()
                f.seek(start_tx)
                raw_tx = f.read(end_tx - start_tx)
                txid = compute_txid(raw_tx)
                todays_txids.add(txid.hex())

                # check for same day input re-use
                is_same_day_tx = False
                for itxid in input_txids:
                    if itxid in todays_txids:
                        is_same_day_tx = True

                # === Final inclusion check ===
                if (
                    input_count <= 5
                    and output_count == 2
                    and not is_coinbase
                    and not has_op_return
                    and not witness_exceeds
                ) and not is_same_day_tx:
                    # add all outputs to the bell curve
                    for amount in output_values:
                        # find the right output amount bin to increment
                        amount_log = log10(amount)
                        percent_in_range = (
                            amount_log - first_bin_value
                        ) / range_bin_values
                        bin_number_est = int(percent_in_range * number_of_bins)

                        # double check exact right bin (won't be less than)
                        while output_bell_curve_bins[bin_number_est] <= amount:
                            bin_number_est += 1
                        bin_number = bin_number_est - 1

                        # add this output to the bell curve
                        output_bell_curve_bin_counts[bin_number] += 1.0

                        # add the output to this block's output list
                        txs_to_add.append(amount)

        # add the block's output list to the total output list
        if len(txs_to_add) > 0:
            block_dec_inc = 1 / len(txs_to_add)
            bkh = block_nums_needed[block_num - 1]
            tm = block_times_needed[block_num - 1]
            for amt in txs_to_add:
                raw_outputs.append(amt)
                block_heights_dec.append(bkh)
                block_times_dec.append(tm)

    print("100% \t\t\t95% done", flush=True)

    ##############################################################################

    #  Part 9) Remove non-usd related outputs from the bell curve

    ##############################################################################

    # This section aims to remove non-usd denominated samples from the bell curve
    # of outputs. The two primary steps are to remove very large/small outputs
    # and then to remove round btc amounts. We don't set the round btc amounts
    # to zero because if the USD price of bitcoin is also round, then round
    # btc amounts will co-align with round usd amounts. There are many ways to deal
    # with this. One way we've found to work is to smooth over the round btc amounts
    # using the neighboring amounts in the bell curve. The last step is to normalize
    # the bell curve. Normalizing is done by dividing the entire curve by the sum
    # of the curve. This is done because it's more convenient for signal processing
    # procedures if the sum of the signal integrates to one.

    # print update
    print("\nFinding prices and rendering plot", flush=True)
    print("0%..", end="", flush=True)

    # remove outputs below 10k sat (increased from 1k sat in v6)
    for n in range(0, 201):
        output_bell_curve_bin_counts[n] = 0

    # remove outputs above ten btc
    for n in range(1601, len(output_bell_curve_bin_counts)):
        output_bell_curve_bin_counts[n] = 0

    # create a list of round btc bin numbers
    round_btc_bins = [
        201,  # 1k sats
        401,  # 10k
        461,  # 20k
        496,  # 30k
        540,  # 50k
        601,  # 100k
        661,  # 200k
        696,  # 300k
        740,  # 500k
        801,  # 0.01 btc
        861,  # 0.02
        896,  # 0.03
        940,  # 0.04
        1001,  # 0.1
        1061,  # 0.2
        1096,  # 0.3
        1140,  # 0.5
        1201,  # 1 btc
    ]

    # smooth over the round btc amounts
    for r in round_btc_bins:
        amount_above = output_bell_curve_bin_counts[r + 1]
        amount_below = output_bell_curve_bin_counts[r - 1]
        output_bell_curve_bin_counts[r] = 0.5 * (amount_above + amount_below)

    # get the sum of the curve
    curve_sum = 0.0
    for n in range(201, 1601):
        curve_sum += output_bell_curve_bin_counts[n]

    # normalize the curve by dividing by it's sum and removing extreme values
    for n in range(201, 1601):
        output_bell_curve_bin_counts[n] /= curve_sum

        # remove extremes (0.008 chosen by historical testing)
        if output_bell_curve_bin_counts[n] > 0.008:
            output_bell_curve_bin_counts[n] = 0.008

    # print update
    print("20%..", end="", flush=True)

    ##############################################################################

    #  Part 8) Construct the USD price finder stencils

    ##############################################################################

    # We now have a bell curve of outputs which should contain round USD outputs
    # as it's prominent features. To expose these prominent features more,
    # and estimate a usd price, we slide two types of stencils over the bell curve and look
    # for where the slide location is maximized. There are several stencil designs
    # and maximization strategies which could accomplish this. The one used here
    # is to have one smooth stencil that finds the general shape of a typical output
    # distribution day, and a spike stencil which narrows in on exact locations
    # of the round USD amounts. Both the smooth and spike stenciled have been created
    # by an iterative process of manually sliding together round USD spikes in
    # output distribtutions over every day from 2020 to 2024, and then taking the average
    # general shape and round usd spike values over that period.

    # Load the average smooth stencil to align broadly with a typical output day
    #
    #                       *  *
    #                    *         *
    #                 *               *
    #              *                     *
    #            *                          *
    #          *                               *
    #        *                                     *
    #      *                                            *
    #   10k sats        0.01 btc           1 btc        10btc

    # Parameters
    num_elements = 803
    mean = 411  # (num_elements - 1) / 2  # Center of the array
    std_dev = 201

    # contstruct the smooth stencil
    smooth_stencil = []
    for x in range(num_elements):
        exp_part = -((x - mean) ** 2) / (2 * (std_dev**2))
        smooth_stencil.append((0.00150 * 2.718281828459045**exp_part) + (0.0000005 * x))

    # Load the spike stencil that fine tunes the alignment on popular usd amounts
    #
    #                         *
    #                     *   *
    #                     *   *
    #                *    *   *          *
    #           *    *    *   *    *     *
    #           *    *    *   *    *     *    *
    #       *   *    *    *   *    *     *    *     *
    #       *   *    *    *   *    *     *    *     *
    #      $1 $10  $20  $50  $100  $500  $1k  $2k   $10k

    spike_stencil = []
    for n in range(0, 803):
        spike_stencil.append(0.0)

    # round usd bin location   #popularity    #usd amount
    spike_stencil[40] = 0.001300198324984352  # $1
    spike_stencil[141] = 0.001676746949820743  # $5
    spike_stencil[201] = 0.003468805546942046  # $10
    spike_stencil[202] = 0.001991977522512513  #
    spike_stencil[236] = 0.001905066647961839  # $15
    spike_stencil[261] = 0.003341772718156079  # $20
    spike_stencil[262] = 0.002588902624584287  #
    spike_stencil[296] = 0.002577893841190244  # $30
    spike_stencil[297] = 0.002733728814200412  #
    spike_stencil[340] = 0.003076117748975647  # $50
    spike_stencil[341] = 0.005613067550103145  #
    spike_stencil[342] = 0.003088253178535568  #
    spike_stencil[400] = 0.002918457489366139  # $100
    spike_stencil[401] = 0.006174500465286022  #
    spike_stencil[402] = 0.004417068070043504  #
    spike_stencil[403] = 0.002628663628020371  #
    spike_stencil[436] = 0.002858828161543839  # $150
    spike_stencil[461] = 0.004097463611984264  # $200
    spike_stencil[462] = 0.003345917406120509  #
    spike_stencil[496] = 0.002521467726855856  # $300
    spike_stencil[497] = 0.002784125730361008  #
    spike_stencil[541] = 0.003792850444811335  # $500
    spike_stencil[601] = 0.003688240815848247  # $1000
    spike_stencil[602] = 0.002392400117402263  #
    spike_stencil[636] = 0.001280993059008106  # $1500
    spike_stencil[661] = 0.001654665137536031  # $2000
    spike_stencil[662] = 0.001395501347054946  #
    spike_stencil[741] = 0.001154279140906312  # $5000
    spike_stencil[801] = 0.000832244504868709  # $10000

    ##############################################################################

    #  Part 10) Estimate a rough price using the best fit stencil slide

    ##############################################################################

    # Here we slide the stencil over the bell curve and see
    # where it fits the best. The best fit location and it's neighbor are used
    # in a weighted average to estimate the best fit USD price

    # set up scores for sliding the stencil
    best_slide = 0
    best_slide_score = 0
    total_score = 0

    # weighting of the smooth and spike slide scores
    smooth_weight = 0.65
    spike_weight = 1

    # establish the center slide such that if zero slide then 0.001 btc is $100 ($100k price)
    center_p001 = 601  # 601 is where 0.001 btc is in the output bell curve
    left_p001 = center_p001 - int((len(spike_stencil) + 1) / 2)
    right_p001 = center_p001 + int((len(spike_stencil) + 1) / 2)

    # upper and lower limits for sliding the stencil
    min_slide = -141  # $500k
    max_slide = 201  # $5k

    # slide the stencil and calculate slide score
    for slide in range(min_slide, max_slide):
        # shift the bell curve by the slide
        shifted_curve = output_bell_curve_bin_counts[
            left_p001 + slide : right_p001 + slide
        ]

        # score the smoothslide by multiplying the curve by the stencil
        slide_score_smooth = 0.0
        for n in range(0, len(smooth_stencil)):
            slide_score_smooth += shifted_curve[n] * smooth_stencil[n]

        # score the spiky slide by multiplying the curve by the stencil
        slide_score = 0.0
        for n in range(0, len(spike_stencil)):
            slide_score += shifted_curve[n] * spike_stencil[n]

        # add the spike and smooth slide scores, neglect smooth slide over wrong regions
        if slide < 150:
            slide_score = slide_score + slide_score_smooth * 0.65

        # see if this score is the best so far
        if slide_score > best_slide_score:
            best_slide_score = slide_score
            best_slide = slide

        # increment the total score
        total_score += slide_score

    # estimate the usd price of the best slide
    usd100_in_btc_best = output_bell_curve_bins[center_p001 + best_slide]
    btc_in_usd_best = 100 / (usd100_in_btc_best)

    # find best slide neighbor up
    neighbor_up = output_bell_curve_bin_counts[
        left_p001 + best_slide + 1 : right_p001 + best_slide + 1
    ]
    neighbor_up_score = 0.0
    for n in range(0, len(spike_stencil)):
        neighbor_up_score += neighbor_up[n] * spike_stencil[n]

    # find best slide neighbor down
    neighbor_down = output_bell_curve_bin_counts[
        left_p001 + best_slide - 1 : right_p001 + best_slide - 1
    ]
    neighbor_down_score = 0.0
    for n in range(0, len(spike_stencil)):
        neighbor_down_score += neighbor_down[n] * spike_stencil[n]

    # get best neighbor
    best_neighbor = +1
    neighbor_score = neighbor_up_score
    if neighbor_down_score > neighbor_up_score:
        best_neighbor = -1
        neighbor_score = neighbor_down_score

    # get best neighbor usd price
    usd100_in_btc_2nd = output_bell_curve_bins[center_p001 + best_slide + best_neighbor]
    btc_in_usd_2nd = 100 / (usd100_in_btc_2nd)

    # weight average the two usd price estimates
    avg_score = total_score / len(range(min_slide, max_slide))
    a1 = best_slide_score - avg_score
    a2 = abs(neighbor_score - avg_score)
    w1 = a1 / (a1 + a2)
    w2 = a2 / (a1 + a2)
    rough_price_estimate = int(w1 * btc_in_usd_best + w2 * btc_in_usd_2nd)

    # Print update
    print("40%..", end="", flush=True)

    ##############################################################################

    #  Part 10) Convert all outputs near round USD to the USD price used in the output

    ##############################################################################

    # In this section we converting the outputs to the price used by those outputs to
    # create a round USD amount. we also further remove micro round sat amounts (new in v 9)

    # list of round USD prices to collect outputs from
    usds = [5, 10, 15, 20, 25, 30, 40, 50, 100, 150, 200, 300, 500, 1000]

    # pct of price increase of decrease to include
    pct_range_wide = 0.25

    # filter for micro round satoshi amounts
    micro_remove_list = []
    i = 0.00005000
    while i < 0.0001:
        micro_remove_list.append(i)
        i += 0.00001
    i = 0.0001
    while i < 0.001:
        micro_remove_list.append(i)
        i += 0.00001
    i = 0.001
    while i < 0.01:
        micro_remove_list.append(i)
        i += 0.0001
    i = 0.01
    while i < 0.1:
        micro_remove_list.append(i)
        i += 0.001
    i = 0.1
    while i < 1:
        micro_remove_list.append(i)
        i += 0.01
    pct_micro_remove = 0.0001

    # init output prices list
    output_prices = []
    output_blocks = []
    output_times = []

    # loop through all outputs
    for i in range(0, len(raw_outputs)):
        # get the amount, height and time of the next output
        n = raw_outputs[i]
        b = block_heights_dec[i]
        t = block_times_dec[i]

        # loop throughll usd amounts possible
        for usd in usds:
            # calculate the upper and lower bounds for the USD range
            avbtc = usd / rough_price_estimate
            btc_up = avbtc + pct_range_wide * avbtc
            btc_dn = avbtc - pct_range_wide * avbtc

            # check if inside price bounds
            if btc_dn < n < btc_up:
                append = True

                # remove perfectly round sats
                for r in micro_remove_list:
                    rm_dn = r - pct_micro_remove * r
                    rm_up = r + pct_micro_remove * r
                    if rm_dn < n < rm_up:
                        append = False

                # if in price range and not perfectly round sat, add to list
                if append:
                    output_prices.append(usd / n)
                    output_blocks.append(b)
                    output_times.append(t)

    print("60%..", end="", flush=True)

    ##############################################################################

    #  Part 11) Find the central output and average deviation for plot window

    ##############################################################################

    # Here we use and iterative procedure of finding a central output,
    # shifting the price ranges to re-center the data, then finding the center again.
    # This asserts that the price is the center of the largest cluster of price
    # points of the day. This has been found by testing to be better than
    # the mean or the median because we specifically need the cluster center

    # define an algorithm for finding the central price point and avg deviation
    def find_central_output(r2, price_min, price_max):
        # sort the list of prices
        r6 = [r for r in r2 if price_min < r < price_max]
        outputs = sorted(r6)
        n = len(outputs)

        # Prefix sums
        prefix_sum = []
        total = 0
        for x in outputs:
            total += x
            prefix_sum.append(total)

        # count the number of point left and right
        left_counts = list(range(n))
        right_counts = [n - i - 1 for i in left_counts]
        left_sums = [0] + prefix_sum[:-1]
        right_sums = [total - x for x in prefix_sum]

        # find the total distance to other points
        total_dists = []
        for i in range(n):
            dist = (outputs[i] * left_counts[i] - left_sums[i]) + (
                right_sums[i] - outputs[i] * right_counts[i]
            )
            total_dists.append(dist)

        # find the Most central output
        min_index, _ = min(enumerate(total_dists), key=lambda x: x[1])
        best_output = outputs[min_index]

        # Median absolute deviation
        deviations = [abs(x - best_output) for x in outputs]
        deviations.sort()
        m = len(deviations)
        if m % 2 == 0:
            mad = (deviations[m // 2 - 1] + deviations[m // 2]) / 2
        else:
            mad = deviations[m // 2]

        return best_output, mad

    # use a tight pct range to find the first central price
    pct_range_tight = 0.05
    price_up = rough_price_estimate + pct_range_tight * rough_price_estimate
    price_dn = rough_price_estimate - pct_range_tight * rough_price_estimate
    central_price, av_dev = find_central_output(output_prices, price_dn, price_up)

    # find the deviation as a percentage of the price range
    price_range = price_up - price_dn
    dev_pct = av_dev / price_range

    # iteratively re-center the bounds and find a new center price until convergence
    avs = set()
    avs.add(central_price)
    while central_price not in avs:
        avs.add(central_price)
        price_up = central_price + pct_range_tight * central_price
        price_dn = central_price - pct_range_tight * central_price
        central_price, av_dev = find_central_output(output_prices, price_dn, price_up)
        price_range = price_up - price_dn
        dev_pct = av_dev / price_range

    # print update
    print("80%..", end="", flush=True)

    # because price flutucation may exceed bounds, check a wide ranger for the devation
    pct_range_med = 0.1
    price_up = central_price + pct_range_med * central_price
    price_dn = central_price - pct_range_med * central_price
    price_range = price_up - price_dn
    unused_price, av_dev = find_central_output(output_prices, price_dn, price_up)
    dev_pct = av_dev / price_range

    # use the pct deviation of data to set y axis range
    map_dev_axr = (0.15 - 0.05) / (0.20 - 0.17)
    ax_range = 0.05 + (dev_pct - 0.17) * map_dev_axr

    # set max and min y axis ranges
    if ax_range < 0.05:
        ax_range = 0.05
    if ax_range > 0.2:
        ax_range = 0.2
    price_up = central_price + ax_range * central_price
    price_dn = central_price - ax_range * central_price

    # print update
    print("100%\t\t\tdone", flush=True)
    if date_mode:
        print(
            "\n\n\t\t"
            + price_day_date_utc
            + " price: $"
            + f"{int(central_price):,}\n\n",
            flush=True,
        )

    ##############################################################################

    #  Part 12) Generate the chart in a webpage and serve it to the browser

    ##############################################################################

    # In this final section we use python to create a local webpage and serve that
    # webpage to the local browswer. We write a long string of data whose syntax is that
    # of html/javascript. We then pass python data into that string and save it as
    # an html file in the local directory. We then use python webbroswer to serve the
    # html into the local browser.

    # geometric layout of webpage and chart
    width = 1000  # canvas width (px)
    height = 660  # canvas height (px)
    margin_left = 120
    margin_right = 90
    margin_top = 100
    margin_bottom = 120

    # #get linear block hieghts on x axis
    start = block_nums_needed[0]
    end = block_nums_needed[-1]
    count = len(output_prices)
    step = (end - start) / (count - 1) if count > 1 else 0
    b3 = [start + i * step for i in range(count)]

    # Prepare python prices, heights, and timestamps for sending to html
    heights = []
    heights_smooth = []
    timestamps = []
    prices = []
    for i in range(len(output_prices)):
        if price_dn < output_prices[i] < price_up:
            heights.append(output_blocks[i])
            heights_smooth.append(b3[i])
            timestamps.append(output_times[i])
            prices.append(output_prices[i])

    # Sort by timestamps (optional, looks nicer)
    heights_smooth, prices = zip(*sorted(zip(heights_smooth, prices)))

    # set x tick locations
    num_ticks = 5
    n = len(heights_smooth)
    tick_indxs = [round(i * (n - 1) / (num_ticks - 1)) for i in range(num_ticks)]

    # Set the x tick labels
    xtick_positions = []
    xtick_labels = []
    for tk in tick_indxs:
        xtick_positions.append(heights_smooth[tk])
        block_height = heights[tk]
        timestamp = timestamps[tk]
        dt = datetime.utcfromtimestamp(timestamp)
        time_label = f"{dt.hour:02}:{dt.minute:02} UTC"
        label = f"{block_height}\n{time_label}"  # comma after 3 digits
        xtick_labels.append(label)

    # Calculate avg price
    avg_price = central_price

    # set the plot annotations
    plot_title_left = ""
    plot_title_right = ""
    bottom_note1 = ""
    bottom_note2 = ""
    if date_mode:
        plot_title_left = price_day_date_utc + " blocks from local node"
        plot_title_right = (
            "UTXOracle Consensus Price $" + f"{int(central_price):,} "
        )  # +test_price
        bottom_note1 = "Consensus Data:"
        bottom_note2 = "this plot is identical and immutable for every bitcoin node"
    if block_mode:
        plot_title_left = (
            "Local Node Blocks " + str(block_start_num) + "-" + str(block_finish_num)
        )
        plot_title_right = "UTXOracle Block Window Price $" + f"{int(central_price):,}"
        bottom_note1 = "* Block Window Price "
        bottom_note2 = "may have node dependent differences data on the chain tip"

    # Write the HTML code for the chart
    html_content = f"""<!DOCTYPE html>

    <html>
    <head>
    <title>UTXOracle Local</title>
    <style>
        body {{
            background-color: black;
            margin: 0;
            color: #CCCCCC;
            font-family: Arial, sans-serif;
            text-align: center;
        }}
        canvas {{
            background-color: black;
            display: block;
            margin: auto;
        }}


    </style>
    </head>
    <body>



    <div id="tooltip" style="
        position: absolute;
        background-color: black;
        color: cyan;
        border: 1px solid cyan;
        padding: 8px;
        font-size: 14px;
        border-radius: 5px;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.2s;
        text-align: left;
        z-index: 10;
    "></div>

    <div style="position: relative; width: 95%; max-width: 1000px; margin: auto;">

        <canvas id="myCanvas" style="width: 100%; height: auto;" width="{width}" height="{height}"></canvas>

        <button id="downloadBtn" style="
            position: absolute;
            bottom: 5%;
            right: 2%;
            font-size: 14px;
            padding: 6px 10px;
            background-color: black;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            opacity: 0.85;
        ">
        Save PNG
        </button>

    </div>



    <script>
    const canvas = document.getElementById('myCanvas');
    const ctx = canvas.getContext('2d');

    const width = {width};
    const height = {height};

    const marginLeft = {margin_left};
    const marginRight = {margin_right};
    const marginTop = {margin_top};
    const marginBottom = {margin_bottom};

    const plotWidth = width - marginLeft - marginRight;
    const plotHeight = height - marginTop - marginBottom;

    // Data
    const heights_smooth = {list(heights_smooth)};
    const prices = {list(prices)};
    const heights = {list(heights)};
    const timestamps = {list(timestamps)};


    const ymin = Math.min(...prices);
    const ymax = Math.max(...prices);
    const xmin = Math.min(...heights_smooth);
    const xmax = Math.max(...heights_smooth);

    // xticks
    const xtick_positions = {xtick_positions};
    const xtick_labels = {xtick_labels};


    // Scaling functions
    function scaleX(t) {{
        return marginLeft + (t - xmin) / (xmax - xmin) * plotWidth;
    }}

    function scaleY(p) {{
        return marginTop + (1 - (p - ymin) / (ymax - ymin)) * plotHeight;
    }}

    // Background
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, width, height);


    // UTXOracle Local Title
    ctx.font = "bold 36px Arial";
    ctx.textAlign = "center";
    ctx.fillStyle = "cyan";
    ctx.fillText("UTXOracle", width / 2 - 60, 40);  // Slight left shift for spacing

    ctx.fillStyle = "lime";
    ctx.fillText("Local", width / 2 + 95, 40);  // Slight right shift

    // Plot Date and Consensus Price
    ctx.font = "24px Arial";
    ctx.textAlign = "right";
    ctx.fillStyle = "white";
    ctx.fillText("{plot_title_left}", width /2, 80);
    ctx.textAlign = "left";
    ctx.fillStyle = "lime";
    ctx.fillText("{plot_title_right}", width/2 +10, 80);





    // Draw axes
    ctx.strokeStyle = "white";
    ctx.lineWidth = 1;

    // Y axis
    ctx.beginPath();
    ctx.moveTo(marginLeft, marginTop);
    ctx.lineTo(marginLeft, marginTop + plotHeight);
    ctx.stroke();

    // X axis
    ctx.beginPath();
    ctx.moveTo(marginLeft, marginTop + plotHeight);
    ctx.lineTo(marginLeft + plotWidth, marginTop + plotHeight);
    ctx.stroke();

    // Right spine
    ctx.beginPath();
    ctx.moveTo(marginLeft + plotWidth, marginTop);
    ctx.lineTo(marginLeft + plotWidth, marginTop + plotHeight);
    ctx.stroke();

    // Top spine
    ctx.beginPath();
    ctx.moveTo(marginLeft, marginTop);
    ctx.lineTo(marginLeft + plotWidth, marginTop);
    ctx.stroke();


    // Draw ticks and labels
    ctx.fillStyle = "white";
    ctx.font = "20px Arial";

    // Y axis ticks
    const yticks = 5;
    for (let i = 0; i <= yticks; i++) {{
        let p = ymin + (ymax - ymin) * i / yticks;
        let y = scaleY(p);
        ctx.beginPath();
        ctx.moveTo(marginLeft - 5, y);
        ctx.lineTo(marginLeft, y);
        ctx.stroke();
        ctx.textAlign = "right";
        ctx.fillText(Math.round(p).toLocaleString(), marginLeft - 10, y + 4);
    }}

    // X axis ticks
    ctx.textAlign = "center";
    ctx.font = "16px Arial";

    for (let i = 0; i < xtick_positions.length; i++) {{
        let x = scaleX(xtick_positions[i]);
        ctx.beginPath();
        ctx.moveTo(x, marginTop + plotHeight);
        ctx.lineTo(x, marginTop + plotHeight + 5);
        ctx.stroke();

        // Split label into two lines
        let parts = xtick_labels[i].split("\\n");
        ctx.fillText(parts[0], x, marginTop + plotHeight + 20);   // Block height
        ctx.fillText(parts[1], x, marginTop + plotHeight + 40);   // Time
    }}


    // Axis labels
    ctx.fillStyle = "white";
    ctx.font = "20px Arial";
    ctx.textAlign = "center";
    ctx.fillText("Block Height and UTC Time", marginLeft + plotWidth/2, height - 48);
    ctx.save();
    ctx.translate(20, marginTop + plotHeight/2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText("BTC Price ($)", 0, 0);
    ctx.restore();

    // Plot points
    ctx.fillStyle = "cyan";
    for (let i = 0; i < heights_smooth.length; i++) {{
        let x = scaleX(heights_smooth[i]);
        let y = scaleY(prices[i]);
        ctx.fillRect(x, y, .75, .75);
    }}

    // Annotation for average price
    ctx.fillStyle = "cyan";
    ctx.font = "20px Arial";
    ctx.textAlign = "left";
    ctx.fillText("- {int(avg_price):,}", marginLeft + plotWidth + 1, scaleY({avg_price}) +0);


    // Annotate bottom chart note

    ctx.font = "24px Arial";
    ctx.fillStyle = "lime";
    ctx.textAlign = "right";
    ctx.fillText("{bottom_note1}", 320, height-10);
    ctx.font = "24px Arial";
    ctx.fillStyle = "white";
    ctx.textAlign = "left";
    ctx.fillText("{bottom_note2}", 325, height-10);


    // === MOUSEOVER INFO ===

    const tooltip = document.getElementById('tooltip');

    canvas.addEventListener('mousemove', function(event) {{
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const mouseX = (event.clientX - rect.left) * scaleX;
    const mouseY = (event.clientY - rect.top) * scaleY;

    if (mouseX >= marginLeft && mouseX <= width - marginRight &&
        mouseY >= marginTop && mouseY <= marginTop + plotHeight) {{

        const fractionAcross = (mouseX - marginLeft) / plotWidth;
        let index = Math.round(fractionAcross * (heights.length - 1));
        index = Math.max(0, Math.min(index, heights.length - 1));

        const price = ymax - (mouseY - marginTop) / plotHeight * (ymax - ymin);
        const blockHeight = heights[index];
        const timestamp = timestamps[index];

        const date = new Date(timestamp * 1000);
        const hours = date.getUTCHours().toString().padStart(2, '0');
        const minutes = date.getUTCMinutes().toString().padStart(2, '0');
        const utcTime = `${{hours}}:${{minutes}} UTC`;

        tooltip.innerHTML = `
            Price: $${{Math.round(price).toLocaleString()}}<br>
            Block: ${{blockHeight.toLocaleString()}}<br>
            Time: ${{utcTime}}
        `;

        tooltip.style.left = (event.clientX + 5) + 'px';
        tooltip.style.top = (event.clientY + window.scrollY - 75) + 'px';
        tooltip.style.opacity = 1;
    }} else {{
        tooltip.style.opacity = 0;
    }}
    }});




    </script>


    <script>
    // Download canvas as PNG
    const downloadBtn = document.getElementById('downloadBtn');
    downloadBtn.addEventListener('click', function() {{
        const link = document.createElement('a');
        link.download = 'UTXOracle_Local_Node_Price.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
    }});
    </script>

    <br>
    <br>


    <h2 style="margin-top:10px; font-size:24px;">
    Want a 
    <span style="color:orange; font-size:24px;">Live Updating Oracle</span>
      with New Mempool Transactions? 
    </h2>


    <iframe
        width="{width}"
        height="{height}"
        src="https://www.youtube.com/embed/live_stream?channel=UCXN7Xa_BF7dqLErzOmS-B7Q&autoplay=1&mute=1"
        frameborder="0"
        allow="autoplay; encrypted-media"
        allowfullscreen

    </iframe>



    <br>

    </body>
    </html>
    """

    # name the file with dates or blocks
    filename = ".html"
    if date_mode:
        filename = "UTXOracle_" + price_date_dash + filename
    if block_mode:
        filename = (
            "UTXOracle_" + str(block_start_num) + "-" + str(block_finish_num) + filename
        )

    # Write file locally and serve to browser
    import webbrowser

    with open(filename, "w") as f:
        f.write(html_content)
    webbrowser.open("file://" + os.path.realpath(filename))


if __name__ == "__main__":
    print("-" * 80)
    print("Let's go!")
    print("-" * 80)

    run_mode, user_date = part_1a_process_args()
    data_dir, blocks_dir, bitcoin_cli_options = part_1b_initializing()
    rpc_output = part_2_ask_node(bitcoin_cli_options, "getblockchaininfo")
    consensus_block_timestamp = part_3_get_consensus_block_timestamp()
    target_date = part_4_set_target_date("date", [])
    target_block_start, target_block_end, target_block_hashes_needed = (
        part_5_get_target_block_heights(
            "date",
            "2025-05-25",
        )
    )
    found_blocks = part_6_create_target_block_binaries_index(target_block_hashes_needed)
    bins = part_7_build_bins()

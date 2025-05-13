from typing import Tuple
from models import RawBlock#, BlockHeader#, Transaction, Input, Output, ScriptSig, WitnessField, StackItem

# invaluable resource: https://learnmeabitcoin.com/technical/block/blkdat/

BLOCK_FILE_TO_READ = 'blk04930.dat'
    
def ghetto_debug_delineator(message: str) -> None:
    print("-" * 80)
    print(message)
    print("-" * 80)

def is_all_zeros(value: bytes) -> bool:
    return value == b'\x00' * 8

def get_xor_key(xor_data_file: str) -> Tuple[bytes, bool]:
    need_to_deobfuscate = True 
    with open(xor_data_file, 'rb') as f:
        xor_key = f.read(8)
        if is_all_zeros(xor_key):
            need_to_deobfuscate = False
        return xor_key, need_to_deobfuscate

def display_bytes(data: bytes, endian: str = 'little') -> str:
    return f"{data.hex()} --> {int.from_bytes(data, byteorder=endian)}"

def main():
    xor_key, need = get_xor_key('blocks/xor.dat')
    print(f"XOR key: {xor_key.hex()}")
    
    if need:
        print("Need to deobfuscate the data.")
        print("\nWrite some code to do this eventually.")
        exit()
    else:
        print("No need to deobfuscate the data.")
        print("-" * 80)
        
        print(f"Reading binary block file {BLOCK_FILE_TO_READ}...")
        print("-" * 80)

        # Read the block file        
        b = 0  # index of block to read
        start = 0  # start position of block in file to read raw block data
        with open(f'blocks/{BLOCK_FILE_TO_READ}', 'rb') as f:
            b += 1
            print(f"  Reading block #{b}...")
            raw_block = RawBlock.parse(f, start)
            print(raw_block)
            exit()

            # Extract the block height from the block data.
            # It's contained in the coinbase transaction (required by BIP-34).
            # BIP-34 didn't take effect until block 227,836 (3/24/2013)...so beware in prior blocks.
            # print("    Reading transaction data...")
            # n_txs, tx_data_pos = get_compact_size(block_bytes, 80)
            # print(f"      # of txs                 : {n_txs}")
            # print(f"      Tx data pos              : {tx_data_pos}")
            # print("-" * 80)

            # tx_data_version = block_bytes[tx_data_pos:tx_data_pos+4]
            # print(f"Tx data version     : {display_bytes(tx_data_version)}")
            # tx_data_marker = block_bytes[tx_data_pos+4:tx_data_pos+5]
            # print(f"Tx data marker      : {display_bytes(tx_data_marker)}")
            # tx_data_flag = block_bytes[tx_data_pos+5:tx_data_pos+6]
            # print(f"Tx data flag        : {display_bytes(tx_data_flag)}")
            # n_input_txs, coinbase_tx_in_pos = get_compact_size(block_bytes, tx_data_pos+6)
            # print(f"# of input txs      : {n_input_txs}")
            # print(f"coinbase tx pos     : {coinbase_tx_in_pos}")
            # print("-" * 80)

            # https://developer.bitcoin.org/reference/transactions.html
            # Coinbase input:  (note: there is no previous outpoint for the coinbase tx, by definition)
            # |-- previous outpoint TXID (hash) (32 bytes)
            #     previous outpoint index (4 bytes)
            #     number of bytes in script (compactSize)
            #     |-- # bytes in block height (1 byte) 
            #         block height (3 bytes)... will be 3 until block 16,777,216 --> 300 years from now
            #         coinbase script (until sequence)
            #         sequence (4 bytes)
            # cb_tx_hash = block_bytes[coinbase_tx_in_pos:coinbase_tx_in_pos+32]
            # print(f"Coinbase tx hash    : {cb_tx_hash.hex()}")
            # cb_tx_index = block_bytes[coinbase_tx_in_pos+32:coinbase_tx_in_pos+36]
            # print(f"Coinbase tx index   : {cb_tx_index.hex()}")
            # cb_tx_n_script_bytes, script_sig_pos = get_compact_size(block_bytes, coinbase_tx_in_pos+36)
            # print(f"# bytes in cb script: {cb_tx_n_script_bytes}")
            # print(f"ScriptSig pos       : {script_sig_pos}")
            
            # print("-" * 80)
            # script_sig = block_bytes[script_sig_pos:script_sig_pos+cb_tx_n_script_bytes]
            # print(f"ScriptSig           : {script_sig.hex()}")
            # block_height_n_btyes = script_sig[0]
            # print(f"# bytes in block ht : {block_height_n_btyes}")
            # block_height = script_sig[1:1+block_height_n_btyes]
            # print(f"Block height        : {display_bytes(block_height)}")
            # cb_script = script_sig[1+block_height_n_btyes:-4]
            # print(f"Coinbase script     : {cb_script.hex()}")
            # cb_sequence = script_sig[-4:]
            # print(f"Coinbase sequence   : {cb_sequence.hex()}")

if __name__ == "__main__":
    ghetto_debug_delineator("Let's go!")
    main()
    ghetto_debug_delineator("Done!")
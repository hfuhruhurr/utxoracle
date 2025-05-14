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

def display_preimage(preimage: str) -> None:
    print(format_hex_string(preimage))


def format_hex_string(hex_str, space_interval=8, hex_per_line=80):
    # Remove any existing spaces or newlines
    hex_str = hex_str.replace(" ", "").replace("\n", "")
    
    # Split into chunks of space_interval hex chars
    chunks = [hex_str[i:i+space_interval] for i in range(0, len(hex_str), space_interval)]
    
    # Group chunks to form lines with hex_per_line hex chars
    result = []
    chars_per_line = 0
    current_line = []
    
    for chunk in chunks:
        if chars_per_line + len(chunk) <= hex_per_line:
            current_line.append(chunk)
            chars_per_line += len(chunk)
        else:
            result.append(" ".join(current_line))
            current_line = [chunk]
            chars_per_line = len(chunk)
    
    # Append the last line if it exists
    if current_line:
        result.append(" ".join(current_line))
    
    return "\n".join(result)


def debug_preimages():
    # This preimage will create the transaction txid = b92c03f30b602c9722e82220ddd023907fe90f338d7818dc887b32b0f170ec9d
    known_good_preimage = '01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff63034ead0d04404321687c204d415241204d61646520696e2055534120f09f87baf09f87b8207c763033fabe6d6ddba189b7152a01f2dc78587b891b6056da1f740e23178396b08b7c5c66a0d88701000000000000001237333e640000000000ffffffffffffffff02f620f21200000000160014d16827c45ab3b3f961817257e6279ab35e8e25550000000000000000266a24aa21a9ed155cd0bc52b43013e271778c603991464f47ed3c56bc88d9d1f6602d15215804a78cbbe5'

    my_preimage = "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff63034ead0d04404321687c204d415241204d61646520696e2055534120f09f87baf09f87b8207c763033fabe6d6ddba189b7152a01f2dc78587b891b6056da1f740e23178396b08b7c5c66a0d88701000000000000001237333e640000000000fffffffffffffffff620f21200000000160014d16827c45ab3b3f961817257e6279ab35e8e25550000000000000000266a24aa21a9ed155cd0bc52b43013e271778c603991464f47ed3c56bc88d9d1f6602d15215804a78cbbe5"

    print("Known good preimage:")
    display_preimage(known_good_preimage)
    print()
    print("My preimage:")
    display_preimage(my_preimage)
    print()


def decipher_tx_id_creation():
    # from https://raw.githubusercontent.com/ragestack/blockchain-parser/refs/heads/master/result/blk_example.txt
    from models import RawBlock, hash256

    # courtesy of https://bitcoin.stackexchange.com/questions/120354/how-to-compute-a-txid-of-any-bitcoin-transaction-in-python
    # first, looked the block hash up on mempool.space to get the transaction txid
    # then, got raw tx data from  https://blockchain.info/rawtx/<transaction txid>?format=hex
    raw_tx_hash_hex = "010000000001010000000000000000000000000000000000000000000000000000000000000000ffffffff63034ead0d04404321687c204d415241204d61646520696e2055534120f09f87baf09f87b8207c763033fabe6d6ddba189b7152a01f2dc78587b891b6056da1f740e23178396b08b7c5c66a0d88701000000000000001237333e640000000000ffffffffffffffff02f620f21200000000160014d16827c45ab3b3f961817257e6279ab35e8e25550000000000000000266a24aa21a9ed155cd0bc52b43013e271778c603991464f47ed3c56bc88d9d1f6602d1521580401200000000000000000000000000000000000000000000000000000000000000000a78cbbe5"
    # raw_tx_hash_hex = "01000000000101189a3f6fbfb614264c8176cd2d3836882afc3c0940d698d6b481f3e5cb733c200000000000ffffffff0240420f00000000001976a914341b568f59229818c460b1795ad48cd78895c54d88ac6eeefa4a00000000160014d701ce5e753bd9454d343c8a3b86d84a3c34dbf502473044022001609cd43eb8e9b8f8438eded9f6b10bad32efd7620724ccd2ed5277c0c6a3ae02200f0c1c3f4c409ada536d2363a2d8bdad418df67fed9b36bfa4482bd9985bf396012102ee3c98964dd1bfe13bee16c0b95fcf8281f12c5885d1fcb7b59fc2cb01ca763200000000"
    raw_tx_hash = bytes.fromhex(raw_tx_hash_hex)

    print(f"There are {len(raw_tx_hash)} bytes in the raw tx hash.")
    
    version = raw_tx_hash[0:4]
    marker = raw_tx_hash[4:5]
    flag = raw_tx_hash[5:6]
    
    # Inputs
    n_inputs, inputs_pos, n_inputs_bytes = RawBlock.get_compact_size(raw_tx_hash, 6)
    utxo_txid = raw_tx_hash[inputs_pos:inputs_pos+32]
    utxo_vout = raw_tx_hash[inputs_pos+32:inputs_pos+36]
    input_script_size, script_sig_pos, input_script_size_bytes = RawBlock.get_compact_size(raw_tx_hash, inputs_pos+36)
    input_script = raw_tx_hash[script_sig_pos:script_sig_pos+input_script_size]
    sequence = raw_tx_hash[script_sig_pos+input_script_size:script_sig_pos+input_script_size+4]
    
    # Outputs
    n_outputs, outputs_pos, n_outputs_bytes = RawBlock.get_compact_size(raw_tx_hash, script_sig_pos+input_script_size+4)
    o1_amount = raw_tx_hash[outputs_pos:outputs_pos+8]
    o1_script_size, o1_script_pos, o1_script_size_bytes = RawBlock.get_compact_size(raw_tx_hash, outputs_pos+8)
    o1_script = raw_tx_hash[o1_script_pos:o1_script_pos+o1_script_size]
    o2_amount = raw_tx_hash[o1_script_pos+o1_script_size:o1_script_pos+o1_script_size+8]
    
    o2_script_size, o2_script_pos, o2_script_size_bytes = RawBlock.get_compact_size(raw_tx_hash, o1_script_pos+o1_script_size+8)
    o2_script = raw_tx_hash[o2_script_pos:o2_script_pos+o2_script_size]
    
    # Witness
    witness = raw_tx_hash[o2_script_pos+o2_script_size:-4]
    # n_stack_items, witness_pos, n_stack_items_bytes = RawBlock.get_compact_size(raw_tx_hash, o2_script_pos+o2_script_size)
    # print(f"n_stack_items: {n_stack_items}")

    # Locktime
    locktime = raw_tx_hash[-4:]

    # Preimage (the blob to be hashed to create the txid)
    preimage = version + n_inputs_bytes + utxo_txid + utxo_vout + input_script_size_bytes + input_script + sequence
    preimage += n_outputs_bytes + o1_amount + o1_script_size_bytes + o1_script
    preimage += o2_amount + o2_script_size_bytes + o2_script
    preimage += locktime

    reference_preimage = '0100000001189a3f6fbfb614264c8176cd2d3836882afc3c0940d698d6b481f3e5cb733c200000000000ffffffff0240420f00000000001976a914341b568f59229818c460b1795ad48cd78895c54d88ac6eeefa4a00000000160014d701ce5e753bd9454d343c8a3b86d84a3c34dbf500000000'

    
    print(f"\nVersion: {version.hex()}")
    print(f"Marker: {marker.hex()}")
    print(f"Flag: {flag.hex()}")
    print(f"\nn_inputs: {n_inputs}")
    print(f"n_inputs: {n_inputs_bytes.hex()}")
    print(f"utxo txid: {utxo_txid.hex()}")
    print(f"utxo vout: {utxo_vout.hex()}")
    print(f"input script size: {input_script_size_bytes.hex()}")
    print(f"input script: {input_script.hex()[:40]}...{input_script.hex()[-40:]}")
    print(f"sequence: {sequence.hex()}")
    print(f"\nn_outputs: {n_outputs}")
    print(f"n_outputs: {n_outputs_bytes.hex()}")
    print("Output 1:")
    print(f"    o1 amount: {o1_amount.hex()} --> {int.from_bytes(o1_amount, byteorder='little'):,} satoshis")
    print(f"    o1 script size: {o1_script_size_bytes.hex()} --> {int.from_bytes(o1_script_size_bytes, byteorder='little'):,} bytes")
    print(f"    o1 script: {o1_script.hex()[:40]}...{o1_script.hex()[-40:]}")
    print("Output 2:")
    print(f"    o2 amount: {o2_amount.hex()} --> {int.from_bytes(o2_amount, byteorder='little'):,} satoshis")
    print(f"    o2 script size: {o2_script_size_bytes.hex()} --> {int.from_bytes(o2_script_size_bytes, byteorder='little'):,} bytes")
    print(f"    o2 script: {o2_script.hex()[:40]}...{o2_script.hex()[-40:]}")
    print(f"\nWitness: {witness.hex()[:40]}...{witness.hex()[-40:]}")
    print(f"\nLocktime: {locktime.hex()}")

    print(f"\nThere are {len(preimage.hex())} hex chars in the preimage.")
    
    print(preimage.hex())
    # Debugging my preimage versus the reference preimage
    # print("\npreimage:")
    # print(f"{preimage.hex()[:81]}")
    # print(reference_preimage[:81])
    # print("\n")
    # print(f"{preimage.hex()[81:162]}")
    # print(reference_preimage[81:162])
    # print("\n")
    # print(f"{preimage.hex()[162:]}")
    # print(reference_preimage[162:])

    # print(f"\nDoes my preimage match the reference preimage? {preimage.hex() == reference_preimage}")

    print(f"\nTransaction txid: {hash256(preimage)[::-1].hex()}\n")

def main():
    # debug_preimages()
    # exit()

    # decipher_tx_id_creation()
    # exit()

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
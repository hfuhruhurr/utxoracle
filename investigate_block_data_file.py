from datetime import datetime, timezone
from hashlib import sha256
from typing import BinaryIO, Tuple
from dataclasses import dataclass
import struct

# invaluable resource: https://learnmeabitcoin.com/technical/block/blkdat/

BLOCK_FILE_TO_READ = 'blk04930.dat'

MAINNET_MAGIC_BYTES = b'\xf9\xbe\xb4\xd9'
HEADER_LENGTH = 80  # Bitcoin block header total length (in bytes)

@dataclass
class BlockHeader:
    header: bytes           # Full 80-byte block header
    version: bytes          # First 4 bytes of the header
    prev_block_hash: bytes  # Next 32 bytes
    merkle_root: bytes      # Next 32 bytes
    timestamp_bytes: bytes  # Next 4 bytes
    hash_target: bytes      # Next 4 bytes
    nonce: bytes            # Last 4 bytes

    @classmethod
    def get_timestamp(cls, timestamp_bytes: bytes) -> datetime:
        """Convert timestamp bytes to a UTC datetime object."""
        timestamp = int.from_bytes(timestamp_bytes, byteorder='little')
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    
    @property
    def timestamp(self) -> datetime:
        """Get the timestamp as a UTC datetime object."""
        return self.get_timestamp(self.timestamp_bytes)
    
    @property
    def block_hash(self) -> bytes:
        """Get the block hash by hashing the header twice with SHA-256."""
        return hash256(self.header)[::-1]
    
@dataclass
class RawBlock:
    magic_bytes: bytes
    size: bytes
    block_header: BlockHeader
    n_txs: bytes
    tx_data: bytes

    @property
    def is_mainnet(self) -> bool:
        """Check if the block is from the mainnet."""
        return self.magic_bytes == MAINNET_MAGIC_BYTES
    
    def __repr__(self) -> str:
        return (
            f"    Magic bytes (bytes)        : {self.magic_bytes.hex()}\n"
            f"    Magic bytes == Mainnet     : {self.is_mainnet}\n"
            f"    Block size                 : {self.size.hex()}\n"
            f"    Block header               : {self.block_header.header.hex()}\n"
            f"      Version (bit field)      : {self.block_header.version.hex()}\n"
            f"      Prev block hash          : {self.block_header.prev_block_hash.hex()}\n"
            f"      Merkle root              : {self.block_header.merkle_root.hex()}\n"
            f"      Timestamp (bytes)        : {self.block_header.timestamp_bytes.hex()}\n"
            f"      Timestamp                : {self.block_header.timestamp}\n"
            f"      Hash target (aka, bits)  : {self.block_header.hash_target.hex()}\n"
            f"      Nonce                    : {self.block_header.nonce.hex()}\n"
            f"    # of txs                   : {self.n_txs.hex()}\n"
            f"    Tx data (truncated)        : {self.tx_data.hex()[:50]}...{self.tx_data.hex()[-50:]}\n"
            f"    Block hash                 : {self.block_header.block_hash.hex()}"
        )
    
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
    
def hash256(block_header: bytes) -> bytes:
    return sha256(sha256(block_header).digest()).digest()

def get_compact_size(byte_data: bytes, pos: int) -> Tuple[int, int]:
    # Starting from pos in byte_data, get the compact size integer.
    # Return a tuple of (the compact size integer value, the position immediately after the compact size integer).
    leading_byte = byte_data[pos]
    if leading_byte < 0xfd:
        return leading_byte, pos + 1
    elif leading_byte == 0xfd:
        return int.from_bytes(byte_data[pos+1:pos+3], 'little'), pos + 3
    elif leading_byte == 0xfe:
        return int.from_bytes(byte_data[pos+1:pos+5], 'little'), pos + 5
    else:
        # note: should never happen...ow, the block's txs consume more than 4GB!
        return int.from_bytes(byte_data[pos+1:pos+9], 'little'), pos + 9
    
def display_bytes(data: bytes, endian: str = 'little') -> str:
    return f"{data.hex()} --> {int.from_bytes(data, byteorder=endian)}"

def get_block_header_bytes(block_bytes: bytes) -> BlockHeader:
    """Extract block header information from raw block bytes.

    Args:
        block_bytes: The raw block data (at least 80 bytes).

    Returns:
        A BlockHeaderInfo dataclass containing:
        - header: Full block header (80 bytes)
        - version: Version bytes (4 bytes)
        - prev_block_hash: Previous block hash (32 bytes)
        - merkle_root: Merkle root (32 bytes)
        - timestamp: Timestamp bytes (4 bytes)
        - bits: Bits (difficulty target, 4 bytes)
        - nonce: Nonce (4 bytes)

    Raises:
        ValueError: If block_bytes is shorter than 80 bytes or cannot be parsed.
    """
    if len(block_bytes) < HEADER_LENGTH:
        raise ValueError(f"Block data too short: got {len(block_bytes)} bytes, need at least {HEADER_LENGTH}")

    # Extract full header
    header = block_bytes[:HEADER_LENGTH]

    # Parse header fields using struct
    try:
        version, prev_block, merkle_root, timestamp, bits, nonce = struct.unpack(
            "<4s32s32s4s4s4s", header
        )
    except struct.error as e:
        raise ValueError("Failed to parse block header") from e

    return BlockHeader(
        header=header,
        version=version,
        prev_block_hash=prev_block,
        merkle_root=merkle_root,
        timestamp_bytes=timestamp,
        hash_target=bits,
        nonce=nonce
    )

def get_raw_block_bytes(f: BinaryIO, start: int) -> RawBlock:
    f.seek(start)

    # Read magic bytes
    magic_bytes = f.read(4)
    if len(magic_bytes) < 4:
        raise EOFError("File ended before reading magic bytes")

    # Read size of block data
    size_bytes = f.read(4)
    if len(size_bytes) < 4:
        raise EOFError("File ended before reading size bytes")
    
    # Compute size of block data (in bytes)
    size = int.from_bytes(size_bytes, byteorder='little')
    if size <= HEADER_LENGTH:    
        raise ValueError(f"Invalid block size: {size}")
    if size > 1_000_000_000:
        raise ValueError(f"Block size too large: {size} bytes")

    # Read block data
    block_data = f.read(size)
    if len(block_data) < size:
        raise EOFError(f"Expected {size} bytes, but read {len(block_data)}")

    # Get the number of transactions and the position of the transaction data
    n_txs, tx_data_pos = get_compact_size(block_data, HEADER_LENGTH)

    return RawBlock(
        magic_bytes=magic_bytes,
        size=size_bytes,
        block_header=get_block_header_bytes(block_data),
        n_txs=block_data[HEADER_LENGTH:tx_data_pos],
        tx_data=block_data[tx_data_pos:]  
    )

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
        start = 0
        with open(f'blocks/{BLOCK_FILE_TO_READ}', 'rb') as f:
            b += 1
            print(f"  Reading block #{b}...")
            raw_block = get_raw_block_bytes(f, start)
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
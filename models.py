from typing import BinaryIO
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Tuple, List, Optional

# invaluable resource: https://learnmeabitcoin.com/technical/block/blkdat/
MAINNET_MAGIC_BYTES = b'\xf9\xbe\xb4\xd9'
HEADER_LENGTH = 80  # Bitcoin block header total length (in bytes)
# HEADER_FORMAT = '<4s32s32s4s4s4s'  # Little-endian format for the block header

def hash256(block_header: bytes) -> bytes:
    return sha256(sha256(block_header).digest()).digest()

@dataclass
class BlockHeader:
    header: bytes           # Full 80-byte block header
    version: bytes          # First 4 bytes of the header
    prev_block_hash: bytes  # Next 32 bytes
    merkle_root: bytes      # Next 32 bytes
    timestamp: datetime     # Next 4 bytes
    hash_target: bytes      # Next 4 bytes
    nonce: bytes            # Last 4 bytes

    @property
    def block_hash(self) -> bytes:
        """Get the block hash by hashing the header twice with SHA-256."""
        return hash256(self.header)[::-1]

@dataclass
class Input:
    txid: bytes
    vout: int
    script_size: int
    script: bytes
    sequence: bytes

@dataclass
class Output:
    amount: int
    script_size: int
    script: bytes

@dataclass
class StackItem:
    size: int
    data: bytes

@dataclass
class WitnessField:
    n_stack_items: int
    stack_items: List[StackItem]

@dataclass
class Transaction:
    version: bytes
    marker: Optional[bytes] 
    flag: Optional[bytes]
    n_inputs: int
    inputs: List[Input]
    n_outputs: int
    outputs: List[Output]
    witness: Optional[List[WitnessField]] 
    lock_time: bytes

@dataclass
class RawBlock:
    magic_bytes: bytes
    size: int
    block_header: BlockHeader
    n_txs: int
    txs: bytes # List[Transaction]

    @property
    def is_mainnet(self) -> bool:
        """Check if the block is from the mainnet."""
        return self.magic_bytes == MAINNET_MAGIC_BYTES
    
    @classmethod
    def parse(cls, f: BinaryIO, start: int) -> 'RawBlock':
        """
        Parse a Bitcoin block from a binary file from the given start position.

        Args:
            file: A file object opened in binary mode ('rb') positioned at the start of a block.

        Returns:
            A RawBlock instance.
        """
        f.seek(start)

        # Read magic bytes (4 bytes)
        magic_bytes = f.read(4)
        if len(magic_bytes) < 4:
            raise ValueError("Incomplete magic bytes; end of file or invalid block")

        # Read size (4 bytes)
        size_bytes = f.read(4)
        if len(size_bytes) < 4:
            raise ValueError("Incomplete size field")
        size = int.from_bytes(size_bytes, 'little')

        # Read block_data (header + n_txs + transactions, based on size)
        block_data = f.read(size)
        if len(block_data) < size:
            raise ValueError(f"Incomplete block data: got {len(block_data)} bytes, expected {size}")

        # Parse block header (starts at byte 0 of block_data)
        block_header = cls.parse_block_header(block_data)

        # Parse n_txs (compact size, after header at byte 80)
        n_txs, tx_data_pos = cls.get_compact_size(block_data, pos=80)

        # Transaction data (from tx_data_pos to end)
        tx_data = block_data[tx_data_pos:]
        txs = cls.parse_txs(tx_data)

        return RawBlock(
            magic_bytes=magic_bytes,
            size=size,
            block_header=block_header,
            n_txs=n_txs,
            txs=txs
        )
    
    @staticmethod
    def parse_block_header(block_data: bytes) -> BlockHeader:
        """Extract block header information from raw block bytes.

        Args:
            block_data: The raw block data (at least 80 bytes).

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
        if len(block_data) < HEADER_LENGTH:
            raise ValueError(f"Block data too short: got {len(block_data)} bytes, need at least {HEADER_LENGTH}")

        # Extract header
        header = block_data[:HEADER_LENGTH]

        # Parse timestamp as integer, then convert to datetime
        timestamp_int = int.from_bytes(header[68:72], 'little')
        timestamp = datetime.fromtimestamp(timestamp_int, tz=timezone.utc)

        # Parse header fields 
        return BlockHeader(
            header=header,
            version=header[0:4],
            prev_block_hash=header[4:36],
            merkle_root=header[36:68],
            timestamp=timestamp,
            hash_target=header[72:76],
            nonce=header[76:80]
        )

    @staticmethod
    def get_compact_size(byte_data: bytes, pos: int) -> Tuple[int, int]:
        """
        Get the compact size integer from byte_data starting at pos.
        Args:
            byte_data: The input bytes containing the compact size integer.
            pos: The starting position in byte_data.
        Returns:
            A tuple of (compact size integer value, position immediately after).
        """
        leading_byte = byte_data[pos]
        if leading_byte < 0xfd:
            return leading_byte, pos + 1
        elif leading_byte == 0xfd:
            return int.from_bytes(byte_data[pos+1:pos+3], 'little'), pos + 3
        elif leading_byte == 0xfe:
            return int.from_bytes(byte_data[pos+1:pos+5], 'little'), pos + 5
        else:
            return int.from_bytes(byte_data[pos+1:pos+9], 'little'), pos + 9
        
    @staticmethod
    def parse_txs(tx_data: bytes) -> List[Transaction]:
        """Parse the transaction data into a list of Transaction objects."""
        transactions = []
        pos = 0
        while pos < len(tx_data):
            # Read transaction version
            version = tx_data[pos:pos+4]
            pos += 4

            # Read marker and flag (if present)
            if tx_data[pos:pos+1] == b'\x00':
                marker = tx_data[pos:pos+1]
                flag = tx_data[pos+1:pos+2]
                pos += 2
            else:
                marker = None
                flag = None
            
            # Read number of inputs
            n_inputs, pos = RawBlock.get_compact_size(tx_data, pos)

            # Read inputs
            inputs = []
            for _ in range(n_inputs):
                # Read txid (32 bytes)
                txid = tx_data[pos:pos+32]
                pos += 32

                # Read vout (4 bytes)
                vout_bytes = tx_data[pos:pos+4]
                vout = int.from_bytes(vout_bytes, byteorder='little')
                pos += 4

                # Read script size (compact size integer)
                script_size, pos = RawBlock.get_compact_size(tx_data, pos)

                # Read script (variable length)
                script = tx_data[pos:pos+script_size]
                pos += script_size

                # Read sequence (4 bytes)
                sequence = tx_data[pos:pos+4]
                pos += 4

                # Create input object
                inputs.append(Input(txid, vout, script_size, script, sequence))

            # Read number of outputs
            n_outputs, pos = RawBlock.get_compact_size(tx_data, pos)

            # Read outputs
            outputs = []
            for _ in range(n_outputs):
                # Read amount (8 bytes)
                amount_bytes = tx_data[pos:pos+8]
                amount = int.from_bytes(amount_bytes, byteorder='little')
                pos += 8

                # Read script size (compact size integer)
                script_size, pos = RawBlock.get_compact_size(tx_data, pos)

                # Read script (variable length)
                script = tx_data[pos:pos+script_size]
                pos += script_size

                # Create output object
                outputs.append(Output(amount, script_size, script))

            # Read witness (if present)
            # There is a set of stack_items for each input
            # Each stack_item is:
            #     - a compact size integer (size of the upcoming item)
            #     - the item data
            if marker == b'\x00':
                witness_fields = []
                for _ in range(n_inputs):
                    # Read the number of stack items
                    n_stack_items, pos = RawBlock.get_compact_size(tx_data, pos)
                    
                    # Read each stack item
                    stack_items = []
                    for _ in range(n_stack_items):
                        stack_item_size, pos = RawBlock.get_compact_size(tx_data, pos)
                        stack_item = tx_data[pos:pos+stack_item_size]
                        pos += stack_item_size
                        stack_items.append(StackItem(stack_item_size, stack_item))
                    
                    witness_fields.append(WitnessField(n_stack_items, stack_items))
                
                witness = witness_fields
            else:
                witness = None

            # Read lock time
            lock_time = tx_data[pos:pos+4]
            pos += 4

            transactions.append(Transaction(
                version=version,
                marker=marker,
                flag=flag,
                n_inputs=n_inputs,
                inputs=inputs,
                n_outputs=n_outputs,
                outputs=outputs,
                witness=witness,
                lock_time=lock_time
            ))

        return transactions
    
    def __repr__(self) -> str:
        result = (
            f"    Is mainnet?                : {self.is_mainnet}\n"
            f"    Block size                 : {self.size:,} bytes = {self.size / 1000 / 1000:.02f} MB\n"
            f"    Block header               : {self.block_header.header.hex()[:40]}...{self.block_header.header.hex()[-40:]}\n"
            f"      Version (bit field)      : {self.block_header.version[::-1].hex()}\n"
            f"      Prev block hash          : {self.block_header.prev_block_hash[::-1].hex()}\n"
            f"      Merkle root              : {self.block_header.merkle_root[::-1].hex()}\n"
            f"      Timestamp                : {self.block_header.timestamp} (UTC)\n"
            f"      Hash target (aka, bits)  : {self.block_header.hash_target[::-1].hex()}\n"
            f"      Nonce                    : {self.block_header.nonce[::-1].hex()}\n"
            f"    Block hash                 : {self.block_header.block_hash.hex()}\n"
            f"    # of txs                   : {self.n_txs:,}\n"
        )
        
        result += "\n    Transactions:\n"
        for i, tx in enumerate(self.txs, 1):
            if i <= 3:
                result += (
                    f"    --------------------------\n"
                    f"    Transaction #{i}:\n"
                    f"      Version                 : {tx.version[::-1].hex()}\n"
                    f"      Marker                  : {tx.marker[::-1].hex() if tx.marker else 'None'}\n"
                    f"      Flag                    : {tx.flag[::-1].hex() if tx.flag else 'None'}\n"
                    f"      # inputs                : {tx.n_inputs:,}\n"
                    f"      # outputs               : {tx.n_outputs:,}\n"
                    f"      # witness fields        : {len(tx.witness) if tx.witness else 0}\n"
                    f"      Lock time               : {tx.lock_time[::-1].hex()}\n"
                )
        return result + "\n"
        

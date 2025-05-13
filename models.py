from dataclasses import dataclass
from datetime import datetime #, timezone
from hashlib import sha256
# from typing import List #, Optional, Tuple

# invaluable resource: https://learnmeabitcoin.com/technical/block/blkdat/
MAINNET_MAGIC_BYTES = b'\xf9\xbe\xb4\xd9'
HEADER_LENGTH = 80  # Bitcoin block header total length (in bytes)
HEADER_FORMAT = '<4s32s32s4s4s4s'  # Little-endian format for the block header


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

# @dataclass
# class Input:
#     txid: bytes
#     vout_bytes: bytes
#     script_size_bytes: bytes
#     script: bytes
#     sequence: bytes

#     @property
#     def vout(self) -> int:
#         """Get the output index as an integer."""
#         return int.from_bytes(self.vout_bytes, byteorder='little')
    
#     @property
#     def script_size(self) -> int:
#         """Get the script size as an integer."""
#         return int.from_bytes(self.script_size_bytes, byteorder='little')
    
# @dataclass
# class Output:
#     amount_bytes: bytes
#     script_size_bytes: bytes
#     script: bytes

#     @property
#     def amount(self) -> int:
#         """Get the output amount as an integer."""
#         return int.from_bytes(self.amount_bytes, byteorder='little')
    
#     @property
#     def script_size(self) -> int:
#         """Get the script size as an integer."""
#         return int.from_bytes(self.script_size_bytes, byteorder='little')

# @dataclass
# class StackItem:
#     size_bytes: bytes
#     data: bytes

#     @property
#     def size(self) -> int:
#         """Get the size of the stack item as an integer."""
#         return int.from_bytes(self.size_bytes, byteorder='little')
    
# @dataclass
# class WitnessField:
#     n_stack_items_bytes: bytes
#     stack_items: List[StackItem]

#     @property
#     def n_stack_items(self) -> int:
#         """Get the number of stack items as an integer."""
#         return int.from_bytes(self.n_stack_items_bytes, byteorder='little')

# @dataclass
# class Transaction:
#     version: bytes
#     marker: Optional[bytes] 
#     flag: Optional[bytes]
#     n_inputs_bytes: bytes
#     inputs: List[Input]
#     n_outputs_bytes: bytes
#     outputs: List[Output]
#     witness: Optional[List[WitnessField]]  # Optional, only if marker == b'\x00'
#     lock_time: bytes

#     @property
#     def n_inputs(self) -> int:
#         """Get the number of inputs as an integer."""
#         return int.from_bytes(self.n_inputs_bytes, byteorder='little')
    
#     @property
#     def n_outputs(self) -> int:
#         """Get the number of outputs as an integer."""
#         return int.from_bytes(self.n_outputs_bytes, byteorder='little')

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
    
    # @classmethod
    # def parse_txs(cls, tx_data: bytes) -> List[Transaction]:
    #     """Parse the transaction data into a list of Transaction objects."""
    #     transactions = []
    #     pos = 0
    #     while pos < len(tx_data):
    #         # Read transaction version
    #         version = tx_data[pos:pos+4]
    #         pos += 4

    #         # Read marker and flag (if present)
    #         if tx_data[pos:pos+1] == b'\x00':
    #             marker = tx_data[pos:pos+1]
    #             flag = tx_data[pos+1:pos+2]
    #             pos += 2
    #         else:
    #             marker = None
    #             flag = None
            
    #         # Read number of inputs
    #         n_inputs, pos = get_compact_size(tx_data, pos)

    #         # Read inputs
    #         inputs = tx_data[pos:pos+n_inputs]
    #         pos += n_inputs

    #         # Read number of outputs
    #         n_outputs, pos = get_compact_size(tx_data, pos)

    #         # Read outputs
    #         outputs = tx_data[pos:pos+n_outputs]
    #         pos += n_outputs

    #         # Read witness (if present)
    #         # There is a set of stack_items for each input
    #         # Each stack_item is:
    #         #     - a compact size integer (size of the upcoming item)
    #         #     - the item data
    #         if marker == b'\x00':
    #             for i in range(n_inputs):
    #                 # Read the number of stack items
    #                 n_stack_items, pos = get_compact_size(tx_data, pos)
    #                 # Read each stack item
    #                 for j in range(n_stack_items):
    #                     len_stack_item, pos = get_compact_size(tx_data, pos)
    #                     stack_item = tx_data[pos:pos+len_stack_item]
    #                     pos += len_stack_item
    #         else:
    #             witness = None

    #         # Read lock time
    #         lock_time = tx_data[pos:pos+4]
    #         pos += 4

    #         transactions.append(Transaction(
    #             version=version,
    #             marker=marker,
    #             flag=flag,
    #             n_inputs=n_inputs, 
    #             inputs=inputs, 
    #             n_outputs=n_outputs, 
    #             outputs=outputs,
    #             witness=witness,
    #             lock_time=lock_time
    #         ))

    #     return transactions
    
    def __repr__(self) -> str:
        return (
            f"    Is mainnet?                : {self.is_mainnet}\n"
            f"    Block size                 : {self.size:,} bytes\n"
            f"    Block header               : {self.block_header.header.hex()}\n"
            f"      Version (bit field)      : {self.block_header.version.hex()}\n"
            f"      Prev block hash          : {self.block_header.prev_block_hash.hex()}\n"
            f"      Merkle root              : {self.block_header.merkle_root.hex()}\n"
            f"      Timestamp                : {self.block_header.timestamp} (UTC)\n"
            f"      Hash target (aka, bits)  : {self.block_header.hash_target.hex()}\n"
            f"      Nonce                    : {self.block_header.nonce.hex()}\n"
            f"    Block hash                 : {self.block_header.block_hash.hex()}"
            f"    # of txs                   : {self.n_txs:,}\n"
            # f"    Tx data (truncated)        : {self.txs.hex()[:50]}...{self.txs.hex()[-50:]}\n"
            # f"\n    len(txs) = {len(self.txs)}, type(txs) = {type(self.txs)}"
            "\n"
        )

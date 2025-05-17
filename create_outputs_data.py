import os
import polars as pl
from typing import List, Dict
import logging
from models import RawBlock


def process_block_file(file_path: str):
    # Read the block file        
    b = 0  # index of block to read
    pos = 0  # start position of block in file to read raw block data
    logger.info(f"Reading binary block file {file_path}...")
    logger.info("-" * 80)

   # Initialize the processor
    processor = BlockProcessor(chunk_size=1000, output_dir="dude_data")
    
    with open(f'{file_path}', 'rb') as f:
        file_len = len(f.read())
        logger.info(f"len {file_path} = {file_len:,} bytes")
        while pos < file_len:
            b += 1
            logger.info(f"  Reading block #{b:3} from byte {pos:12,}...")
            raw_block, new_pos = RawBlock.parse(f, pos)
            processor.process_raw_block(raw_block)
            pos = new_pos

            # if b >= 2:
            #     break
    processor.flush() 

class BlockProcessor:
    def __init__(self, chunk_size: int, output_dir: str):
        self.chunk_size = chunk_size
        self.output_dir = output_dir
        self.block_buffer: List[Dict] = []
        self.tx_buffer: List[Dict] = []
        self.input_buffer: List[Dict] = []
        self.output_buffer: List[Dict] = []
        os.makedirs(output_dir, exist_ok=True)
        self.blocks_file = os.path.join(output_dir, "blocks.parquet")
        self.txs_file = os.path.join(output_dir, "txs.parquet")
        self.inputs_file = os.path.join(output_dir, "inputs.parquet")
        self.outputs_file = os.path.join(output_dir, "outputs.parquet")

    def process_raw_block(self, block: RawBlock):
        # Extract block-level data
        block_hash = block.block_header.block_hash.hex()
        block_height = block.block_height
        timestamp = block.block_header.timestamp

        if block.is_mainnet:# Add block to block_buffer
            self.block_buffer.append({
                "block_id": block_hash,
                "block": block_height,
                "timestamp": timestamp,
                "n_txs": block.n_txs,
            })

            # Process transactions
            for tx in block.txs:
                txid = tx.txid
                self.tx_buffer.append({
                    "block": block_height,
                    "txid": txid,
                    "n_inputs": tx.n_inputs,
                    "n_outputs": tx.n_outputs,
                    "locktime": tx.locktime.hex(),
                    "is_coinbase": tx.is_coinbase,
                    "witness_size": tx.witness_size
                })

                for i, input in enumerate(tx.inputs):
                    self.input_buffer.append({
                        "index": i,
                        "txid": txid,
                        "prev_txid": input.utxo_txid.hex(),
                        "prev_vout": input.utxo_vout,
                        "script_size": input.script_size,
                    })

                for i, output in enumerate(tx.outputs):
                    self.output_buffer.append({
                        "index": i,
                        "txid": txid,
                        "amount": output.amount,
                        "script_size": output.script_size,
                        "is_op_return": output.script[0] == 0x6a
                    })

        # Write buffers to Parquet if chunk_size is reached
        for buffer, file_path in [
            (self.block_buffer, self.blocks_file),
            (self.tx_buffer, self.txs_file),
            (self.input_buffer, self.inputs_file),
            (self.output_buffer, self.outputs_file)
        ]:
            if len(buffer) >= self.chunk_size:
                df = pl.DataFrame(buffer)
                if os.path.isfile(file_path):
                    existing_df = pl.read_parquet(file_path)
                    df = pl.concat([existing_df, df])
                df.write_parquet(file_path)
                buffer.clear()

    def flush(self):
        # Write any remaining data
        for buffer, file_path, name in [
            (self.block_buffer, self.blocks_file, "blocks"),
            (self.tx_buffer, self.txs_file, "txs"),
            (self.input_buffer, self.inputs_file, "inputs"),
            (self.output_buffer, self.outputs_file, "outputs")
        ]:
            if buffer:
                logger.info(f"Flushing {len(buffer)} records to {file_path}")
                df = pl.DataFrame(buffer)
                try:
                    if os.path.isfile(file_path):
                        existing_df = pl.read_parquet(file_path)
                        df = pl.concat([existing_df, df])
                    df.write_parquet(file_path)
                    buffer.clear()
                    logger.info(f"Successfully flushed {name} to {file_path}")
                except Exception as e:
                    logger.error(f"Error flushing {name} to {file_path}: {e}")

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    logger = logging.getLogger(__name__)
    
    BLOCKS_DIR = 'blocks'
    block_files_to_read = ['blk04930.dat', 'blk04931.dat']
    for file in block_files_to_read:
        block_file_path = os.path.join(BLOCKS_DIR, file)
        process_block_file(block_file_path)
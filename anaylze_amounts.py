import marimo

__generated_with = "0.13.10"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import matplotlib.pyplot as plt
    import numpy as np
    return mo, np, pl, plt


@app.cell
def _(pl):
    blocks = pl.read_parquet('dude_data/blocks.parquet')
    txs = pl.read_parquet('dude_data/txs.parquet').drop(['locktime'])
    inputs = pl.read_parquet('dude_data/inputs.parquet')
    outputs = pl.read_parquet('dude_data/outputs.parquet').drop(['script_size'])
    return blocks, outputs, txs


@app.cell(hide_code=True)
def _(outputs, pl, txs):
    outputs_with_flags = (
        txs
        .with_columns(
            (pl.col('n_inputs') >= 6).alias('is_too_many_inputs'),
            (pl.col('n_outputs') >= 3).alias('is_too_many_outputs'),
            (pl.col('n_outputs') == 1).alias('is_one_output'),
            (pl.col('witness_size') > 500).alias('is_witness_too_big'),
        )
        .drop(['n_inputs', 'n_outputs', 'witness_size'])
        .join(outputs, on='txid', how='inner')
        .with_columns(
            (pl.col('amount') < 1000).alias('is_amount_too_small'),
            (pl.col('amount') >= 10e8).alias('is_amount_too_big'),
        )
        .rename({'index': 'output_index'})
        .select(
            pl.col(['block', 'txid', 'amount', 'output_index']),
            pl.col('^is_.*$')
        )
        .with_columns(
            pl.any_horizontal(pl.col('^is_.*$')).alias('exclude')
        )
    )
    return (outputs_with_flags,)


@app.cell
def _(blocks):
    min_block = blocks['block'].min()
    max_block = blocks['block'].max()
    return max_block, min_block


@app.cell
def _(max_block, min_block, mo):
    n_bins_per_exponent = mo.ui.slider(1, 250, value=200, label="num bins per exponent")
    exponents_range = mo.ui.range_slider(0, 12, value=[3,9], label="exponents")
    blocks_range = mo.ui.range_slider(min_block, max_block, label="blocks")
    exclude_switch = mo.ui.switch(label='exclude')
    return blocks_range, exclude_switch, exponents_range, n_bins_per_exponent


@app.cell
def _(exponents_range):
    min_exponent, max_exponent = exponents_range.value
    n_exponents = max_exponent - min_exponent
    return max_exponent, min_exponent, n_exponents


@app.cell
def _(
    blocks_range,
    exclude_switch,
    max_exponent,
    min_exponent,
    n_bins_per_exponent,
    n_exponents,
    np,
    outputs_with_flags,
    pl,
):
    filtered = (
        outputs_with_flags.filter(
            pl.col('amount') >= 10 ** min_exponent,
            pl.col('amount') < 10 ** max_exponent,
            pl.col('block') >= blocks_range.value[0],
            pl.col('block') <= blocks_range.value[1],
            pl.col('exclude') == exclude_switch.value,
        )
    )
    min_amount = filtered['amount'].min()
    max_amount = filtered['amount'].max()
    bins = np.logspace(
        np.log10(min_amount), 
        np.log10(max_amount), 
        num=n_bins_per_exponent.value * n_exponents
    )
    print(f"min_sats: {min_amount:,}, max_sats: {max_amount:,}")
    print(f"# included amounts: {len(filtered):,}")
    return bins, filtered


@app.cell(hide_code=True)
def _(bins, filtered, pl):
    # Compute histogram manually
    hist = (
        filtered 
        .with_columns(
            pl.col('amount').cut(breaks=bins, include_breaks=True).alias('bin')
        )
        .group_by('bin')
        .agg(count=pl.len())
        .with_columns(
            pl.col('bin').struct.field('breakpoint').alias('breakpoint'),
            pl.col('count').fill_null(0)
        )
        .sort('breakpoint')
    )
    # hist
    return (hist,)


@app.cell(hide_code=True)
def _(hist, np):
    finite_mask = hist['breakpoint'].is_finite()
    breakpoints = hist['breakpoint'].filter(finite_mask)[:-1]
    counts = hist['count'].filter(finite_mask)[:-1]
    widths = np.diff(hist['breakpoint'].filter(finite_mask))  # Compute widths
    # print(len(breakpoints))
    # print(len(counts))
    # print(len(widths))
    # widths
    return breakpoints, counts, widths


@app.cell
def _(blocks_range, exclude_switch, exponents_range, mo, n_bins_per_exponent):
    mo.vstack([
        n_bins_per_exponent,
        exponents_range,
        blocks_range,
        exclude_switch
    ])
    return


@app.cell(hide_code=True)
def _(breakpoints, counts, plt, widths):
    plt.bar(breakpoints, counts, width=widths)
    plt.xscale('log')
    plt.xlabel('Sats')
    plt.ylabel('Frequency')
    plt.title('Histogram of Amounts')
    plt.show()
    return


@app.cell
def _(hist, pl):
    hist.filter(pl.col('count') >= 500).sort('count', descending=True)
    return


if __name__ == "__main__":
    app.run()

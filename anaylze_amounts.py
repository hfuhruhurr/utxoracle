import marimo

__generated_with = "0.13.10"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import matplotlib.pyplot as plt
    import numpy as np
    import altair as alt
    return alt, mo, np, pl, plt


@app.cell
def _(mo):
    mo.md("""Part 7 - Construct the bin container""")
    return


@app.function
def build_btc_bins_list():
    # Build the bin values OG style
    btc_bins = [0.0]

    for exponent in range(-6, 6): # python range uses 'less than' for the big number 
        for b in range(0, 200):
            bin_value = 10 ** (exponent + b / 200)
            btc_bins.append(bin_value)

    return btc_bins


@app.cell
def _(pl):
    def create_dataframe(float_list):
        # Hard-coded list of round btc bins
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
            940,  # 0.05 
            1001, # 0.1 
            1061, # 0.2
            1096, # 0.3
            1140, # 0.5
            1201  # 1 btc
            ]

        # Create DataFrame with index and original values
        df = pl.DataFrame({
            "index": range(len(float_list)),
            "btc_bin": float_list,
            # Add translated value (example: simple translation by adding 10)
            "sat_bin": [round(x * 1e8) for x in float_list],
            # Initialize boolean column to False
            "is_round": [i in round_btc_bins for i in range(len(float_list))]
        })


        return df
    return (create_dataframe,)


@app.cell
def _(create_dataframe):
    bins = create_dataframe(build_btc_bins_list())
    return (bins,)


@app.cell
def _(np):
    def construct_bins_og(n_bins_per_exponent=200, min_btc_exp=-6, max_btc_exp=6):
        bins = [0.0]
        for exponent in range (min_btc_exp, max_btc_exp):
            for b in range(0, n_bins_per_exponent):
                bin = 10 ** (exponent + b / n_bins_per_exponent)
                bins.append(bin)
        return bins

    def construct_bins_dude(n_bins_per_exponent=200, min_btc_exp=-6, max_btc_exp=6):
        bins = [0.0]

        return bins + list(np.logspace(
            min_btc_exp,
            max_btc_exp,
            num=n_bins_per_exponent * (max_btc_exp - min_btc_exp),
            endpoint=False
        ))
    return construct_bins_dude, construct_bins_og


@app.cell(hide_code=True)
def _(alt, construct_bins_dude, construct_bins_og, pl):
    def visually_debug_bin_construction():
        steve = construct_bins_og(10, 2, 4)
        dude = construct_bins_dude(10, 2, 4)

        df = pl.DataFrame([steve, dude]).rename({'column_0': 'steve', 'column_1': 'dude'})
        df_long = df.unpivot(variable_name="column", value_name="value")

        chart = alt.Chart(df_long).mark_tick().encode(
            x=alt.X("value:Q", title="Value"),  # Quantitative axis for values
            y=alt.Y("column:N", title="Column"),  # Nominal axis for column names
            color=alt.Color("column:N", title="Column", scale=alt.Scale(range=["#1f77b4", "#ff7f0e"]))  # Distinct colors
        ).properties(
            title="Tick Marks for Column Values",
            width=600,
            height=100
        )

        chart.show()

    return (visually_debug_bin_construction,)


@app.cell
def _(visually_debug_bin_construction):
    visually_debug_bin_construction()
    return


@app.cell
def _(mo):
    mo.md("""Part 8 - Populate the bins with amounts""")
    return


@app.cell
def _(pl):
    blocks = pl.read_parquet('dude_data/blocks.parquet')
    txs = pl.read_parquet('dude_data/txs.parquet').drop(['locktime'])
    inputs = pl.read_parquet('dude_data/inputs.parquet')
    outputs = pl.read_parquet('dude_data/outputs.parquet').drop(['script_size'])
    return outputs, txs


@app.cell
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
def _(bins):
    sat_bins = bins['sat_bin'].to_list()
    return (sat_bins,)


@app.cell
def _(outputs_with_flags, pl, sat_bins):
    tallied = (
        outputs_with_flags
        # .filter(pl.col('amount') == 1000)
        # .select('amount')
        .with_columns(
            pl.col('amount').cut(breaks=sat_bins, left_closed=True, include_breaks=True).alias('bin')
        )
        .group_by('bin')
        .agg(count=pl.len())
        .with_columns(
            pl.col('bin')
                .struct.field('category')
                .cast(pl.Utf8)  # Convert categorical to string
                .str.extract(r'^\[(\d+\.?\d*)')  # Extract number before comma (e.g., '500' from '[500,1500)')
                .cast(pl.Int64)  # Convert to int
                .alias('lo_bound'),
            pl.col('bin').struct.field('breakpoint').alias('hi_bound'),
            pl.col('count').fill_null(0)
        )
        .sort('lo_bound', descending=False)
        .select(['bin', 'lo_bound', 'hi_bound', 'count'])
    )
    return (tallied,)


@app.cell
def _(tallied):
    tallied
    return


@app.cell
def _(bins, tallied):
    binned = (
        bins
        .join(tallied, left_on='sat_bin', right_on='lo_bound', how='left')
        .select(['index', 'sat_bin', 'is_round', 'count'])
        .fill_null(0)
    )
    return (binned,)


@app.cell
def _(pl):
    def part_9_transform(df):
        # Add bin widths
        df = df.with_columns(
            pl.col('sat_bin').diff(1).alias('sat_bin_width')
        )
    
        # zero out counts in bins <= 200 and bins >= 1601
        df = df.filter(
            pl.col('index').is_in(range(201,1601)),
        )
    
        # for round bins, replace actual count with average of nearest neighbors
        df = df.with_columns(
            pl.when(pl.col("is_round"))
            .then(
                    # Average of previous and next non-zero counts
                (
                    pl.col("count").shift(1).fill_null(0) + 
                    pl.col("count").shift(-1).fill_null(0)
                ) / 2
            )
            .otherwise(pl.col("count"))
            .alias("count")
        )

        # Replace counts with relative frequency
        total_count = df["count"].sum()
        df = df.with_columns(
            (pl.col("count") / total_count).alias("rel_freq")
        )

        return df
    return (part_9_transform,)


@app.cell
def _():
    #part_9_transform(binned)
    return


@app.cell
def _(plt):
    def plot_binned(df):
        x = df['sat_bin']
        y = df['rel_freq']
        widths = df['sat_bin_width']
    
        plt.bar(x, y, width=widths)
        plt.xscale('log')
        plt.axvspan(1e3, 1e5, alpha=0.3, color='orange', label='Stencil Overlay')
        plt.xlabel('Sats')
        plt.ylabel('Frequency')
        plt.title('Histogram of Amounts')
        plt.show()
    return (plot_binned,)


@app.cell
def _(binned, part_9_transform):
    part_9_transform(binned)
    return


@app.cell
def _(binned, part_9_transform, plot_binned):
    plot_binned(part_9_transform(binned))
    return


@app.cell
def _(mo):
    mo.md("""Part 10 - Stencil creation""")
    return


@app.function
def construct_stencils():
    num_elements = 803
    mean = 411
    std_dev = 201
    scale = 0.0015
    tilt = 0.0000005

    # Contstruct the smooth stencil
    smooth_stencil = []
    for x in range(num_elements):
        exp_part = -((x - mean) ** 2) / (2 * (std_dev ** 2))
        smooth_stencil.append( (scale * 2.718281828459045 ** exp_part) + (tilt * x) )

    # Construct the spike stencil
    spike_stencil = []
    for n in range(0, num_elements):
        spike_stencil.append(0.0)
    
    #round usd bin location   #popularity    #usd amount  
    spike_stencil[40] = 0.001300198324984352  # $1
    spike_stencil[141]= 0.001676746949820743  # $5
    spike_stencil[201]= 0.003468805546942046  # $10
    spike_stencil[202]= 0.001991977522512513  # 
    spike_stencil[236]= 0.001905066647961839  # $15
    spike_stencil[261]= 0.003341772718156079  # $20
    spike_stencil[262]= 0.002588902624584287  # 
    spike_stencil[296]= 0.002577893841190244  # $30
    spike_stencil[297]= 0.002733728814200412  # 
    spike_stencil[340]= 0.003076117748975647  # $50
    spike_stencil[341]= 0.005613067550103145  # 
    spike_stencil[342]= 0.003088253178535568  # 
    spike_stencil[400]= 0.002918457489366139  # $100
    spike_stencil[401]= 0.006174500465286022  # 
    spike_stencil[402]= 0.004417068070043504  # 
    spike_stencil[403]= 0.002628663628020371  # 
    spike_stencil[436]= 0.002858828161543839  # $150
    spike_stencil[461]= 0.004097463611984264  # $200
    spike_stencil[462]= 0.003345917406120509  # 
    spike_stencil[496]= 0.002521467726855856  # $300
    spike_stencil[497]= 0.002784125730361008  # 
    spike_stencil[541]= 0.003792850444811335  # $500
    spike_stencil[601]= 0.003688240815848247  # $1000
    spike_stencil[602]= 0.002392400117402263  # 
    spike_stencil[636]= 0.001280993059008106  # $1500
    spike_stencil[661]= 0.001654665137536031  # $2000
    spike_stencil[662]= 0.001395501347054946  # 
    spike_stencil[741]= 0.001154279140906312  # $5000
    spike_stencil[801]= 0.000832244504868709  # $10000

    return smooth_stencil, spike_stencil


@app.cell
def _(pl):
    pl.DataFrame(construct_stencils()[0])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()

import marimo

__generated_with = "0.13.10"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import matplotlib.pyplot as plt
    import numpy as np
    from typing import List
    return List, np, plt


@app.cell
def _(np):
    def build_smooth_stencil(n_elements=803, mean=411, sd=201, scale=0.0015, tilt=0.00000015):
        # Construct the smooth stencil
        stencil = []
        for x in range(n_elements):
            exp_part = -((x - mean) ** 2) / (2 * (sd ** 2))
            stencil.append(scale * np.exp(exp_part) + (tilt * x))

        return stencil

    def build_spike_stencil(n_elements=803):
        # Construct the spiked stencil
        stencil = []
        for n in range(0, n_elements):
            stencil.append(0.0)

        # Hard-coded values by design
        #round usd bin location   #popularity    #usd amount  
        stencil[40] = 0.001300198324984352  # $1
        stencil[141]= 0.001676746949820743  # $5
        stencil[201]= 0.003468805546942046  # $10
        stencil[202]= 0.001991977522512513  # 
        stencil[236]= 0.001905066647961839  # $15
        stencil[261]= 0.003341772718156079  # $20
        stencil[262]= 0.002588902624584287  # 
        stencil[296]= 0.002577893841190244  # $30
        stencil[297]= 0.002733728814200412  # 
        stencil[340]= 0.003076117748975647  # $50
        stencil[341]= 0.005613067550103145  # 
        stencil[342]= 0.003088253178535568  # 
        stencil[400]= 0.002918457489366139  # $100
        stencil[401]= 0.006174500465286022  # 
        stencil[402]= 0.004417068070043504  # 
        stencil[403]= 0.002628663628020371  # 
        stencil[436]= 0.002858828161543839  # $150
        stencil[461]= 0.004097463611984264  # $200
        stencil[462]= 0.003345917406120509  # 
        stencil[496]= 0.002521467726855856  # $300
        stencil[497]= 0.002784125730361008  # 
        stencil[541]= 0.003792850444811335  # $500
        stencil[601]= 0.003688240815848247  # $1000
        stencil[602]= 0.002392400117402263  # 
        stencil[636]= 0.001280993059008106  # $1500
        stencil[661]= 0.001654665137536031  # $2000
        stencil[662]= 0.001395501347054946  # 
        stencil[741]= 0.001154279140906312  # $5000
        stencil[801]= 0.000832244504868709  # $10000

        return stencil
    return build_smooth_stencil, build_spike_stencil


@app.cell
def _(List, plt):
    def draw_stencil(stencil: List[float], label="Dunno"):
        n_elements = len(stencil)
    
        # Create a line plot of the stencil
        fig, ax = plt.subplots()
        ax.plot(range(n_elements), stencil, label=label)
        ax.set_xlabel("Index")
        ax.set_ylabel("Weight")
        ax.set_title("Distribution")
        ax.legend()
        ax.grid(True)
        # plt.tight_layout()
    
        return fig # Return the figure for marimo to render
    return (draw_stencil,)


@app.cell
def _(build_smooth_stencil, draw_stencil):
    draw_stencil(build_smooth_stencil(), "Smooth")
    return


@app.cell
def _(build_spike_stencil, draw_stencil):
    draw_stencil(build_spike_stencil(), "Spike")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()

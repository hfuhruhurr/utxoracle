def part_7_build_curve_containter_og():
    # create a list of output_bell_curve_bins and add zero sats as the first bin
    output_bell_curve_bins = [0.0] # a decimal tells python the list will contain decimals

    # calculate btc amounts of 200 samples in every 10x from 100 sats (1e-6 btc) to 100k (1e5) btc
    print("Constructing bins container...")
    for exponent in range(-6, 6): # python range uses 'less than' for the big number 
        for b in range(0, 200):
            bin_value = 10 ** (exponent + b / 200)
            output_bell_curve_bins.append(bin_value)

    # Create a list the same size as the bell curve to keep the count of the bins
    print("Constructing counts container...")
    number_of_bins = len(output_bell_curve_bins)
    output_bell_curve_bin_counts = []
    for n in range(0, number_of_bins):
        output_bell_curve_bin_counts.append(float(0.0))

    # Let's see what we've got:
    print("Let's see what we've got:")
    for i in range(number_of_bins):
        # if i % 100 == 1 or i % 200 == 0:
        start = 0
        if start <= i <= start + 30:
        # if i % 20 == 1 and i <= 201:
            print(f"    i: {i:04}    bin: {round(output_bell_curve_bins[i] * 1e8):19,}    counts: {output_bell_curve_bin_counts[i]}")
    print()

def build_bin_container():
    # Build the bin values OG style
    bins = [0.0]

    for exponent in range(-6, 6): # python range uses 'less than' for the big number 
        for b in range(0, 200):
            bin_value = 10 ** (exponent + b / 200)
            bins.append(bin_value)

    # Place them into a more informative container
    container = {}
    for i, x in enumerate(bins):
        container[i] = {'btc_bin': x, 'sat_bin': round(x * 1e8), 'count': 0, 'is_round': False} 

    # Add the round numbers
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
    
    for i in round_btc_bins:
        container[i]['is_round'] = True
   
    return container

if __name__ == '__main__':
    # part_7_build_curve_containter_og()
    bc = build_bin_container()

    print(bc[401])
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
        start = 2390
        if start <= i <= start + 30:
        # if i % 20 == 1 and i <= 201:
            print(f"    i: {i:04}    bin: {round(output_bell_curve_bins[i] * 1e8):19,}    counts: {output_bell_curve_bin_counts[i]}")
    print()

if __name__ == '__main__':
    part_7_build_curve_containter_og()
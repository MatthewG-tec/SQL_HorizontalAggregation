import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt

def gen_data(N, d, dist='uniform'):
    """
    Generate synthetic dataset.
    
    Parameters:
        N: Total # of rows in the dataset.
        d: # of distinct groups in the grouping column.
        dist: Distribution type for groups ('uniform' or 'zipf').

    Returns:
        pd.DataFrame: A DataFrame with three columns: 'id', 'grouping_column', and 'value'.
    """
    if dist == 'uniform':
        # Uniformly distribute rows across groups
        groups = np.random.randint(0, d, size=N)
    elif dist == 'zipf':
        # Use Zipf's distribution to generate group assignments
        groups = np.random.zipf(2, size=N) % d
    else:
        raise ValueError("Unsupported Distribution")
    
    # Create the DataFrame
    data = pd.DataFrame({
        'id': np.arange(N),
        'grouping_column': groups,
        'value': np.random.random(size=N)
    })
    return data

def pivot_aggregation(data):
    """
    Perform horizontal aggregation using the PIVOT approach.
    
    Parameters:
        data: Input dataset with 'grouping_column' and 'value' columns.
    """
    return data.pivot_table(index='grouping_column', values='value', aggfunc='sum')

def case_aggregation(data, d):
    """
    Perform horizontal aggregation using CASE logic.
    
    Parameters:
        data: Input dataset with 'grouping_column' and 'value' columns.
        d: Number of distinct groups.
    """
    agg = pd.DataFrame({'group': np.arange(d)})  # Initialize result DataFrame with group IDs
    for group in range(d):
        # Compute the sum of 'value' for the current group
        group_sum = data.loc[data['grouping_column'] == group, 'value'].sum()
        agg.loc[group, f'case_{group}'] = group_sum  # Add the sum as a new column
    return agg

def spj_aggregation(data, d):
    """
    Perform horizontal aggregation using SPJ logic.
    
    Parameters:
        data: Input dataset with 'grouping_column' and 'value' columns.
        d: Number of distinct groups.
    """
    result = []
    for group in range(d):
        # Filter data for the current group and calculate the sum of 'value'
        subset = data[data['grouping_column'] == group]
        agg_value = subset['value'].sum()
        result.append({'group': group, 'value': agg_value})  # Append result as a dictionary
    return pd.DataFrame(result)

def run_multiple(N, n, d, dist='uniform', repetitions=5):
    """
    Run the aggregation methods multiple times and compute average execution times.
    
    Parameters:
        N: Total number of rows in the dataset.
        n: Placeholder (unused in current implementation).
        d: Number of distinct groups.
        dist: Distribution type for groups ('uniform' or 'zipf').
        repetitions: Number of times to repeat the experiment for averaging.
    """
    pivot_times, case_times, spj_times = [], [], []
    for _ in range(repetitions):
        # Generate synthetic dataset
        data = gen_data(N, d, dist)
        
        # Measure execution time for PIVOT
        start = time.time()
        pivot_aggregation(data)
        pivot_times.append(time.time() - start)
        
        # Measure execution time for CASE
        start = time.time()
        case_aggregation(data, d)
        case_times.append(time.time() - start)
        
        # Measure execution time for SPJ
        start = time.time()
        spj_aggregation(data, d)
        spj_times.append(time.time() - start)
    
    # Compute and return average execution times
    avg_pivot_time = np.mean(pivot_times)
    avg_case_time = np.mean(case_times)
    avg_spj_time = np.mean(spj_times)
    return avg_pivot_time, avg_case_time, avg_spj_time

def plot_results(x, pivot_times, case_times, spj_times, xlabel):
    """
    Visualize the execution time results for the aggregation methods.
    
    Parameters:
        x: X-axis values (N, n, or d depending on the experiment).
        pivot_times: Execution times for the PIVOT method.
        case_times: Execution times for the CASE method.
        spj_times: Execution times for the SPJ method.
        xlabel: Label for the X-axis indicating the varying parameter.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(x, pivot_times, label="PIVOT", marker='o')
    plt.plot(x, case_times, label="CASE", marker='s')
    plt.plot(x, spj_times, label="SPJ", marker='^')
    plt.xlabel(xlabel)
    plt.ylabel("Time in Seconds (s)")
    plt.title(f"Time Complexity Analysis ({xlabel})")
    plt.legend()
    plt.grid()
    plt.show()

def main():
    """
    Main function to run experiments for varying N, n, and d, and visualize results.
    """
    repetitions = 5  # Number of repetitions for averaging results

    #1: Varying table size (N)
    Ns = [1000, 5000, 10000, 50000, 100000]
    pivot_times, case_times, spj_times = [], [], []
    for N in Ns:
        pt, ct, st = run_multiple(N=N, n=1000, d=16, repetitions=repetitions)
        pivot_times.append(pt)
        case_times.append(ct)
        spj_times.append(st)
    plot_results(Ns, pivot_times, case_times, spj_times, xlabel="Fact Table Size (N)")

    #2: Varying FH table size (n)
    ns = [1000, 5000, 10000, 20000]
    pivot_times, case_times, spj_times = [], [], []
    for n in ns:
        pt, ct, st = run_multiple(N=50000, n=n, d=16, repetitions=repetitions)
        pivot_times.append(pt)
        case_times.append(ct)
        spj_times.append(st)
    plot_results(ns, pivot_times, case_times, spj_times, xlabel="FH Table Size (n)")

    #3: Varying number of distinct groups (d)
    ds = [8, 16, 32, 64, 128]
    pivot_times, case_times, spj_times = [], [], []
    for d in ds:
        pt, ct, st = run_multiple(N=50000, n=1000, d=d, repetitions=repetitions)
        pivot_times.append(pt)
        case_times.append(ct)
        spj_times.append(st)
    plot_results(ds, pivot_times, case_times, spj_times, xlabel="Distinct Grouping Columns (d)")

if __name__ == "__main__":
    main()

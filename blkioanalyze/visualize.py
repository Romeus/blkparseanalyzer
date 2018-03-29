import matplotlib.pyplot as plt

def visualize_generic(data, xlabel, ylabel, title):
    fig, ax = plt.subplots()
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.grid()
    ax.plot(data)

def visualize_os_overhead(data):
    visualize_generic(data, "time", "os_overhead", "OS overhead (Q2C/D2C)")

def visualize_sector_reads(data):
    visualize_generic(data, "time", "sector number", "Sector reads")

def visualize_sector_counts(data):
    plt.bar(data.sector.values.tolist(), data.num_reads.values.tolist())


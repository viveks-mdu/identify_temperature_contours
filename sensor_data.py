__author__ = 'vivek'
# Vivek Anand Sampath - vxs135130
import sys
import codecs
import random
import operator
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

global c, cluster_size, nodes_category_cnt, nodes_total_cnt
data_set = []
mean_for_data = {}
sensor_coordinates = []

def read_data_set(file_name):
    global data_set, mean_for_data

    fh = codecs.open(file_name, "rU", "utf-8", errors="ignore")

    sum_for_data = {}
    frq_for_data = {}

    for i in [2, 3, 4, 5]:
        sum_for_data[i] = 0
        frq_for_data[i] = 0
        mean_for_data[i] = 0

    line_count = 0
    for line in fh:
        data = [float(x) for x in line.strip().split()]
        data_set.append(data)

        for i in [2, 3, 4, 5]:
            if not math.isnan(data[i]):
                sum_for_data[i] += data[i]
                frq_for_data[i] += 1

        line_count += 1
        # if line_count >= 500000:
            # break

    # print(len(data_set))

    for i in [2, 3, 4, 5]:
        mean_for_data[i] = sum_for_data[i] / frq_for_data[i]

def read_sensor_locations(sensor_locations):
    global sensor_coordinates

    fh1 = codecs.open(sensor_locations, "rU", "utf-8", errors="ignore")

    sensor_coordinates.append((0, 0))
    for line in fh1:
        sensor_position = line.strip().split()
        sensor_coordinates.append((sensor_position[1], sensor_position[2]))


def kmeans(index, k):
    global data_set, mean_for_data, c, nodes_category_cnt, nodes_total_cnt

    c = [0 for i in range(k)]
    a = [0 for i in range(len(data_set))]
    mismatch = 0

    for i in range(k):
        c[i] = data_set[random.randint(0, len(data_set)-1)][index]

    while True:
        mismatch = 0
        for i in range(len(data_set)):

            if math.isnan(data_set[i][index]):
                data_set[i][index] = mean_for_data[index]

            prev_assignment = a[i]
            a[i] = min_dist_assignment(data_set[i][index], c)

            if prev_assignment != a[i]:
                mismatch += 1

        c = find_mean(a, index, k)

        if mismatch == 0:
            break

    num_nodes = 54

    nodes_category_cnt = {}
    for i in range(num_nodes+1):
        nodes_category_cnt[i] = {}
        for j in range(cluster_size):
            nodes_category_cnt[i][j] = 0

    nodes_total_cnt = [0 for i in range(num_nodes+1)]

    for i in range(len(data_set)):
        if not math.isnan(data_set[i][1]) and int(data_set[i][1]) <= 54:
            nodes_category_cnt[int(data_set[i][1])][a[i]] += 1
            nodes_total_cnt[int(data_set[i][1])] += 1

def min_dist_assignment(x_i, c):
    min_distance = 0
    min_i = 0

    for i in range(len(c)):
        dist = math.pow((x_i - c[i]), 2)

        if i == 0:
            min_distance = dist
            min_i = i
        else:
            if dist < min_distance:
                min_distance = dist
                min_i = i

    return min_i

def find_mean(a, index, k):
    global data_set, mean_for_data

    total_sum = [0 for i in range(k)]
    freq_count = [0 for i in range(k)]

    mean = [0 for i in range(k)]

    for i in range(k):
        total_sum[i] = 0
        freq_count[i] = 0

    for i in range(len(data_set)):
        total_sum[int(a[i])] += data_set[i][index]
        freq_count[int(a[i])] += 1

    for i in range(k):
        if freq_count[i] != 0:
            mean[i] = (total_sum[i] / freq_count[i])
        else:
            mean[i] = 0

    return mean

def display_graph():
    global data_set, c, mean_for_data, sensor_coordinates, cluster_size, nodes_category_cnt, nodes_total_cnt

    color_spectrum = []
    for i in range(cluster_size):
        color_spectrum.append([float(i)/float(cluster_size), 0.0, float(cluster_size-i)/float(cluster_size)])

    dict_cluster = {}
    for i in range(cluster_size):
        dict_cluster[i] = c[i]

    dict_cluster_x = sorted(dict_cluster.items(), key=operator.itemgetter(1))

    i = 0
    cluster_color = {}
    for key, value in dict_cluster_x:
        cluster_color[key] = color_spectrum[i]
        i += 1

    x = []
    y = []
    color_set = []
    size_radius = []

    for i in range(1, len(nodes_category_cnt)):
        nodes_category_cnt_x = sorted(nodes_category_cnt[i].items(), key=operator.itemgetter(1), reverse=True)
        for order_node in range(len(nodes_category_cnt_x)):
            x.append(sensor_coordinates[i][0])
            y.append(sensor_coordinates[i][1])
            color_set.append(cluster_color[nodes_category_cnt_x[order_node][0]])
            if nodes_total_cnt[i] > 0:
                size = (nodes_category_cnt_x[order_node][1] * 4000/nodes_total_cnt[i])
                size_radius.append(size)
            else:
                size_radius.append(0)
            break

    plt.axis([0, 42, 0, 34])
    plt.title("TEMPERATURE ZONES AT SENSOR LOCATIONS")
    plt.xlabel("FACILITY X-COORDINATE")
    plt.ylabel("FACILITY Y-COORDINATE")

    for i in range(1, len(sensor_coordinates)):
        x_val = sensor_coordinates[i][0]
        y_val = sensor_coordinates[i][1]
        plt.text(x_val, y_val, i, bbox=dict(facecolor='yellow', alpha=0.5))

    plt.scatter(x, y, c=color_set, s=size_radius)
    plt.show()

def main():
    global data_set, cluster_size

    print("Program started ...")

    if len(sys.argv) == 4:
        read_data_set(sys.argv[1])
        read_sensor_locations(sys.argv[2])
        cluster_size = int(sys.argv[3])
    else:
        print("Invalid command line arguments")
        print("arg1 - <input_file>; arg2 - <sensor_locations_file>; arg3 - <cluster_size>")
        exit(0)

    # set temperature
    index = 2

    print("Starting k-means algorithm ...")
    kmeans(index, cluster_size)

    print("Preparing to display the temperature zones...")
    display_graph()

    print("Program completed.")

if __name__ == "__main__":
    main()

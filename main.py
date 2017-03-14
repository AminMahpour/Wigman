#!/usr/bin/env python3

import operator
import pyBigWig
import sys
import matplotlib.pyplot as pp
import numpy as np

def parseconfig(conf_file):
    config = open(conf_file, mode="r")
    bed_line = []
    bw_line =[]
    pdf_file = ""
    for line in config:

        line=line.strip("\n").split("\t")

        if line[0] == "bed":
            bed_line.append([line[1], int( line[2]), int( line[3]), line[4]])
        elif line[0] =="bw":
            bw_line.append([line[1], float(line[2]), float(line[3]), float(line[4]), line[5], line[6], line[7]])
        elif line[0] == "pdf":
            pdf_file = line[1]

    print(bed_line,bw_line,pdf_file)
    return bed_line, bw_line, pdf_file


class BigwigObj:
    def __init__(self, url):
        myurl = url
        self.bw = pyBigWig.open(myurl)

    def get_scores(self, pos):
        return self.bw.values(*pos)

def bedreader(file, min=50, max=50):
    data = open(file, mode="r")
    for line in data:
        line = line.split("\t")
        line[1] = int(line[1]) - min
        line[2] = int(line[2]) + max
        out = (line[0], line[1], line[2])
        yield out

def get_value_from_pos(bwurl, bed, min=50, max=60, sort=True):
    bw = BigwigObj(bwurl)
    out_data = []
    data_output = []
    masked_data = []
    for coord in bed:
        scores = None
        try:
            scores = bw.get_scores(coord)
        except Exception as e:
            print("Error occurred: {0}".format(e))
        if scores != None:
            if len(scores) != 0:

                data_output.append([coord, np.mean(scores[min:max]), scores])
    if sort:


        for i in data_output:
            if not np.isnan(np.mean(i[2])):
                masked_data.append(i)

        out_data = sorted(masked_data, key=operator.itemgetter(1))
    else:
        out_data = data_output

    return out_data

graph=1

config_file = sys.argv[1]
beds, bws, pdf_file = parseconfig(config_file)
print(beds)

print("calculating...")
fig = pp.figure(figsize=(2 * len(bws), 4*len(beds)+2), dpi=90)
for j, bed in enumerate(beds):
    current_bed = bedreader(bed[0],min=bed[1],max=bed[2])
    bed_title = bed[3]
    sorted_bed = []
    for i, bw in enumerate(bws):

        bw_file = bw[0]
        bw_min = float(bw[1])
        bw_max = float(bw[2])
        bw_step = float(bw[3])
        bw_gradient = str(bw[4])
        bw_title = str(bw[5])
        bw_desc = str(bw[6])

        if i == 0:
            raw_data = get_value_from_pos(bw_file, current_bed,min=bed[1], max=bed[2]+10)
            sorted_bed = [x[0] for x in raw_data]
            current_bed = sorted_bed
        else:
            raw_data = get_value_from_pos(bw_file, current_bed, sort=False)

        array = np.array([x[2] for x in raw_data])
        masked_array = np.ma.masked_invalid(array)
        y = int(len(raw_data)/40) + 2
        blrd_color = pp.cm.bwr
        hot_color = pp.cm.hot

        current_color = None
        if bw_gradient == "BuRd":current_color = pp.cm.bwr
        if bw_gradient == "Hot": current_color = pp.cm.hot
        if bw_gradient == "Reds": current_color = "Reds"
        if bw_gradient == "Blues": current_color = "Blues_r"

        print("plotting {0}...".format(bw_file))

        pp.subplot(len(beds), len(bws), graph)

        pp.title(bw_title)

        pp.pcolormesh(masked_array, cmap=current_color)
        pp.clim(bw_min, bw_max)
        cbar = pp.colorbar(orientation="horizontal", ticks=list(np.arange(bw_min,bw_max,step=bw_step)), pad=0.07)
        cbar.set_label(bw_desc, size=10)
        cbar.ax.tick_params(labelsize=8)
        frame1 = pp.gca()
        if i == 0:
            pp.ylabel("{0}\nn={1}".format(bed_title,len(raw_data)), fontsize=16, color="black")

        for xlabel_i in frame1.axes.get_xticklabels():
            xlabel_i.set_visible(False)
            xlabel_i.set_fontsize(0.0)
        for xlabel_i in frame1.axes.get_yticklabels():
            xlabel_i.set_fontsize(0.0)
            xlabel_i.set_visible(False)
        for tick in frame1.axes.get_xticklines():
            tick.set_visible(False)
        for tick in frame1.axes.get_yticklines():
            tick.set_visible(False)
        graph += 1
pp.savefig(pdf_file)

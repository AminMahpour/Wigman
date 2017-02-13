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
            bed_line.append([line[1], int( line[2]), int( line[3])])
        elif line[0] =="bw":
            bw_line.append([line[1], int(line[2]), int(line[3]), int(line[4]), line[5], line[6], line[7]])
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
            if np.isnan(np.mean(i[2])): data_output.remove(i)

        out_data = sorted(data_output, key=operator.itemgetter(1))
    else:
        out_data = data_output

    return out_data

config_file = sys.argv[1]
beds, bws, pdf_file = parseconfig(config_file)

current_bed = bedreader(beds[0][0])
sorted_bed = []
print("calculating...")
fig = pp.figure(figsize=(2 * len(bws), 8), dpi=600)
for i, bw in enumerate(bws):

    bw_file = bw[0]
    bw_min = int(bw[1])
    bw_max = int(bw[2])
    bw_step = int(bw[3])
    bw_gradient = str(bw[4])
    bw_title = str(bw[5])
    bw_desc = str(bw[6])

    if i == 0:
        raw_data = get_value_from_pos(bw_file, current_bed)
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
    if bw_gradient == "Hot":current_color = pp.cm.hot
    if bw_gradient == "Reds": current_color = "Reds"
    if bw_gradient == "Blues": current_color = "Blues_r"

    print("plotting {0}...".format(bw_file))
    pp.subplot(1, len(bws), i+1)
    pp.title(bw_title)

    pp.pcolormesh(masked_array, cmap=current_color)
    pp.clim(bw_min, bw_max)
    cbar = pp.colorbar(orientation="horizontal", ticks=list(range(bw_min, bw_max, bw_step)), pad=0.07)
    cbar.set_label(bw_desc, size=10)
    cbar.ax.tick_params(labelsize=8)
    frame1 = pp.gca()
    if i == 0:
        pp.ylabel("n={0}".format(len(raw_data)), fontsize=16, color="black")

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

pp.savefig(pdf_file)

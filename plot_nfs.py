# %%
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import re
from datetime import datetime
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

# %%
parser = argparse.ArgumentParser()

parser.add_argument(
    type=str,
    help="log file",
    dest="input"
)

args = parser.parse_args()
file = Path(args.input)

# %%
re_temp = {"read": [], "write": [], "times": []}

columns = [
    "ops/s",
    "kb/s",
    "kb/op",
    "retrans",
    "avg RTT",
    "avg exe",
    "avg queue",
    "errors",
]

data = defaultdict(lambda: defaultdict(lambda: deepcopy(re_temp)))

linetype = "time"
mount = None

with open(file) as f:
    while len(line := f.readline()) > 0:
        if match := re.match(".*mounted on (.*):", line):
            mount = match.group(1)

        if re.match("read.*", line):
            linetype = "read"
            continue
        if re.match("write.*", line):
            linetype = "write"
            continue
        if re.search("##########", line):
            linetype = "time"
            continue
        if linetype:
            if linetype == "time":
                time = line
                linetype = None
                continue

            fields = [n.strip() for n in line.split("    ") if len(n) > 0]

            for k, v in zip(columns, fields):
                if match := re.search(".*\((.*)%\)", v):
                    v = match.group(1)
                data[k][mount][linetype].append(float(v))
                if linetype == "read":
                    data[k][mount]["times"].append(time)
            linetype = None

# %%

fig = plt.figure(figsize=(8, 50))
ccounter = [0 for _ in range(4)]

for i, (plot_name, mount_d) in enumerate(data.items()):
    ax = plt.subplot(8, 1, i+1)
    ax.set_title(plot_name)
    ax2 = ax.twinx()

    for j, (mount_name, rw_d) in enumerate(mount_d.items()):
        palatte = sns.color_palette("Paired", n_colors=len(mount_d)*2)
        c = palatte[j*2]
        s = 5
        timestamps = []
        for t in rw_d["times"]:
            timestamps.append(
                # datetime.strptime(t, "%a %b %d %I:%M:%S %p %Z %Y\n").strftime("%m-%d")
                datetime.strptime(t, "%a %b %d %I:%M:%S %p %Z %Y\n").timestamp()
            )

        for rw in ["read", "write"]:
            ax.set_ylabel(rw)
            ax.scatter(
                x=timestamps,
                y=rw_d[rw],
                color=c,
                s=s,
                label=f"{mount_name}:{rw}",
            )
            c = palatte[j*2+1]
            ax = ax2
    plt.legend(markerscale=5)

plt.tight_layout()
plt.savefig("plot_nfsiostat.jpg")

# %%

#!/usr/bin/env python3
import sys
from Bio import SeqIO

input_fasta = sys.argv[1]
output_fasta = sys.argv[2]

with open(output_fasta, "w") as outputs:
    for r in SeqIO.parse(input_fasta, "fasta"):
        r.description = r.id
        r.id = "_".join((r.description).split("_")[1:])
        SeqIO.write(r, outputs, "fasta")

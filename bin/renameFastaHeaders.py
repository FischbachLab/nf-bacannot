#!/usr/bin/env python3
import sys
from Bio import SeqIO

input_fasta = sys.argv[1]
output_fasta = sys.argv[2]

sequence_number  = 0

with open(output_fasta, "w") as outputs:
    for r in SeqIO.parse(input_fasta, "fasta"):
        sequence_number += 1
        r.description = r.id
        r.id = f"Node_{sequence_number}"
        SeqIO.write(r, outputs, "fasta")

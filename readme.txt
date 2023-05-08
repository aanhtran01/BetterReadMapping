
Faster Read Mapping
===================

A Python project that aligns donor reads to a reference genome by calculating a Burrows-Wheeler Transform using a Suffix Array. The Burrows-Wheeler-Transform is used along with the FM Index to recover read positions. A seed and extend method is used find potential alignments and the alignment with the best hamming distance is considered to be the best alignment. 

The project finds substitutions and indels outputs a "predictions.txt" of these mutations in this format:

>S455 A G
>S460 A G
>S718 C A
>S863 T G
>I413 G
>I624 G
>D281 T
>D544 C

The project also does its best filter out random sequencing errors. 

Deliverables:
-------------
betterreadmapping.py -- code for readmapping 

predictions.txt -- output after running project1b_1000000_reference_genome.fasta and  project1b_1000000_with_error_paired_reads.fasta 

predictions.zip -- zipped csv of predictions.txt


Usage
-----

To run the program, navigate to the project directory and run:

> python3 betterreadmapping.py reference_genome.fasta donor_reads.fasta 

The program takes the following arguments:

* `--reference_genome.fasta`: A fasta file of the reference_genome.
* `--donor_reads.fasta `: A fasta file of the donor_reads.

Examples
--------

Here is an example of how to run the program: 

>python3 betterreadmapping.py project1b_1000000_reference_genome.fasta project1b_1000000_with_error_paired_reads.fasta 


Performance
-----------

Program is very capable of handling reference genomes of 1 million nucleotides and ~200k reads. 

Runtime is based on laptop computer with the following specifications:
* Processor: 1.1 GHz Quad-Core Intel Core i5
* RAM: 8GB
* Operating System: MacOS Catalina 

For a reference genome of 1 million nucleotides and ~200k donor reads, the run time is:

real	3m28.779s
user	3m26.618s
sys	0m1.761s


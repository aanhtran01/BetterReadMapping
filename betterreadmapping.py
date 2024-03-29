2# -*- coding: utf-8 -*-

from collections import defaultdict
import pandas as pd
import numpy as np
import io
import re
import difflib
import pdb
import argparse
import sys
import queue
import numpy as np
from copy import deepcopy

#set up a command line interface with argparse, create argparse objects
parser = argparse.ArgumentParser(description='Process reference and donor files.')
parser.add_argument('reference_file', type=str, help='path to reference file')
parser.add_argument('donor_file', type=str, help='path to donor file')

args = parser.parse_args()

reference_file = args.reference_file
donor_file = args.donor_file


# Open the reference file and extract the DNA sequence
with open(reference_file) as f:
    # Read the file
    lines = f.readlines()
    # Remove newlines and any leading/trailing spaces
    lines = [line.strip() for line in lines]
    # Concatenate the DNA sequence lines
    reference_genome = "".join(lines[1:])

# Append the "$" symbol to the end of the genome
reference_genome += "$"

#define kmer size
k = 16
kmer_size = 16

# Print the output in the desired format
#output_file = 'predictions1000.txt'
output_file = 'predictions.txt'



#BurrowsWheeler  Construction

class suffix_array:
    def __init__(self, text):
        # Constructor that builds the suffix array for a given text string
        self.suff_arr = self._make_suffix_array(text)


    def _sort_array(self, S):
        # Method that sorts the characters of the string S
        l = len(S)
        arrangement = [0] * l
        num = dict()
        
        # Count the occurrences of each character in S
        for i in range(l):
            num[S[i]] = num.get(S[i], 0) + 1
        
        # Sort the characters in ascending arrangement
        char_list = sorted(num.keys())
        
        # Compute the starting position of each character in the sorted arrangement
        prev_char = char_list[0]
        for char in char_list[1:]:
            num[char] += num[prev_char]
            prev_char = char
        
        # Compute the arrangement of each suffix based on the starting character
        for i in range(l-1, -1, -1):
            c = S[i]
            num[c] = num[c] - 1
            arrangement[num[c]] = i
        
        return arrangement

    def class_character_arrangement(self, S, arrangement):
        # Method that computes the character classes for each position in the suffix array
        l = len(S)
        class_characters = [0] * l
        class_characters[arrangement[0]] = 0
        
        # Assign the class to each suffix based on whether the starting character is the same as the previous suffix
        for i in range(1, l):
            if S[arrangement[i]] != S[arrangement[i-1]]:
                class_characters[arrangement[i]] = class_characters[arrangement[i-1]] + 1
            else:
                class_characters[arrangement[i]] = class_characters[arrangement[i-1]]
        
        return class_characters

    def _double_suffix_sort(self, S, L, arrangement, class_characters):
        # Method that sorts the doubled suffixes
        string_length = len(S)
        num = [0] * string_length
        new_arrangement = [0] * string_length
        
        # Count the occurrences of each class in the first half of the doubled suffixes
        for i in range(string_length):
            num[class_characters[i]] += 1
        
        # Compute the starting position of each class in the sorted arrangement
        for j in range(1, string_length):
            num[j] += num[j-1]
        
        # Sort the doubled suffixes based on their second half
        for i in range(string_length-1, -1, -1):
            start = (arrangement[i]-L+string_length) % string_length
            cl = class_characters[start]
            num[cl] -= 1
            new_arrangement[num[cl]] = start
        
        return new_arrangement
    
    def _update_classes(self, new_arrangement, class_characters, L):
      # This function updates the character classes based on a new arrangement of indices.
      # new_arrangement: the new arrangement of indices for the string
      # class_characters: a list containing the character classes of the string
      # L: the length of substrings used for sorting
    
      n = len(new_arrangement)
     # n is the length of the new arrangement
    
      class_new = [0] * n
      # Create a new list of character classes with n elements initialized to 0
    
      class_new[new_arrangement[0]] = 0
      # The character class of the first element in the new arrangement is always 0
    
      for i in range(1, n):
          prev = new_arrangement[i-1]
          curr = new_arrangement[i]
          mid = curr + L
          mid_prev = (prev + L) % n
          # Define curr, prev, mid, and mid_prev for easier readability
        
          # Compare the character classes of two adjacent elements in the new arrangement
          # and two adjacent substrings starting at those elements, respectively.
          # If they're different, increment the character class.
          if class_characters[curr] != class_characters[prev] or class_characters[mid] != class_characters[mid_prev]:
              class_new[curr] = class_new[prev] + 1
          else:
              class_new[curr] = class_new[prev]
    
      # Return the updated character classes
      return class_new
    
    def _make_suffix_array(self, S):
      # This function builds the suffix array for a given string S
      # S: the input string
    
      string_length = len(S)
      # The length of S
    
      arrangement = self._sort_array(S)
      # Sort the characters of S and store the resulting arrangement
    
      class_characters = self.class_character_arrangement(S, arrangement)
      # Compute the character classes of S and store them
    
      L = 1
      while L < string_length:
          arrangement = self._double_suffix_sort(S, L, arrangement, class_characters)
          class_characters = self._update_classes(arrangement, class_characters, L)
          L = 2 * L
      # Repeat the process with longer substrings until L >= string_length.
    
      # Return the final suffix array
      return arrangement


    def get_suffix_array(self):
      # This function returns the suffix array of the input string.
    
      return self.suff_arr
      # Return the suffix array stored in self.sa


class BurrowsWheeler:
    def __init__(self, reference_genome):
        self.burrows_wheeler = self.burrows_wheelerFromsuffix_array(reference_genome)
    # Initialize the BurrowsWheeler by calling burrows_wheelerFromsuffix_array with a reference genome
    
    def _input(self):
        return sys.stdin.readline().strip()
    # A helper function to read input
    
    def burrows_wheelerTransform(self, text):
        # This function calculates the Burrows-Wheeler Transform
        # text: the input string
        
        # Generate all possible transfrom of the input string
        transfrom = [text[i:]+text[:i] for i in range(len(text))]
        # Sort the transfrom lexicographically and concatenate their last characters
        burrows_wheeler = ''.join([m[-1] for m in sorted(transfrom)])
        
        return burrows_wheeler

    def burrows_wheelerFromsuffix_array(self, text):
       # This function calculates the Burrows-Wheeler Transform using suffix arrays.
        suff_arr = suffix_array(text).get_suffix_array()
        return ''.join([text[(suff_arr[i]+len(text)-1)%len(text)] for i in range(len(text))])


def HammingDistance(seq1, seq2):
    return len([i for i in range(len(seq1)) if seq1[i] != seq2[i]])


#compute the FirstOccurrence array and CountSymbol function
def FirstOccurrence_CountSymbol(burrows_wheeler, alphabet = ['$', 'A', 'C', 'G', 'T']):
    l = len(burrows_wheeler)
    CountSymbol = dict()
    first_occurances = dict()
    for char in alphabet:
        CountSymbol[char] = [0] * (l + 1)
    for i in range(l):
        currChar = burrows_wheeler[i]
        for char, count in CountSymbol.items():
            CountSymbol[char][i+1] = CountSymbol[char][i]
        CountSymbol[currChar][i+1] += 1
    currIndex = 0
    for char in sorted(alphabet):
        first_occurances[char] = currIndex
        currIndex += CountSymbol[char][l]
    return first_occurances, CountSymbol


#perform pattern matching in a Burrows-Wheeler transformed string
#using the better Burrows-Wheeler matching algorithm
def BetterBWMatching(suff_arr, pattern, burrows_wheeler, starts, counts):
    occs = set()
    top = 0
    bottom = len(burrows_wheeler) - 1
    currIndex = len(pattern) - 1
    while top <= bottom:
        if currIndex >= 0:
            symbol = pattern[currIndex]
            currIndex -= 1
            if counts[symbol][bottom+1] - counts[symbol][top] > 0:
                top = starts[symbol] + counts[symbol][top]
                bottom = starts[symbol] + counts[symbol][bottom+1] - 1
            else:
                break
        else:
            for i in range(top, bottom + 1):
                occs.add(suff_arr[i])
            break

    return occs

#function to read in donor reads fasta file
def read_fasta_file(filename):
    with open(filename, 'r') as f:
        donor_id = None
        donor_seq = ""
        for line in f:
            if line.startswith(">"):
                if donor_id is not None:
                    yield (donor_id, donor_seq)
                donor_id = line.strip()[1:]
                donor_seq = ""
            else:
                donor_seq += line.strip()
        if donor_id is not None:
            yield (donor_id, donor_seq)

#function to align a single read to a genome
def align_read_to_genome(read, reference_genome, k, suffix_array, burrows_wheeler, starts, counts):

    # Step 1: Break the read into k-mers
    kmers = [read[i:i+k] for i in range(len(read)-k+1)]
    #first_kmer = kmers[0]


    # Step 2: Search for matches in the BurrowsWheeler  index and extend the alignment
    best_match = None
    best_score = float('inf')
    for i, kmer in enumerate(kmers):
        positions = BetterBWMatching(suffix_array, kmer, burrows_wheeler, starts, counts)

        for pos in positions:
            # extend the alignment
            offset = i
            alignment_start = pos - offset
            alignment_end = alignment_start + len(read)
            if alignment_start < 0 or alignment_end > len(reference_genome):
                continue # alignment out of bounds, skip to next position
            ref_sequence = reference_genome[alignment_start:alignment_end]
            score = HammingDistance(read, ref_sequence)

            # check if this is the best match so far
            if score < best_score:
                best_score = score
                best_match = alignment_start

    return best_match, best_score

#function to alogn all reads to the genome
def align_all_reads_to_genome(suffix_array, donor_reads, reference_genome, k, burrows_wheeler, starts, counts):
    results = []
    for read_id, read_seq in donor_reads:
        best_match, best_score = align_read_to_genome(read_seq, reference_genome, k, suffix_array, burrows_wheeler, starts, counts)
        results.append({'donor_read_id': read_id,'sequence' : read_seq ,'best_match': best_match, 'best_score': best_score})
    return results

#function to find substitutions
def find_subs(reference_genome, results):
    substitutions = []
    for read in results:
        if 'best_score' in read and read['best_score'] <= 3:  # Filter by best match score
            read_seq = read['sequence']
            best_match = read['best_match']
            if isinstance(best_match, int):
                best_match = [best_match]
            for read_pos in best_match:
                for i in range(len(read_seq)):
                    if read_pos + i >= len(reference_genome):
                        break  # end of genome sequence reached
                    if read_seq[i] != reference_genome[read_pos + i]:
                        substitution = {
                            'read_id': read['donor_read_id'],
                            'read_pos': read_pos + i,
                            'ref_nucleotide': reference_genome[read_pos + i],
                            'donor_nucleotide': read_seq[i]
                        }
                        substitutions.append(substitution)
    return substitutions

#function to filter out errors by enforcing a threshold
def get_base_counts(substitutions, ratio_threshold):
    base_counts = {}
    for sub in substitutions:
        if sub['read_pos'] not in base_counts:
            base_counts[sub['read_pos']] = {'A': 0, 'C': 0, 'G': 0, 'T': 0, 'total': 0}
        base_count = base_counts[sub['read_pos']]
        base_count[sub['donor_nucleotide']] += 1
        base_count['total'] += 1

    # Filter out positions with total base count of two or less
    base_counts = {pos: counts for pos, counts in base_counts.items() if counts['total'] > 2}

    # Filter out reads that don't qualify for the threshold
    for pos, counts in base_counts.items():
        total_count = counts['total']
        min_count = total_count * ratio_threshold
        counts = {base: count for base, count in counts.items() if base != 'total' and count >= min_count}
        base_counts[pos] = counts

    return base_counts

#function to print subs
def print_base_substitutions(ref_genome, base_counts, output_file):
    with open(output_file, 'w') as f:
        for pos, counts in base_counts.items():
            ref_base = ref_genome[pos]
            for base, count in counts.items():
                if base != 'total' and count > 0:
                    f.write(f">S{pos} {ref_base} {base}\n")

#function to calculate the distance between two positions in the reference genome for insertions and deletions
def calculate_distance(pos1, pos2, kmer_size, indels, read):
    """
    Calculate the distance between two positions in the reference genome.
    """
    for p1 in pos1:
        for p2 in pos2:
            distance = abs(p2 - p1)
            if distance == (2 * kmer_size + 1):
                if read not in indels:
                    indels[read] = []
                indels[read].append(('deletion', p1 + 16))  # Append pos1 + 16 to indels[read]
            elif distance == (2 * kmer_size - 1):
                if read not in indels:
                    indels[read] = []
                indels[read].append(('insertion', p1 + 16))  # Append pos1 + 16 to indels[read]
    return

#function to find indels using the L/3 middle segment method
def find_indels(results, kmer_size, suffix_array, burrows_wheeler, starts, counts, reference_genome):
    indels = {}  # Initialize an empty dictionary for storing indels
    for read in results:
        donor_read = read['sequence']
        read_id = read['donor_read_id']

        seq_len = len(donor_read)
        
        if seq_len != 50:
          continue 
       
        substring1 = donor_read[0:kmer_size]
        substring2 = donor_read[kmer_size:2*kmer_size]
        substring3 = donor_read[2*kmer_size:3*kmer_size]

        # Find the position of substring1 in the reference genome using BetterBWMatching
        pos1 = set()
        occs1 = BetterBWMatching(suffix_array, substring1, burrows_wheeler, starts, counts)
        #print(occs1)
        for occ in occs1:
            if occ + kmer_size <= len(reference_genome):
                pos1.add(occ)
                break
        if not pos1:
            continue

        # Find the position of substring3 in the reference genome using BetterBWMatching
        pos3 = set()
        occs3 = BetterBWMatching(suffix_array, substring3, burrows_wheeler, starts, counts)
        #print(occs3)
        for occ in occs3:
            if occ + kmer_size <= len(reference_genome):
                pos3.add(occ)
                break
        if not pos3:
            continue

        calculate_distance(pos1, pos3, kmer_size, indels, read_id)  # Pass kmer_size, indels, and read_id to calculate_distance
      
    return indels


def print_indels(indels):
    for read, indel_list in indels.items():
        print("Read:", read)
        for indel in indel_list:
            indel_type, pos = indel
            print("Indel Type:", indel_type)
            print("Position:", pos)
            print() 


#compare indel list with reference genome to find the insertion or deletion nucleotide
def check_true_indel(reference_genome, results, indels, kmer_size):
    true_indels = {}

    for read, indel_list in indels.items():
        don_sub = None  # Define don_sub with a default value of None
        for result in results:
            if result['donor_read_id'] == read:
                don_seq = result['sequence']
                don_sub = don_seq[kmer_size : 2*kmer_size]
                break  # Exit the loop once the read is found
        else:
            don_sub = ''  # Define don_sub as an empty string if the read is not found

        for indel in indel_list:
            indel_type, pos = indel
            ref_pos = pos  # Calculate the position in the reference genome
            ref_sub = reference_genome[ref_pos : ref_pos + kmer_size]

            # Generate the diff output using ndiff
            diff = difflib.ndiff(ref_sub, don_sub)

            count = 0

            for idx, line in enumerate(diff):
                if indel_type == "deletion":
                    if line.startswith('-'):
                        count += 1
                elif indel_type == "insertion":      
                    if line.startswith('+'):
                        count += 1

            if count == 1:
                diff_copy = difflib.ndiff(ref_sub, don_sub)  # Create a copy of diff
                for idx, line in enumerate(diff_copy):
                    if indel_type == "deletion":
                        if line.startswith('-'):
                            position = idx  # Calculate the position in the second string
                            true_indels.setdefault(read, []).append(('D', position + ref_pos - 1, line[1:]))
                    elif indel_type == "insertion":
                        if line.startswith('+'):
                            position = idx  # Calculate the position in the second string
                            true_indels.setdefault(read, []).append(('I', position + ref_pos - 1, line[2:]))

    return true_indels


def print_true_indels(true_indels, output_file):
    pos_counts = {}
    printed_pos = set()
    with open(output_file, 'a') as f:
        for read, indel_data in true_indels.items():
            for indel_type, pos, value in indel_data:
                pos_counts[pos] = pos_counts.get(pos, 0) + 1
                if pos_counts[pos] > 0 and pos not in printed_pos:
                    f.write(f">{indel_type}{pos} {value.strip()}\n")
                    printed_pos.add(pos)


#calling the functions
burrows_wheeler = BurrowsWheeler(reference_genome).burrows_wheeler
starts, counts = FirstOccurrence_CountSymbol(burrows_wheeler)
suffix_array = suffix_array(reference_genome).get_suffix_array()
donor_reads = read_fasta_file(donor_file)

results = align_all_reads_to_genome(suffix_array, donor_reads, reference_genome, k, burrows_wheeler, starts, counts)


subs = find_subs(reference_genome, results)

base_counts = get_base_counts(subs, 0.80)
print_base_substitutions(reference_genome, base_counts, output_file)

indels = find_indels(results, kmer_size, suffix_array, burrows_wheeler, starts, counts, reference_genome)

# Call the function and get the true indels dictionary
true_indels = check_true_indel(reference_genome, results, indels, kmer_size)
      
       
print_true_indels(true_indels, output_file)

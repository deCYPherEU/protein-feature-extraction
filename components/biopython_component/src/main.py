"""
The BiopythonComponent class is a component that takes in a dataframe, performs the Biopython functions to generate new features and returns the dataframe with the new features added.
"""
import logging
import pandas as pd
from fondant.component import PandasTransformComponent
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from Bio.SeqUtils import gc_fraction, CodonAdaptationIndex

# Set up logging
logger = logging.getLogger(__name__)

class BiopythonComponent(PandasTransformComponent):
	"""The BiopythonComponent class is a component that takes in a dataframe, performs the Biopython functions to generate new features and returns the dataframe with the new features added."""

	def __init__(self, *_):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The transform method takes in a dataframe, performs the Biopython functions to generate new features and returns the dataframe with the new features added."""

		sequence_analysis = dataframe["sequence"].apply(ProteinAnalysis)
		
		dataframe["sequence_length"] = sequence_analysis.apply(lambda x: x.length)
		dataframe["molecular_weight"] = sequence_analysis.apply(lambda x: x.molecular_weight())
		dataframe["aromaticity"] = sequence_analysis.apply(lambda x: x.aromaticity())
		dataframe["isoelectric_point"] = sequence_analysis.apply(lambda x: x.isoelectric_point())
		dataframe["instability_index"] = sequence_analysis.apply(lambda x: x.instability_index())
		dataframe["gravy"] = sequence_analysis.apply(lambda x: x.gravy())
		dataframe["flexibility_max"] = sequence_analysis.apply(lambda x: max(x.flexibility()))
		dataframe["flexibility_min"] = sequence_analysis.apply(lambda x: min(x.flexibility()))
		dataframe["flexibility_mean"] = sequence_analysis.apply(lambda x: sum(x.flexibility()) / len(x.flexibility()))
		dataframe["helix"] = sequence_analysis.apply(lambda x: x.secondary_structure_fraction()[0])
		dataframe["turn"] = sequence_analysis.apply(lambda x: x.secondary_structure_fraction()[1])
		dataframe["sheet"] = sequence_analysis.apply(lambda x: x.secondary_structure_fraction()[2])
		dataframe["charge_at_ph3"] = sequence_analysis.apply(lambda x: x.charge_at_pH(3.0))
		dataframe["charge_at_ph5"] = sequence_analysis.apply(lambda x: x.charge_at_pH(5.0))
		dataframe["charge_at_ph7"] = sequence_analysis.apply(lambda x: x.charge_at_pH(7.0))
		dataframe["charge_at_ph9"] = sequence_analysis.apply(lambda x: x.charge_at_pH(9.0))
		dataframe["molar_extinction_coefficient_oxidized"] = sequence_analysis.apply(lambda x: x.molar_extinction_coefficient()[0])
		dataframe["molar_extinction_coefficient_reduced"] = sequence_analysis.apply(lambda x: x.molar_extinction_coefficient()[1])

		dataframe = self.calculate_nucleotide_frequency(dataframe)
		dataframe = self.calculate_gc_content(dataframe)
		dataframe = self.calculate_codon_frequency(dataframe)
		dataframe = self.calculate_codon_usage_bias(dataframe)

		logger.info(f"BiopythonComponent: features generated: {dataframe.columns.tolist()}")
		return dataframe


	def calculate_nucleotide_frequency(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Calculate the frequency of each nucleotide in the sequence."""
		# Transcribe protein sequences to DNA sequences
		dna_sequences = dataframe["sequence"].apply(self.reverse_translate)
		
		# Define the nucleotides
		nucleotides = "ACGT"
		
		# Calculate the nucleotide frequency for each sequence
		nucleotide_frequencies = []
		for sequence in dna_sequences:
			nucleotide_count = {nucleotide: sequence.count(nucleotide) for nucleotide in nucleotides}
			total_nucleotides = sum(nucleotide_count.values())
			nucleotide_frequency = {nucleotide: count / total_nucleotides for nucleotide, count in nucleotide_count.items()}
			nucleotide_frequencies.append(nucleotide_frequency)

		# Add the nucleotide frequency to the dataframe
		for nucleotide in nucleotides:
			dataframe[f"{nucleotide}_frequency"] = [freq[nucleotide] for freq in nucleotide_frequencies]

		return dataframe
	
	def calculate_gc_content(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Calculate the GC content of the sequence."""
		# Transcribe protein sequence to DNA sequence
		dna_sequences = dataframe["sequence"].apply(self.reverse_translate)

		# Calculate the GC content for each sequence
		gc_content = dna_sequences.apply(gc_fraction)

		# Add the GC content to the dataframe
		dataframe["gc_content"] = gc_content

		return dataframe
	
	def calculate_codon_frequency(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Calculate the frequency of each codon in the sequence."""
		# Transcribe protein sequences to DNA sequences using the reverse translation method
		dna_sequences = dataframe["sequence"].apply(self.reverse_translate)

		condon_frequencies_dict = CodonAdaptationIndex(dna_sequences)

		for codon, freq in condon_frequencies_dict.items():
			dataframe[f"{codon}_frequency"] = freq
		
		return dataframe
	
	def calculate_codon_usage_bias(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Calculate the codon usage bias of the sequence."""
		# Transcribe protein sequences to DNA sequences using the reverse translation method
		dna_sequences = dataframe["sequence"].apply(self.reverse_translate)

		codon_usage_bias_dict = CodonAdaptationIndex(dna_sequences)

		for codon, bias in codon_usage_bias_dict.items():
			dataframe[f"{codon}_usage_bias"] = bias
		
		return dataframe
	
	def reverse_translate(self, protein_sequence: str) -> str:
		"""Reverse translate a protein sequence to a DNA sequence."""

		codon_table = {
			'A': ['GCT', 'GCC', 'GCA', 'GCG'],
			'C': ['TGT', 'TGC'],
			'D': ['GAT', 'GAC'],
			'E': ['GAA', 'GAG'],
			'F': ['TTT', 'TTC'],
			'G': ['GGT', 'GGC', 'GGA', 'GGG'],
			'H': ['CAT', 'CAC'],
			'I': ['ATT', 'ATC', 'ATA'],
			'K': ['AAA', 'AAG'],
			'L': ['TTA', 'TTG', 'CTT', 'CTC', 'CTA', 'CTG'],
			'M': ['ATG'],
			'N': ['AAT', 'AAC'],
			'P': ['CCT', 'CCC', 'CCA', 'CCG'],
			'Q': ['CAA', 'CAG'],
			'R': ['CGT', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG'],
			'S': ['TCT', 'TCC', 'TCA', 'TCG', 'AGT', 'AGC'],
			'T': ['ACT', 'ACC', 'ACA', 'ACG'],
			'V': ['GTT', 'GTC', 'GTA', 'GTG'],
			'W': ['TGG'],
			'Y': ['TAT', 'TAC'],
			'*': ['TAA', 'TAG', 'TGA']  # Stop codons
		}
		
		dna_sequence = ""
		for amino_acid in protein_sequence:
			if amino_acid not in codon_table:
				raise ValueError(f"Amino acid '{amino_acid}' not found in codon table.")
			possible_codons = codon_table[amino_acid]
			# Select a random codon for simplicity (can be optimized based on codon usage bias)
			codon = possible_codons[0]
			dna_sequence += codon
		return dna_sequence

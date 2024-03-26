"""
The UniKP component uses the UniKP framework to predict kinetic properties (Km, Kcat and Vmax) of a protein sequence and a ligand SMILES string. The results will be presented as a JSON, but in a string format for easy storage and retrieval in the dataframe.
"""
import logging
import pandas as pd
from fondant.component import PandasTransformComponent
from typing import Dict, List, Any, Tuple
import pickle
import math
import re
import gc
import torch
from utils import split
from build_vocab import WordVocab
from pretrain_trfm import TrfmSeq2seq
from transformers import T5EncoderModel, T5Tokenizer
import numpy as np
import os

# Set up logging
logger = logging.getLogger(__name__)


class UniKPComponent(PandasTransformComponent):
	"""The UniKP component uses the UniKP framework to predict kinetic properties (Km, Kcat and Vmax) of a protein sequence and a ligand SMILES string. The results will be presented as a JSON, but in a string format for easy storage and retrieval in the dataframe."""

	def __init__(self, protein_smiles_path: str):
		"""Initialize the UniKP component."""
		
		# tokenization and model loading
		self.tokenizer = T5Tokenizer.from_pretrained(
			"Rostlab/prot_t5_xl_half_uniref50-enc", do_lower_case=False, torch_dtype=torch.float16)
		self.model = T5EncoderModel.from_pretrained(
			"Rostlab/prot_t5_xl_half_uniref50-enc")

		# paths to the vocab and trfm model
		vocab_path = "vocab.pkl"
		trfm_path = "trfm_12_23000.pkl"

		# load vocab
		self.vocab = WordVocab.load_vocab(vocab_path)

		# load trfm model
		device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
		self.trfm = TrfmSeq2seq(len(self.vocab), 256, len(self.vocab), 4).to(device)
		self.trfm.load_state_dict(torch.load(trfm_path, map_location=device))
		self.trfm = TrfmSeq2seq(len(self.vocab), 256, len(self.vocab), 4)
		self.trfm.load_state_dict(torch.load(trfm_path))
		self.trfm.eval()

		# paths to the pretrained models
		self.Km_model_path = "Km.pkl"
		self.Kcat_model_path = "Kcat.pkl"
		self.Kcat_over_Km_model_path = "Kcat_over_Km.pkl"

		# paths to the json file of the proteins and smiles
		self.protein_smiles_path = protein_smiles_path

		self.pad_index = 0
		self.unk_index = 1
		self.eos_index = 2
		self.sos_index = 3

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Apply the UniKP component to the input dataframe."""

		logger.info(os.listdir())

		return dataframe
	
	def predict_feature_using_model(self, X: np.array, model_path: str) -> np.array:
		"""
		Function to predict the feature using the pretrained model.
		"""
		with open(model_path, "rb") as f:
			model = pickle.load(f)
		pred_feature = model.predict(X)
		pred_feature_pow = [math.pow(10, pred_feature[i])
							for i in range(len(pred_feature))]
		return pred_feature_pow

	def smiles_to_vec(self, Smiles: str) -> np.array:
		"""
		Function to convert the smiles to a vector using the pretrained model.
		"""

		# UniKP needs the SMILES to be a list.
		Smiles = [Smiles]

		x_split = [split(sm) for sm in Smiles]
		xid, xseg = self.get_array(x_split, self.vocab)
		X = self.trfm.encode(torch.t(xid))
		return X

	def get_inputs(self, sm: str, vocab: WordVocab) -> Tuple[List[int], List[int]]:
		"""
		Convert smiles to tensor
		"""
		seq_len = len(sm)
		sm = sm.split()
		ids = [vocab.stoi.get(token, self.unk_index) for token in sm]
		ids = [self.sos_index] + ids + [self.eos_index]
		seg = [1]*len(ids)
		padding = [self.pad_index]*(seq_len - len(ids))
		ids.extend(padding), seg.extend(padding)
		return ids, seg

	def get_array(self, smiles: list[str], vocab: WordVocab) -> Tuple[torch.tensor, torch.tensor]:
		"""
		Convert smiles to tensor
		"""
		x_id, x_seg = [], []
		for sm in smiles:
			a,b = self.get_inputs(sm, vocab)
			x_id.append(a)
			x_seg.append(b)
		return torch.tensor(x_id), torch.tensor(x_seg)

	def Seq_to_vec(self, Sequence: str) -> np.array:
		"""
		Function to convert the sequence to a vector using the pretrained model.
		"""

		# UniKP needs the sequence to be a list.
		Sequence = [Sequence]

		sequences_Example = []
		for i in range(len(Sequence)):
			zj = ''
			for j in range(len(Sequence[i]) - 1):
				zj += Sequence[i][j] + ' '
			zj += Sequence[i][-1]
			sequences_Example.append(zj)
		
		gc.collect()
		print(torch.cuda.is_available())
		device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
		
		self.model = self.model.to(device)
		self.model = self.model.eval()
		
		features = []
		for i in range(len(sequences_Example)):
			sequences_Example_i = sequences_Example[i]
			sequences_Example_i = [re.sub(r"[UZOB]", "X", sequences_Example_i)]
			ids = self.tokenizer.batch_encode_plus(sequences_Example_i, add_special_tokens=True, padding=True)
			input_ids = torch.tensor(ids['input_ids']).to(device)
			attention_mask = torch.tensor(ids['attention_mask']).to(device)
			with torch.no_grad():
				embedding = self.model(input_ids=input_ids, attention_mask=attention_mask)
			embedding = embedding.last_hidden_state.cpu().numpy()
			for seq_num in range(len(embedding)):
				seq_len = (attention_mask[seq_num] == 1).sum()
				seq_emd = embedding[seq_num][:seq_len - 1]
				features.append(seq_emd)

		features_normalize = np.zeros([len(features), len(features[0][0])], dtype=float)
		for i in range(len(features)):
			for k in range(len(features[0][0])):
				for j in range(len(features[i])):
					features_normalize[i][k] += features[i][j][k]
				features_normalize[i][k] /= len(features[i])
		return features_normalize

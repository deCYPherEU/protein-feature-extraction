"""
DeepTMpred model taken from the DeepTMpred repository
https://github.com/ISYSLAB-HUST/DeepTMpred
"""

import re

import torch  # pylint: disable=import-error
from torch.utils.data import DataLoader  # pylint: disable=import-error

from deepTMpred.model import FineTuneEsmCNN, OrientationNet  # pylint: disable=import-error
from deepTMpred.utils import load_model_and_alphabet_core  # pylint: disable=import-error
from deepTMpred.data import FineTuneDataset, batch_collate  # pylint: disable=import-error


def data_iter(data_path, pssm_dir, hmm_dir, batch_converter, label=False):
	"""
	Iterate over the data and return the data loader
	"""
	data = FineTuneDataset(data_path, pssm_dir=pssm_dir,
						hmm_file=hmm_dir, label=label)
	test = DataLoader(data, len(data), collate_fn=batch_collate(
		batch_converter, label=label))
	return test


def tmh_predict(id_list, predict_str, prob, orientation):
	"""
	Predict the transmembrane helices
	"""
	cutoff = 5
	for _id, predict, prob, ori in zip(id_list, predict_str, prob, orientation):  # pylint: disable=unused-variable,redefined-argument-from-local
		tmp = []
		predict = map(str, predict)
		for item in re.finditer(r'1+', ''.join(predict)):
			if (item.end()-item.start()-1) >= cutoff:
				tmp.append([item.start()+1, item.end()])
	return tmp


def test_model(model, orientation_model, test_loader, device):  # pylint: disable=too-many-locals
	"""
	Test the model
	"""
	model.eval()
	with torch.no_grad():  # pylint: disable=too-many-locals
		for tokens, _ids, matrix, token_lengths in test_loader:
			tokens = tokens.to(device)
			results = model.esm(tokens, repr_layers=[
								12], return_contacts=False)
			token_embeddings = results["representations"][12][:, 1:, :]
			token_lengths = token_lengths.to(device)
			matrix = matrix.to(device)
			embedings = torch.cat((matrix, token_embeddings), dim=2)
			predict_list, prob = model.predict(embedings, token_lengths)
			orientation_out = orientation_model(embedings)
			predict = torch.argmax(orientation_out, dim=1)
			tmh_dict = tmh_predict(_ids, predict_list, prob, predict.tolist())
	return tmh_dict


def deeptmpred(test_file, tmh_model_path, orientation_model_path):
	"""
	Run the DeepTMpred model
	"""
	device = torch.device('cpu')

	model = FineTuneEsmCNN(768)
	args_dict = torch.load('./args.pt')
	pretrain_model, alphabet = load_model_and_alphabet_core(args_dict)
	batch_converter = alphabet.get_batch_converter()
	model.add_module('esm', pretrain_model.to(device))
	model.load_state_dict(torch.load(tmh_model_path))
	model = model.to(device)

	orientation_model = OrientationNet()
	orientation_model.load_state_dict(torch.load(orientation_model_path))
	orientation_model = orientation_model.to(device)

	test_iter = data_iter(test_file, None, None, batch_converter, label=False)
	topo = test_model(model, orientation_model, test_iter, device)
	return topo

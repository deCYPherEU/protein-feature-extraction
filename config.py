import pandas as pd

MOCK_DATA_PATH_LOCAL = "./data/mock_data.parquet"
MOCK_DATA_PATH_FONDANT = MOCK_DATA_PATH_LOCAL[1:] # removes the dot

def generate_mock_data() -> None:
	data = {
		'sequence': [
			'MKTITLEVAVLAALLVLASATVA',
			'MKLITVLLLAVALAGVSKQIAG',
			'MKIFVALLVATLVWSKFIA',
			'MKALSKFNLSAKVNALKAASVNSA',
			'MKSLAISVNLSANVAISVNLSAASANS'
		],
		'name': ['Seq1', 'Seq2', 'Seq3', 'Seq4', 'Seq5']    
	}

	df = pd.DataFrame(data)
	df.to_parquet(MOCK_DATA_PATH_LOCAL, index=False)

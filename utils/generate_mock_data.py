import pandas as pd
from config import MOCK_DATA_PATH_LOCAL

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

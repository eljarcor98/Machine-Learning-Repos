import pandas as pd
from pathlib import Path

class UNSWLoader:
    """
    Utility class for loading and preprocessing the UNSW-NB15 dataset.
    """
    
    def __init__(self, data_dir='data/raw/unsw-nb15'):
        self.data_dir = Path(data_dir)
        self.features_file = self.data_dir / 'NUSW-NB15_features.csv'
        self.column_names = self._load_column_names()
        
    def _load_column_names(self):
        """Loads column names from the features file."""
        if not self.features_file.exists():
            raise FileNotFoundError(f"Features file not found: {self.features_file}")
            
        # The features file is likely latin-1 encoded
        try:
            df_features = pd.read_csv(self.features_file, encoding='latin-1')
        except UnicodeDecodeError:
            df_features = pd.read_csv(self.features_file, encoding='cp1252')
            
        # Clean column names
        names = df_features['Name'].str.strip().tolist()
        return names

    def get_data_files(self):
        """Returns a list of the 4 main data files."""
        return sorted(list(self.data_dir.glob('UNSW-NB15_[1-4].csv')))

    def load_file(self, file_index=1, nrows=None):
        """
        Loads a specific CSV file (1-4) from the dataset.
        """
        file_path = self.data_dir / f'UNSW-NB15_{file_index}.csv'
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
            
        print(f"Reading {file_path.name}...")
        df = pd.read_csv(file_path, names=self.column_names, header=None, nrows=nrows, low_memory=False)
        return df

    def load_consolidated_sample(self, nrows_per_file=100000):
        """
        Loads a sample from each of the 4 files and concatenates them.
        """
        data_files = self.get_data_files()
        dfs = []
        for f in data_files:
            print(f"Reading sample from {f.name}...")
            df = pd.read_csv(f, names=self.column_names, header=None, nrows=nrows_per_file, low_memory=False)
            dfs.append(df)
            
        return pd.concat(dfs, ignore_index=True)

if __name__ == "__main__":
    # Test loader
    loader = UNSWLoader('../../data/raw/unsw-nb15')
    sample = loader.load_file(1, nrows=5)
    print(sample.head())

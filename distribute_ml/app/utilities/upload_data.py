import pandas as pd, os, boto3, uuid
from pandas import DataFrame
from botocore.exceptions import NoCredentialsError
from ...conf.base import BaseConfig

def extract_filename(filename: str) -> str:
    strip_slash: list[str] = filename.split("/")
    if not strip_slash[-1]: 
        print("Error on stripping slash")
        return 'data'
    filename: str = strip_slash[-1] 
    strip_extension: list[str] = filename.split(".")
    if not strip_extension[0]: 
        print("Error on stripping extension")
        return 'data'
    return strip_extension[0]    

# def extract_filename(file: str) -> str:
#     filename = os.path.basename(file)
#     return filename

def save_chunk(new_filename: str, df: DataFrame, start: int, end: int):
    filefolder = "data/"            
    df.iloc[start: end].to_csv(os.path.join(filefolder, new_filename), index=False)
      

class CreateDataPartitions:
    def __init__(self, record_id: str, filename: str, partitions: int, train_split: int, test_split: int, validation_split: int):
        self.filename: str = filename
        self.record_id = record_id
        self.n: int = partitions    
        self.train_split = train_split
        self.test_split = test_split
        self.validation_split = validation_split
        self.new_filename_list: list = [] 

        baseconfig = BaseConfig()
        access_keys = baseconfig.get_s3_access()
        self.__access_key_id: str = access_keys[0]
        self.__secret_access_key: str = access_keys[1]        
    
    def get_new_filename_list(self) -> list[tuple]:
        return_list = []        
        for file in self.new_filename_list:
            filename = file[0]
            id = file[1]
            return_list.append((os.path.basename(filename), id))
        print("Return List:", return_list)
        return return_list


    def split_data(self) -> list[str]: 
        "Splits file into n partitions and returns filename in a list"

        try:
            df: DataFrame = pd.read_csv(self.filename)
            total_train_rows = int(len(df) * self.train_split)
            chunk_size: int = (total_train_rows) // self.n
            print("Df length:", len(df))
            print("Total_Train_Rows:", total_train_rows)
            new_filename_list: list[str] = []
            for i in range(self.n):
                start: int = int(i * chunk_size)
                end: int = int((i + 1) * chunk_size) if i < self.n - 1 else total_train_rows
                new_filename = f"{extract_filename(self.filename)}_chunk_{i + 1}.csv"

                print(f"Data split {i + 1}:", start, end)
                # First save data on local and then take them on and push                
                save_chunk(new_filename, df, start, end)            

                new_filename_list.append(new_filename)
            self.new_filename_list = new_filename_list

            # Split test and validation            
            start_test_split = int(self.train_split * len(df))
            end_test_split = start_test_split + int(self.test_split * len(df))
            print("Test split", start_test_split, end_test_split)
            new_test_filename = f"test_chunk_1.csv"
            save_chunk(new_test_filename, df, start_test_split, end_test_split)         

            start_validate_split = end_test_split
            end_validate_split = len(df)
            print("Validation split", start_validate_split, end_validate_split)
            new_validate_filename = f"validate_chunk_1.csv"
            save_chunk(new_validate_filename, df, start_validate_split, end_validate_split)         
            new_filename_list.append(new_test_filename)
            new_filename_list.append(new_validate_filename)
            return new_filename_list

        except Exception as e:
            print("Error in splitting data:", e)      

    def push_data_to_cloud(self):
        # Initialize s3 client
        s3_client = boto3.client(
            's3', 
            aws_access_key_id = self.__access_key_id, 
            aws_secret_access_key = self.__secret_access_key
        )

        # bucket info
        bucket_name = "paritioned-data-bucket"

        # filedetails
        filelist = []
        filefolder = "data"
        for file in self.new_filename_list:
            filelist.append(os.path.join(filefolder, file))
        
        # Upload files
        for idx, file in enumerate(filelist):
            # UUIDs for data chunks and record_id for test and validate data
            if idx < len(filelist) - 2: header = uuid.uuid4()
            else: header = self.record_id
            object_name = f"{header}-{os.path.basename(file)}"
            try:
                s3_client.upload_file(file, bucket_name, object_name)
                self.new_filename_list[idx] = (file, object_name)
                print(f"Uploaded {file} to {bucket_name}/{object_name}")

            except Exception as e:
                print("Error in uploading file:", e)    

        self.new_filename_list.pop()
        self.new_filename_list.pop()

    

    def initiate(self):
        print("Splitting Data")
        self.split_data()
        print("Pushing Data to Cloud")
        self.push_data_to_cloud()
        # Delete files on loacl once successfulyy uploaded
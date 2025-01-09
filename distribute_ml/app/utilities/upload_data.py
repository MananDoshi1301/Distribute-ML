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
    def __init__(self, filename: str, partitions: int):
        self.filename: str = filename
        self.n: int = partitions    
        self.new_filename_list: list = [] 

        baseconfig = BaseConfig()
        access_keys = baseconfig.get_s3_access()
        self.__access_key_id: str = access_keys[0]
        self.__secret_access_key: str = access_keys[1]
    
    def get_new_filename_list(self) -> list[tuple]:
        return_list = []
        for file in enumerate(self.new_filename_list):
            filename = file[0]
            id = file[1]
            return_list.append((os.path.basename(filename), id))
            return return_list


    def split_data(self) -> list[str]: 
        "Splits file into n partitions and returns filename in a list"

        try:
            df: DataFrame = pd.read_csv(self.filename)
            chunk_size: int = len(df) // self.n

            new_filename_list: list[str] = []
            for i in range(self.n):
                start: int = i * chunk_size
                end: int = (i + 1) * chunk_size if i < self.n - 1 else len(df)
                new_filename = f"{extract_filename(self.filename)}_chunk_{i + 1}.csv"

                # First save data on local and then take them on and push                
                save_chunk(new_filename, df, start, end)            

                new_filename_list.append(new_filename)
            self.new_filename_list = new_filename_list
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
            object_name = f"{uuid.uuid4()}-{os.path.basename(file)}"
            try:
                s3_client.upload_file(file, bucket_name, object_name)
                self.new_filename_list[idx] = (file, object_name)
                print(f"Uploaded {file} to {bucket_name}/{object_name}")

            except Exception as e:
                print("Error in uploading file:", e)    

    def initiate(self):
        print("Splitting Data")
        self.split_data()
        print("Pushing Data to Cloud")
        self.push_data_to_cloud()
        # Delete files on loacl once successfulyy uploaded
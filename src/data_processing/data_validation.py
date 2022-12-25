import json, re, os, shutil, argparse, logging, random
from tqdm import tqdm
from src.utils.common import read_yaml, create_directories
from params import INPUT_FILE_NAME_REGEX
from configs.config import ARTIFACTS
import pandas as pd


class Raw_Data_Validation:
    """
        class Name: Raw_Data_Validation
        Description: This class handles validating the data from source before moveing it to local file storage.
        
        Written By: siddhartha shandilya
        Version: 1.0
        Revisions: None

    """
    def __init__(self, remote_data_path, valid_data_schema_path) -> None:
        self.remote_data_path=remote_data_path
        self.valid_data_schema_path=valid_data_schema_path
        self.good_data_dir = os.path.join(ARTIFACTS["ARTIFACTS_DIR"],ARTIFACTS["DATABASE_DIR"]["DATABASE"],ARTIFACTS["DATABASE_DIR"]["GOOD_DATA_DIR"])
        self.bad_data_dir = os.path.join(ARTIFACTS["ARTIFACTS_DIR"],ARTIFACTS["DATABASE_DIR"]["DATABASE"],ARTIFACTS["DATABASE_DIR"]["BAD_DATA_DIR"])

    def get_value_from_schema(self):
        """
                        Method Name: valuesFromSchema
                        Description: This method extracts all the relevant information from the pre-defined "Schema" file.
                        Output:filenName_pattern, LengthOfDateStampInFile, LengthOfTimeStampInFile, column_names, Number of Columns
                        On Failure: Raise ValueError,KeyError,Exception

                        Written By: Siddhartha Shandilya
                        Version: 1.0
                        Revisions: None
                        
        """
        logging.info("get_value_from_schema function from Raw_Data_Validation class is called")
        try:
            with open(self.valid_data_schema_path, 'r') as f:
                valid_schema = json.load(f)
                f.close()

            input_filename = valid_schema["SampleFileName"]
            LengthOfDateStampInFile = valid_schema["LengthOfDateStampInFile"]
            LengthOfTimeStampInFile = valid_schema["LengthOfTimeStampInFile"]
            NumberofColumns = valid_schema["NumberofColumns"]
            ColName = valid_schema["ColName"]

        except ValueError:
            logging.info("ValueError: No value found inside schema_training.json")
            raise ValueError

        except KeyError:
            logging.info("KeyError: Incorrect key passed")
            raise KeyError

        except Exception as e:
            logging.info(e)
            raise e

        logging.info("get_value_from_schema function successfully executed")
        return input_filename,LengthOfDateStampInFile,LengthOfTimeStampInFile,NumberofColumns,ColName


    def raw_file_validation(self,input_filename, LengthOfDateStampInFile, LengthOfTimeStampInFile):
        """
            Method Name: raw_file_validation
            Description: This method validates input filenname with pre-defined "Schema" file.
            Output:None
            On Failure: Exception

            Written By: Siddhartha Shandilya
            Version: 1.0
            Revisions: None
                        
        """
        remote_raw_file_name = os.path.join(self.remote_data_path, input_filename)
        
        create_directories([self.good_data_dir, self.bad_data_dir])
        logging.info("Running raw_file_name_validation function for validating the input filename")
        try:
            if(re.match(INPUT_FILE_NAME_REGEX, input_filename)):
                split_raw_file_name_at_dot = re.split(".csv",input_filename)
                split_raw_file_name_at_underscore = re.split("_",split_raw_file_name_at_dot[0])
                if(len(split_raw_file_name_at_underscore[1])==LengthOfDateStampInFile):
                    if(len(split_raw_file_name_at_underscore[2])==LengthOfTimeStampInFile):
                        logging.info("File name validated moving it to good data folder")
                        shutil.copy(src=remote_raw_file_name,dst=self.good_data_dir)
                        logging.info(f"File name validated moved, \n updated list of files it in good data folder:{os.listdir(self.good_data_dir)} ")
                        return 1
                    else:
                        logging.info("LengthOfTimeStampInFile not matched moving to bad data folder")
                        shutil.copy(src=remote_raw_file_name,dist=self.bad_data_dir)
                        return 0
                else:
                    logging.info("LengthOfDateStampInFile not matched moving to bad data folder")
                    shutil.copy(src=remote_raw_file_name,dist=self.bad_data_dir)
                    return 0
            else:
                logging.info("FileName not matched moving to bad data folder")
                shutil.copy(src=remote_raw_file_name,dist=self.bad_data_dir)
                return 0

        except Exception as e:
            logging.info(e)
        
    def raw_file_column_length_validation(self, NumberofColumns):
        """
            Method Name: raw_file_column_length_validation
            Description: This method validates input file column length with pre-defined "Schema" file.
            Output: 1 for validated files & 0 for invalid files
            On Failure: Exception

            Written By: Siddhartha Shandilya
            Version: 1.0
            Revisions: None
                        
        """
        logging.info("raw_file_column_length_validation from data vlidation class function called")
        try:
            for files in (os.listdir(self.good_data_dir)):
                raw_file_data = pd.read_csv(f"{self.good_data_dir}/{files}")
                if len(raw_file_data.columns) == NumberofColumns:
                    logging.info(f"{self.good_data_dir}/{files} has valid column length")
                    return 1
                else:
                    logging.info(f"{self.good_data_dir}/{files} has invalid column length moving file to bad data folder")
                    shutil.move(src = f"{self.good_data_dir}/{files}", dst=self.bad_data_dir)
                    return 0

        except Exception as e:
            logging.info(e)
            raise e



    def raw_file_column_name_validation(self, colName):
        """
            Method Name: raw_file_column_name_validation
            Description: This method validates input file column name with pre-defined "Schema" file.
            Output: 1 for validated files & 0 for invalid files
            On Failure: Exception

            Written By: Siddhartha Shandilya
            Version: 1.0
            Revisions: None
                        
        """

        logging.info("raw_file_column_name_validation function is called")
        colName_list = list(colName.keys())
        try:
            
            for file in os.listdir(self.good_data_dir):
                data = pd.read_csv(f"{self.good_data_dir}/{file}")
                extracted_data_columns = list(data.columns)
                for i in range (len(extracted_data_columns)):
                    if colName_list[i]!=extracted_data_columns[i]:
                        logging.info(f"Column name not matched at index {i} ")
                        return 0
            logging.info(f"raw_file_column_name is validated for file {self.good_data_dir}/{file}")
            return 1
        except Exception as e:
            logging.info(e)
            raise e



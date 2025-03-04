"""
Author: Marina Dolokov, Udacity
Date: December 2021

This script downloads the raw dataset from W&B, applies some basic data cleaning and exports the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd  
import os 


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):
    '''
    In this function the raw dataset is downloaded from W&B, 
    a basic data cleaning is done and the results are exported to a new artifact
    '''

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this particular version of the artifact
    logger.info("Download artifact")
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path) 

    # Drop outliers
    logger.info("Dropping outliers")
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    # drop rows in the dataset that are not in the proper geolocation
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    filename = "clean_sample.csv"
    df.to_csv(filename, index=False)

    artifact = wandb.Artifact(
        name=args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(filename)

    logger.info("Logging artifact")
    run.log_artifact(artifact)

    os.remove(filename)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This steps clean the data")


    parser.add_argument(
        "--input_artifact", 
        type= str, 
        help= "Name of input artifact", 
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type= str,
        help= "Name of output artifact", 
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type= str, 
        help= "Type of the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type= str, 
        help= "Description of the output artifact", 
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type= float, 
        help= "Minimal rental price", 
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type= float, 
        help= "Maximal rental price", 
        required=True
    )

    args = parser.parse_args()

    go(args)
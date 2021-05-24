#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd



logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    ######################
    # YOUR CODE HERE     #
    ######################
    logger.info(f"Fetching {args.input_artifact} from W&B...")
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Reading with pandas")
    df = pd.read_csv(artifact_local_path)


    # df['price'].describe(percentiles=[0.01, 0.05, 0.50, 0.95, 0.99])

    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx]

    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Fill the null dates with an old date
    df['last_review'].fillna(pd.to_datetime("2010-01-01"), inplace=True)

    # If the reviews_per_month is nan it means that there is no review
    df['reviews_per_month'].fillna(0, inplace=True)

    # We can fill the names with a short string.
    # DO NOT use empty strings here
    df['name'].fillna('-', inplace=True)
    df['host_name'].fillna('-', inplace=True)

    # idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    # df = df[idx]


    logger.info("Save the results to a CSV")
    df.to_csv("clean_sample.csv", index=False)

    logger.info("Uploading the cleaned file to W&B")
    
    artifact = wandb.Artifact(
         args.output_name,
         type=args.output_type,
         description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Fully-qualified name for the input artifact",
        required=True
    )

    parser.add_argument(
        "--output_name", 
        type=str,
        help="Name of the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Artifact type",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description of output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price",
        required=True
    )


    args = parser.parse_args()

    go(args)

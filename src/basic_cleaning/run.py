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

    # start data cleansing
    # Drop outliers
    logger.info("Filter prices ")
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx]

    # Convert last_review to datetime
    logger.info("Convert last_review to datetime and fill na ")
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Fill the null dates with an old date
    df['last_review'].fillna(pd.to_datetime("2010-01-01"), inplace=True)

    # If the reviews_per_month is nan it means that there is no review
    df['reviews_per_month'].fillna(0, inplace=True)

    # We can fill the names with a short string.
    # DO NOT use empty strings here
    df['name'].fillna('-', inplace=True)
    df['host_name'].fillna('-', inplace=True)

    # add filter for NYC
    logger.info("Filter for NYC based on coordinates")
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx]

    logger.info("Save Dataframe locally ")
    df.to_csv("clean_sample.csv", index=False)

    logger.info("Upload cleaned file")
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
        help="input_artifact: dataset from wandb",
        required=True
    )

    parser.add_argument(
        "--output_name",
        type=str,
        help="file name of the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="Define the type of the output artifact.",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Detailed description of the new generated artifact",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum price to consider as valid data point",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum price to consider as valid data point",
        required=True
    )

    args = parser.parse_args()

    go(args)

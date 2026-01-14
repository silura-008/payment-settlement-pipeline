import json
import boto3
from botocore.exceptions import ClientError
import awswrangler as wr
import pandas as pd
import logging

DESTINATION = "s3://payment-settlement/processed/settlements/"

s3 = boto3.client("s3")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

RENAMES =   {
    "Merchant Account": "merchant_account",
    "Psp Reference": "psp_reference",
    "Payment Method": "payment_method",
    "Creation Date": "creation_date_utc",
    "Creation Date (AMS)": "creation_date",
    "Gross Currency": "gross_currency",
    "Gross Debit (GC)": "gross_amount",
    "Exchange Rate": "exchange_rate",
    "Net Currency": "net_currency",
    "Net Credit (NC)": "net_amount",
    "Commission (NC)": "commission",
    "Markup (NC)": "markup",
    "Scheme Fees (NC)": "scheme_fees",
    "Interchange (NC)": "interchange",
    "DCC Markup (NC)": "dcc_markup",
    "Advanced (NC)": "advanced",
    "Booking Date": "booking_date_utc",
    "Booking Date (AMS)": "booking_date",
    "Type": "type",
    "Batch Number":"batch_number"
}

FINAL_COLUMNS =   [
    "merchant_account",
    "psp_reference",
    "payment_method",
    "creation_date_utc",
    "creation_date",
    "gross_currency",
    "gross_amount",
    "exchange_rate",
    "net_currency",
    "net_amount",
    "commission",
    "markup",
    "scheme_fees",
    "interchange",
    "dcc_markup",
    "advanced",
    "total_charges",
    "type",
    "batch_number",
    "booking_date_utc",
    "booking_date",
    "settled_date"
]

CHARGE_COLUMNS = [
    "commission",
    "markup",
    "scheme_fees",
    "interchange",
    "dcc_markup",
    "advanced",
]

def lambda_handler(event, context):
    
    body = json.loads(event["Records"][0]["body"])
    bucket = body["detail"]["bucket"]["name"]
    key = body["detail"]["object"]["key"]
    etag = body["detail"]["object"]["etag"]

    source = f"s3://{bucket}/{key}"

    try:
        s3.head_object(Bucket=bucket, Key=f"processed/_processed_etags/etag={etag}")
        extra= {"bucket":bucket,"key":key,"etag":etag}
        logger.warning(f"Duplicate file, skipped extra={extra}")
        return
        
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
       
            df = wr.s3.read_csv(source)

            df = df.rename(columns=RENAMES)

            df["creation_date_utc"] = pd.to_datetime(df["creation_date_utc"], utc=True)
            df["creation_date"] = pd.to_datetime(df["creation_date"])
            df["booking_date_utc"] = pd.to_datetime(df["booking_date_utc"], utc=True)
            df["booking_date"] = pd.to_datetime(df["booking_date"])
            df["settled_date"] = pd.to_datetime(df["booking_date"]).dt.date
            
            numeric_cols = [
                "gross_amount",
                "net_amount",
                "exchange_rate",
                *CHARGE_COLUMNS,
            ]

            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

            df["total_charges"] = df[CHARGE_COLUMNS].sum(axis=1)

            df = df[FINAL_COLUMNS]
            rows_read = len(df)

            df = df[df["psp_reference"].notna()]

            rows_written=len(df)
            rows_dropped=rows_read-rows_written
            partitions = df["settled_date"].unique().tolist()
            wr.s3.to_parquet(
                df=df,
                path=DESTINATION,
                dataset=True,
                mode="append",
                partition_cols=["settled_date"],
                compression="snappy",
            )

            s3.put_object(
                Bucket=bucket,
                Key=f"processed/_processed_etags/etag={etag}",
                Body="",
            )


            extra = {"bucket":bucket,"key":key,"etag":etag,
                        "rows_read": rows_read,
                        "rows_written": rows_written,
                        "rows_dropped": rows_dropped,
                        "partition_no": len(partitions),
                        "partitions": partitions}

            logger.info(f"File processed extra={extra}")
            
    
    return

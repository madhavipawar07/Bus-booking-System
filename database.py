import boto3

dynamodb = boto3.resource(
    "dynamodb",
    region_name="ap-south-1"
)

booking_table = dynamodb.Table("booking")
import boto3
from PIL import Image, UnidentifiedImageError
from io import BytesIO

MAX_SIZE = (600, 600)
s3client = boto3.client('s3')

def lambda_handler(event, context):
    record = event['Records'][0]['s3']
    src_bucket, key = record['bucket']['name'], record['object']['key']
    dest_bucket = 'resized-03aac4'

    obj = s3client.get_object(Bucket=src_bucket, Key=key)
    data = obj['Body'].read()

    # verify it’s a valid image
    try:
        img_buffer = BytesIO(data)
        img = Image.open(img_buffer)
        img.verify()
    except UnidentifiedImageError:
        print(f"Skipped {key} (not an image)")
        return {'statusCode': 200, 'body': f"Skipped {key} (not an image)"}

    # processing
    img_buffer.seek(0) # Reset buffer position
    img = Image.open(img_buffer)

    img.thumbnail(MAX_SIZE, Image.LANCZOS)

    # Save to a new buffer
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    s3client.put_object(Bucket=dest_bucket, Key=key, Body=buf, ContentType="image/jpeg")
    print(f"Resized {key} and uploaded to {dest_bucket}")
    return {'statusCode': 200, 'body': f"Resized {key} and uploaded to {dest_bucket}"}


    # Pillow layer for us-east-1
    # https://github.com/keithrozario/Klayers?tab=readme-ov-file
    # arn:aws:lambda:us-east-1:692859926587:layer:pillow-layer:1
    # arn:aws:lambda:eu-north-1:770693421928:layer:Klayers-p312-pillow:2
import boto3
from botocore.exceptions import ClientError

def test_s3_connection():
    try:
        # Crear cliente S3
        s3_client = boto3.client(
            's3',
            aws_access_key_id='<AWS_ACCESS_KEY_ID>',
            aws_secret_access_key='<AWS_SECRET_ACCESS_KEY>',
            region_name='us-east-1'
        )
        
        # Intentar listar los buckets
        response = s3_client.list_buckets()
        print("Buckets disponibles:")
        for bucket in response['Buckets']:
            print(f"- {bucket['Name']}")
            
        # Intentar listar objetos en el bucket perc-charly
        try:
            objects = s3_client.list_objects_v2(Bucket='perc-charly')
            print("\nObjetos en perc-charly:")
            if 'Contents' in objects:
                for obj in objects['Contents']:
                    print(f"- {obj['Key']}")
            else:
                print("El bucket está vacío")
        except ClientError as e:
            print(f"\nError al acceder al bucket perc-charly: {str(e)}")
            
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == "__main__":
    test_s3_connection() 
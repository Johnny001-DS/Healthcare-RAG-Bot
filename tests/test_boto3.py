import boto3

# Initialize Bedrock client
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

# Test invoking the Titan embedding model
try:
    response = bedrock_client.invoke_model(
        modelId="amazon.titan-embed-text-v1",  # Ensure this matches exactly
        body="Hello from Bedrock",            # Text input
        contentType="text/plain"              # Content type
    )

    # Read and print the response (should contain embeddings)
    print(response['body'].read())

except Exception as e:
    print(f"Error invoking the model: {e}")


# Test invoking the Titan embedding model
try:
    response = bedrock_client.invoke_model(
        modelId="amazon.titan-embed-text-v1",  # Ensure this matches exactly
        body="Hello from Bedrock",            # Text input
        contentType="text/plain"              # Content type
    )

    # Read and print the response (should contain embeddings)
    print(response['body'].read())

except Exception as e:
    print(f"Error invoking the model: {e}")
# 
#test 

#test 2
#test 3
#test 4
#test 5
#test 6
#test 7
#test 8
#test 9
#test 10

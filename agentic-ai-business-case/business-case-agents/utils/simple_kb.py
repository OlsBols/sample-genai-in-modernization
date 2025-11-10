#!/usr/bin/env python3

import boto3
import json
from pathlib import Path

def query_partner_knowledge(question, bucket_name="business-case-kb-us-east-1"):
    """Simple S3-based knowledge retrieval without vector database"""
    
    s3 = boto3.client('s3', region_name='us-east-1')
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # Get all partner documents
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix='partner-data/')
    except Exception as e:
        return f"Error accessing S3: {e}"
    
    context_docs = []
    for obj in response.get('Contents', []):
        try:
            # Get document content
            doc = s3.get_object(Bucket=bucket_name, Key=obj['Key'])
            content = doc['Body'].read().decode('utf-8', errors='ignore')
            
            # Skip binary files and get first 1500 chars
            if len(content) > 50 and not obj['Key'].endswith('.pdf'):
                context_docs.append({
                    'filename': obj['Key'].split('/')[-1],
                    'content': content[:1500]
                })
        except:
            continue
    
    if not context_docs:
        return "No partner documents found"
    
    # Create context from documents
    context = "\n\n".join([
        f"Document: {doc['filename']}\n{doc['content']}"
        for doc in context_docs[:3]  # Limit to 3 docs
    ])
    
    # Query Claude with context
    prompt = f"""Based on the following partner knowledge documents, answer this question: {question}

Partner Knowledge:
{context}

Please provide a relevant answer based on the documents above."""

    try:
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1000,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        return result['content'][0]['text']
        
    except Exception as e:
        return f"Error querying Claude: {e}"

def get_partner_context(topic):
    """Get partner context for a specific topic"""
    return query_partner_knowledge(f"What information do you have about {topic}?")

if __name__ == "__main__":
    # Test the function
    result = query_partner_knowledge("What are AWS migration best practices?")
    print(result)

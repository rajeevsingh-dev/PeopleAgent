
# Using DeviceFlow
#https://github.com/microsoftgraph/msgraph-sdk-python/tree/main
#pip install msgraph-sdk


import asyncio
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
import os
from dotenv import load_dotenv

load_dotenv()
        
# Graph API setup
client_id = os.getenv('client_id')
tenant = os.getenv('tenant')


credential = DeviceCodeCredential(client_id=client_id, tenant_id=tenant)
scopes = ["User.Read"]
client = GraphServiceClient(credentials=credential, scopes=scopes)

async def me():
    me = await client.me.get()
    if me:
        print(me.display_name)

asyncio.run(me())
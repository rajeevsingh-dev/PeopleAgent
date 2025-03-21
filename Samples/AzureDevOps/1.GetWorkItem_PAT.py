import requests
import base64

# Replace these values with your actual information
ORGANIZATION = "YOUR_ORG_NAME"
TARGET_EMAIL = "YOUR_EMAIL_ID"
PAT = "YOUR_PERSONAL_ACCESS_TOKEN"  # Insert your PAT here


# Create the Basic authentication header
# Note: The username can be empty. Azure DevOps requires the format ":<PAT>"
auth_str = f":{PAT}"
b64_auth_str = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
headers = {
    "Authorization": f"Basic {b64_auth_str}",
    "Content-Type": "application/json"
}

# WIQL endpoint URL for querying work items
WIQL_URL = f"https://dev.azure.com/{ORGANIZATION}/_apis/wit/wiql?api-version=6.0"

def get_work_items_by_assigned_email(email):
    """
    Retrieves work items assigned to a user (searched by email) using WIQL.
    """
    wiql_payload = {
        "query": f"SELECT [System.Id], [System.Title] FROM WorkItems WHERE [System.AssignedTo] CONTAINS '{email}'"
    }
    
    # Execute the WIQL query
    response = requests.post(WIQL_URL, json=wiql_payload, headers=headers)
    response.raise_for_status()
    query_result = response.json()
    work_items = query_result.get("workItems", [])
    
    if not work_items:
        print(f"No work items found for {email}")
        return []
    
    # Extract work item IDs
    ids = [str(item["id"]) for item in work_items]
    
    # Batch get details of the work items
    batch_url = f"https://dev.azure.com/{ORGANIZATION}/_apis/wit/workitemsbatch?api-version=6.0"
    batch_payload = {
        "ids": ids,
        "fields": ["System.Id", "System.Title", "System.AssignedTo", "System.State"]
    }
    batch_response = requests.post(batch_url, json=batch_payload, headers=headers)
    batch_response.raise_for_status()
    batch_result = batch_response.json()
    
    return batch_result.get("value", [])

def format_work_items(work_items):
    """
    Formats the list of work items into a table-style string.
    """
    # Header for the table.
    header = f"{'ID':<10} | {'Title':<40} | {'Assigned To':<30} | {'State':<15}\n"
    header += "-" * 100 + "\n"

    lines = [header]
    for item in work_items:
        fields = item.get("fields", {})
        id_val = fields.get("System.Id", "N/A")
        title = fields.get("System.Title", "N/A")
        assigned = fields.get("System.AssignedTo", "N/A")
        # If assigned is a dict, try extracting displayName, otherwise convert to string.
        if isinstance(assigned, dict):
            assigned = assigned.get("displayName", str(assigned))
        else:
            assigned = str(assigned)
        state = fields.get("System.State", "N/A")
        line = f"{id_val:<10} | {title:<40} | {assigned:<30} | {state:<15}\n"
        lines.append(line)
    return "".join(lines)



if __name__ == "__main__":
    work_items = get_work_items_by_assigned_email(TARGET_EMAIL)
    if work_items:
        formatted = format_work_items(work_items)
        print(f"Work items assigned to {TARGET_EMAIL}:\n")
        print(formatted)
    else:
        print("No work items found.")
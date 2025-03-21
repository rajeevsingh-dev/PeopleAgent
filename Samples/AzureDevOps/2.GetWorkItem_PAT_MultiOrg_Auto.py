import requests
import base64

# Replace these values with your actual information
TARGET_EMAIL = "YOUR_EMAIL_ID"
PAT = "YOUR_PERSONAL_ACCESS_TOKEN"  # Insert your PAT here

# Create the Basic authentication header
# Note: Username is empty; Azure DevOps expects the format ":<PAT>"
auth_str = f":{PAT}"
b64_auth_str = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
headers = {
    "Authorization": f"Basic {b64_auth_str}",
    "Content-Type": "application/json"
}

def get_my_accounts():
    """
    Retrieves the list of Azure DevOps organizations (accounts) associated with the current user.
    """
    # Get the current user's profile to retrieve the member id.
    profile_url = "https://app.vssps.visualstudio.com/_apis/profile/profiles/me?api-version=6.0"
    profile_response = requests.get(profile_url, headers=headers)
    profile_response.raise_for_status()
    profile_data = profile_response.json()
    member_id = profile_data.get("id")
    if not member_id:
        raise Exception("Unable to retrieve member id from profile.")
        
    # Get associated organizations using the member id.
    accounts_url = f"https://app.vssps.visualstudio.com/_apis/accounts?memberId={member_id}&api-version=6.0"
    accounts_response = requests.get(accounts_url, headers=headers)
    accounts_response.raise_for_status()
    accounts_data = accounts_response.json()
    return accounts_data.get("value", [])

def get_work_items_by_assigned_email_in_org(email, organization):
    """
    Retrieves work items assigned to a user in a single organization using WIQL.
    Also attaches the organization name to each returned work item.
    """
    # WIQL endpoint for the given organization.
    wiql_url = f"https://dev.azure.com/{organization}/_apis/wit/wiql?api-version=6.0"
    wiql_payload = {
        "query": f"SELECT [System.Id], [System.Title] FROM WorkItems WHERE [System.AssignedTo] CONTAINS '{email}'"
    }
    
    # Execute WIQL query
    response = requests.post(wiql_url, json=wiql_payload, headers=headers)
    response.raise_for_status()
    query_result = response.json()
    work_items = query_result.get("workItems", [])
    
    if not work_items:
        print(f"No work items found for {email} in organization {organization}")
        return []
    
    # Extract work item IDs.
    ids = [str(item["id"]) for item in work_items]
    
    # Batch endpoint to get details, including project name with "System.TeamProject"
    batch_url = f"https://dev.azure.com/{organization}/_apis/wit/workitemsbatch?api-version=6.0"
    batch_payload = {
        "ids": ids,
        "fields": ["System.Id", "System.Title", "System.AssignedTo", "System.State", "System.TeamProject"]
    }
    batch_response = requests.post(batch_url, json=batch_payload, headers=headers)
    batch_response.raise_for_status()
    batch_result = batch_response.json()
    
    items = batch_result.get("value", [])
    # Attach the organization to each work item for later reference.
    for item in items:
        item["fields"]["Organization"] = organization
    return items

def get_work_items_from_all_orgs(email):
    """
    Automatically retrieves work items assigned to the given email across
    all organizations associated with the current PAT.
    """
    combined_items = []
    accounts = get_my_accounts()
    if not accounts:
        print("No organizations were found for the current user.")
        return combined_items

    for account in accounts:
        # 'accountName' typically corresponds to the organization name.
        org = account.get("accountName")
        if org:
            print(f"Querying organization: {org}")
            try:
                items = get_work_items_by_assigned_email_in_org(email, org)
                if items:
                    print(f"Found {len(items)} work item(s) in {org}.")
                    combined_items.extend(items)
            except Exception as e:
                print(f"Error querying organization {org}: {str(e)}")
    return combined_items

def format_work_items(work_items):
    """
    Formats the list of work items into a table-style string including Organization and Project.
    """
    header = (f"{'ID':<10} | {'Title':<40} | {'Organization':<20} | {'Project':<20} | "
              f"{'Assigned To':<30} | {'State':<15}\n")
    header += "-" * 140 + "\n"
    lines = [header]
    
    for item in work_items:
        fields = item.get("fields", {})
        id_val = fields.get("System.Id", "N/A")
        title = fields.get("System.Title", "N/A")
        organization = fields.get("Organization", "N/A")
        project = fields.get("System.TeamProject", "N/A")
        assigned = fields.get("System.AssignedTo", "N/A")
        # If assigned is a dict, try extracting displayName.
        if isinstance(assigned, dict):
            assigned = assigned.get("displayName", str(assigned))
        else:
            assigned = str(assigned)
        state = fields.get("System.State", "N/A")
        line = f"{id_val:<10} | {title:<40} | {organization:<20} | {project:<20} | {assigned:<30} | {state:<15}\n"
        lines.append(line)
    return "".join(lines)

if __name__ == "__main__":
    all_work_items = get_work_items_from_all_orgs(TARGET_EMAIL)
    if all_work_items:
        formatted_output = format_work_items(all_work_items)
        print(f"Work items assigned to {TARGET_EMAIL} across all organizations:\n")
        print(formatted_output)
    else:
        print("No work items found across any organizations.")
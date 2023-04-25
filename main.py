import boto3
import pandas as pd

org_client = boto3.client("organizations")


def get_root_info():
    response = org_client.list_roots()
    root_info = response["Roots"][0]
    return root_info


def get_root_id(root_info) -> str:
    root_id = root_info["Id"]
    return root_id


def get_account_info(account_id: str) -> dict:
    response = org_client.describe_account(AccountId=account_id)
    account_info = response.get("Account", {})
    return account_info


def get_account_name(account_id: str) -> str:
    account_info = get_account_info(account_id)
    account_name = account_info.get("Name", "")
    return account_name


def yield_child_accounts(parent_id: str):
    paginator = org_client.get_paginator("list_children")
    operation_parameters = {"ParentId": parent_id, "ChildType": "ACCOUNT"}
    page_iterator = paginator.paginate(**operation_parameters)
    for page in page_iterator:
        children = page["Children"]
        for child in children:
            child["ParentId"] = parent_id
            child["Name"] = get_account_name(child["Id"])
            print(child)
            yield child


def get_ou_info(ou_id: str) -> dict:
    response = org_client.describe_organizational_unit(OrganizationalUnitId=ou_id)
    ou_info = response.get("OrganizationalUnit", {})
    return ou_info


def get_ou_name(ou_id: str) -> str:
    ou_info = get_ou_info(ou_id)
    ou_name = ou_info.get("Name", "")
    return ou_name


def yield_child_ous(parent_id: str):
    paginator = org_client.get_paginator("list_children")
    operation_parameters = {"ParentId": parent_id, "ChildType": "ORGANIZATIONAL_UNIT"}
    page_iterator = paginator.paginate(**operation_parameters)
    for page in page_iterator:
        children = page["Children"]
        for child in children:
            child["ParentId"] = parent_id
            child["Name"] = get_ou_name(child["Id"])
            print(child)
            yield child
            yield from list_all_children(child["Id"])


def list_all_children(parent_id):
    yield from yield_child_accounts(parent_id)
    yield from yield_child_ous(parent_id)


def children_to_dataframe(children):
    data = []
    for child in children:
        data.append(
            {
                "id": child["Id"],
                "name": child["Name"],
                "type": child["Type"],
                "parent_id": child["ParentId"],
            }
        )
    return pd.DataFrame(data)


def main() -> pd.DataFrame:
    root_info = get_root_info()
    root_id = root_info["Id"]
    root_name = root_info["Name"]
    children = list(list_all_children(root_id))
    children.insert(
        0, {"Id": root_id, "Name": root_name, "Type": "ROOT", "ParentId": ""}
    )

    # Generate pandas dataframe from children list in long-format
    df = children_to_dataframe(children)
    return df


if __name__ == "__main__":
    df = main()
    print(df)


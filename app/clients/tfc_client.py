"""
TFC Client Module
This module provides a TFCClient class for interacting with the Terraform Cloud API.
It includes methods to fetch workspaces, check the last apply status, enable auto-apply,
create destroy runs, and process organizations.
"""

import requests
import time
import logging
import traceback

from app.utils.secrets import VaultSecretsLoader


class TfcClient:
    def __init__(self, api_url="https://app.terraform.io/api/v2"):
        """
        Initializes the TfcClient instance.

        Args:
            token (str): The Terraform Cloud API token.
            api_url (str): The base URL for the Terraform Cloud API.
        """
        self.api_url = api_url
        token = VaultSecretsLoader().load_secret("tfc-creds")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json",
        }
        self.org_list = ["DSB", "DJB-Personal"]
        self.exclude_workspaces = {
            "DSB": ["discord-bot", "discord-bot-repositories"],
            "DJB-Personal": ["openvpn-server"],
        }

    def get_workspaces(self, org_name):
        """
        Fetches all workspaces for a given organization.

        Args:
            org_name (str): The name of the organization.

        Returns:
            list: A list of workspaces.
        """
        url = f"{self.api_url}/organizations/{org_name}/workspaces"
        workspaces = []

        logging.info(f"Fetching workspaces for organization: {org_name}")
        while url:
            try:
                res = requests.get(url, headers=self.headers)
                res.raise_for_status()
                data = res.json()
                workspaces.extend(data["data"])
                url = data.get("links", {}).get("next")
            except requests.RequestException as e:
                logging.error(f"Failed to fetch workspaces for '{org_name}': {e}")
                logging.debug(traceback.format_exc())
                break

        logging.info(
            f"Retrieved {len(workspaces)} workspaces for organization: {org_name}"
        )
        return workspaces

    def was_last_apply_destroy(self, workspace_id):
        """
        Checks if the most recent apply for a workspace was a destroy operation.

        Args:
            workspace_id (str): The ID of the workspace to check.

        Returns:
            bool: True if the most recent apply was a destroy, False otherwise.
        """
        url = f"{self.api_url}/workspaces/{workspace_id}/runs"
        logging.info(
            f"Checking if the most recent apply for workspace ID '{workspace_id}' was a destroy."
        )

        try:
            res = requests.get(url, headers=self.headers)
            res.raise_for_status()
            runs = res.json()["data"]

            # Find the most recent completed run
            for run in runs:
                if run["attributes"]["status"] == "applied":
                    is_destroy = run["attributes"]["is-destroy"]
                    logging.info(
                        f"Most recent apply for workspace ID '{workspace_id}' was a "
                        f"{'destroy' if is_destroy else 'normal'} operation."
                    )
                    return is_destroy

            logging.warning(
                f"No completed apply runs found for workspace ID '{workspace_id}'."
            )
            return False

        except requests.RequestException as e:
            logging.error(
                f"Failed to check the most recent apply for workspace ID '{workspace_id}': {e}"
            )
            logging.debug(traceback.format_exc())
            return False

    def enable_auto_apply(self, workspace_id):
        """
        Enables the Auto Apply setting for a workspace.

        Args:
            workspace_id (str): The ID of the workspace to update.

        Returns:
            bool: True if Auto Apply was successfully enabled, False otherwise.
        """
        url = f"{self.api_url}/workspaces/{workspace_id}"
        payload = {"data": {"attributes": {"auto-apply": True}, "type": "workspaces"}}

        logging.info(f"Enabling Auto Apply for workspace ID: {workspace_id}")
        try:
            res = requests.patch(url, headers=self.headers, json=payload)
            if res.status_code == 200:
                logging.info(
                    f"Auto Apply successfully enabled for workspace ID: {workspace_id}"
                )
                return True
            else:
                logging.error(
                    f"Failed to enable Auto Apply for workspace ID '{workspace_id}': {res.text}"
                )
                return False
        except requests.RequestException as e:
            logging.error(
                f"Error enabling Auto Apply for workspace ID '{workspace_id}': {e}"
            )
            logging.debug(traceback.format_exc())
            return False

    def create_destroy_run(self, workspace_id, workspace_name):
        """
        Creates a destroy run for a workspace.

        Args:
            workspace_id (str): The ID of the workspace.
            workspace_name (str): The name of the workspace.
        """
        payload = {
            "data": {
                "attributes": {
                    "is-destroy": True,
                    "message": "Automated destroy with auto-apply",
                },
                "type": "runs",
                "relationships": {
                    "workspace": {"data": {"type": "workspaces", "id": workspace_id}}
                },
            }
        }

        url = f"{self.api_url}/runs"
        logging.info(
            f"Creating destroy run for workspace: {workspace_name} (ID: {workspace_id})"
        )
        try:
            res = requests.post(url, headers=self.headers, json=payload)
            if res.status_code == 201:
                run_id = res.json()["data"]["id"]
                logging.info(
                    f"[✓] Destroy run created for workspace '{workspace_name}' (run_id: {run_id})"
                )
            else:
                logging.error(
                    f"[x] Failed to create destroy run for '{workspace_name}': {res.text}"
                )
        except requests.RequestException as e:
            logging.error(
                f"Failed to create destroy run for workspace '{workspace_name}': {e}"
            )
            logging.debug(traceback.format_exc())

    def process_organization(self, org_name):
        """
        Processes all workspaces in an organization.

        Args:
            org_name (str): The name of the organization.
        """
        logging.info(f"🔍 Starting processing for organization: {org_name}")
        workspaces = self.get_workspaces(org_name)

        if not workspaces:
            logging.warning(f"No workspaces found for organization: {org_name}")
            return

        for ws in workspaces:
            ws_id = ws["id"]
            ws_name = ws["attributes"]["name"]

            if ws_name in self.exclude_workspaces.get(org_name, []):
                logging.info(
                    f"  ⏩ Skipping workspace '{ws_name}' (whitelisted in {org_name})"
                )
                continue

            logging.info(f"  ▶️ Processing workspace: {ws_name} (ID: {ws_id})")

            try:
                # Check if the last apply was a destroy
                if self.was_last_apply_destroy(ws_id):
                    logging.info(
                        f"    [!] Last apply for workspace '{ws_name}' was a destroy. Skipping..."
                    )
                    continue

                logging.info("    Creating destroy run...")
                self.enable_auto_apply(ws_id)
                self.create_destroy_run(ws_id, ws_name)
            except Exception as e:
                logging.error(f"    [!] Error processing workspace '{ws_name}': {e}")
                logging.debug(traceback.format_exc())

            time.sleep(1)  # Avoid API rate limits

        logging.info(f"✅ Finished processing for organization: {org_name}")

    def run(self):
        """
        Runs the TfcClient to process all organizations.
        """
        try:
            for org in self.org_list:
                self.process_organization(org)
        except Exception as e:
            logging.critical(f"Unhandled exception in main: {e}")
            logging.debug(traceback.format_exc())
            raise

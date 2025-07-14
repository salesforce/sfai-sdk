import requests
import time
from requests.auth import HTTPBasicAuth
from typing import Any
from sfai.core.response_models import BaseResponse


class MulesoftAPI:
    """
    Mulesoft API Class for deploying APIs

    Args:
        org_id: Mulesoft Org ID
        environment_id: API environment ID
        client_id: Connected app `id`
        client_secret: Connected app `secret`
    """

    base_url = "https://anypoint.mulesoft.com"

    def __init__(
        self,
        org_id: str,
        environment_id: str,
        client_id: str,
        client_secret: str,
    ):
        self._org_id = org_id
        self._environment_id = environment_id
        self._client_id = client_id
        self._client_secret = client_secret

        auth_result = self._authorize()
        if isinstance(auth_result, BaseResponse):
            self.auth_error = auth_result
            self._session = None
        else:
            self._session = auth_result
            self.auth_error = None

    def _check_auth(self) -> BaseResponse | None:
        if self.auth_error:
            return self.auth_error
        return None

    def _authorize(self) -> BaseResponse:
        """Get oauth token for subsequent API calls."""
        response = requests.post(
            f"{self.base_url}/accounts/api/v2/oauth2/token",
            auth=HTTPBasicAuth(
                username="~~~Client~~~",
                password=f"{self._client_id}~?~{self._client_secret}",
            ),
            headers={"Content-Type": "application/json"},
            json={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "grant_type": "client_credentials",
            },
        )
        if response.status_code != 200:
            try:
                error_msg = response.json().get("message", "Authorization failed")
            except ValueError:
                error_msg = response.text.strip() or "Authorization failed"
            return BaseResponse(
                success=False,
                message=f"Authorization failed: {error_msg}",
            )
        token = response.json()["access_token"]
        session = requests.Session()
        session.headers = {
            "authorization": f"Bearer {token}",
        }
        return session

    def _make_api_call(
        self,
        path: str,
        method: str,
        headers: dict | None = None,
        body: dict | None = None,
        files: dict | None = None,
    ) -> Any:
        """
        Wrapper around MuleSoft API calls.

        Args:
            path: URL Path to call
            method: HTTP Method
            headers: Additional headers
            body: Request body
            files: Request files (for multipart forms)

        Returns:
            JSON response from API
        """
        url = f"{self.base_url}/{path}"
        print(f"Calling: {url=}")
        response = self._session.request(
            method, url, headers=headers, json=body, files=files
        )
        try:
            response.raise_for_status()
        except requests.HTTPError:
            print(response.json())
            raise
        return response.json()

    def search_exchange_assets(
        self, name_filter: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Search Exchange for assets.

        Args:
            name_filter: search for asset based on name.

        Returns:
            List of assets
        """
        query_params = {"search": name_filter}
        query_string = "&".join(
            [f"{key}={value}" for key, value in query_params.items() if value]
        )
        query_string = "?" + query_string if query_string else ""
        return self._make_api_call(
            f"exchange/api/v2/assets/search{query_string}", "get"
        )

    def get_exchange_asset(self, asset_id: str) -> dict[str, Any]:
        """
        Get specified Exchange asset.

        Args:
            asset_id: ID of the asset you want to fetch.

        Returns:
            Asset definition
        """
        return self._make_api_call(
            f"exchange/api/v2/assets/{self._org_id}/{asset_id}/asset", "get"
        )

    def publish_exchange_asset(
        self,
        name: str,
        version: str,
        oas_file: str,
        tags: list[str] | None = None,
        description: str = "",
    ) -> dict[str, Any]:
        """
        Publish an asset to Exchange.

        Args:
            name: Asset Name
            version: Asset version
            oas_file: Open API Specification file (yaml format)
            tags: List of API tags
            description: API Description

        Returns:
            Created Asset
        """
        tags = tags or []
        response = self._make_api_call(
            f"exchange/api/v2/organizations/{self._org_id}/assets/{self._org_id}/{name}/{version}",
            "post",
            files={
                "files.oas.yaml": (oas_file.split("/")[-1], open(oas_file, "rb")),
                "name": (None, name),
                "description": (None, description),
                "type": (None, "oas"),
                "properties.apiVersion": (None, f"v{version.split('.')[0]}"),
                "properties.mainFile": (None, oas_file.split("/")[-1]),
                "tags": (None, ",".join(tags)),
            },
        )
        status_link = response["publicationStatusLink"]
        while True:
            publication_status = self._make_api_call(
                status_link.removeprefix(f"{self.base_url}/"), "get"
            )
            if publication_status["status"] != "running":
                break
            time.sleep(1)
        return publication_status

    def list_published_apis(self) -> list[dict[str, Any]]:
        """List published APIs."""
        return self._make_api_call(
            f"apimanager/api/v1/organizations/{self._org_id}/environments/{self._environment_id}/apis",
            "get",
        )

    def _find_existing_api(
        self, name: str, endpoint_path: str
    ) -> dict[str, Any] | None:
        """
        Find an existing API based on name and endpoint path.

        Args:
            name: Name of the API
            endpoint_path: Path of the API endpoint

        Returns:
            Existing API details if found, None otherwise
        """
        published_apis = self.list_published_apis()

        # Look through assets for matching name
        for asset in published_apis.get("assets", []):
            if asset.get("exchangeAssetName") == name:
                # Look through APIs for matching endpoint path
                for api_instance in asset.get("apis", []):
                    # We need to check the endpoint.proxyUri path
                    api_details = self._make_api_call(
                        f"apimanager/api/v1/organizations/{self._org_id}/environments/{self._environment_id}/apis/{api_instance['id']}",
                        "get",
                    )
                    if (
                        api_details.get("endpoint", {})
                        .get("proxyUri", "")
                        .endswith(f"/{endpoint_path}")
                    ):
                        return api_details

        return None

    def publish_api(
        self,
        name: str,
        version: str,
        implementation_uri: str,
        endpoint_uri: str,
        endpoint_path: str,
    ) -> dict[str, Any]:
        """
        Publish an API.

        Agentforce --> endpoint_uri/endpoint_path --> implementation_uri

        Args:
            environment: Mulesoft Environment ID
            name: Name of the API
            version: Version of the API
            implementation_uri: URI of the actual API
            endpoint_uri: URI of the Mulesoft endpoint (URI of the FlexGateway)
            endpoint_path: Added to the endpoint_uri to separate resources on
                the same FlexGateway

        Returns:
            Published API details
        """
        existing_api = self._find_existing_api(name, endpoint_path)
        if existing_api:
            # If exists, update the existing API with the new version
            print(f"Updating existing API with ID: {existing_api['id']}")
            return self._make_api_call(
                f"apimanager/api/v1/organizations/{self._org_id}/environments/{self._environment_id}/apis/{existing_api['id']}",
                "patch",
                body={
                    "technology": "flexGateway",
                    "endpointUri": endpoint_uri,
                    "providerId": None,
                    "spec": {
                        "groupId": self._org_id,
                        "assetId": name,
                        "version": version,
                    },
                    "endpoint": {
                        "deploymentType": "HY",
                        "isCloudHub": None,
                        "uri": implementation_uri,
                        "proxyUri": f"http://localhost:8081/{endpoint_path}",
                    },
                },
            )
        else:
            # If doesn't exist, create a new API
            return self._make_api_call(
                f"apimanager/api/v1/organizations/{self._org_id}/environments/{self._environment_id}/apis",
                "post",
                body={
                    "technology": "flexGateway",
                    "endpointUri": endpoint_uri,
                    "providerId": None,
                    "spec": {
                        "groupId": self._org_id,
                        "assetId": name,
                        "version": version,
                    },
                    "endpoint": {
                        "deploymentType": "HY",
                        "isCloudHub": None,
                        "uri": implementation_uri,
                        "proxyUri": f"http://localhost:8081/{endpoint_path}",
                    },
                },
            )

    def deploy_api(
        self,
        api_id: str,
        gateway_id: str,
        gateway_version: str,
    ) -> dict[str, Any]:
        """
        Deploy an API

        Args:
            api_id: ID of the API you want to deploy
            gateway_id: Gateway ID
            gateway_version: Gateway Version

        Returns:
            Published API details
        """
        # First check if a deployment already exists
        try:
            existing_deployments = self._make_api_call(
                f"proxies/xapi/v1/organizations/{self._org_id}/environments/{self._environment_id}/apis/{api_id}/deployments",
                "get",
            )

            # If we have existing deployments, handle them
            if existing_deployments and len(existing_deployments) > 0:
                # Find deployment on this target
                for deployment in existing_deployments:
                    if deployment and deployment.get("targetId") == gateway_id:
                        deployment_id = deployment.get("id")
                        print(
                            f"Found existing deployment with ID: {deployment_id}, "
                            f"updating instead of creating new"
                        )

                        # Update the existing deployment
                        return self._make_api_call(
                            f"proxies/xapi/v1/organizations/{self._org_id}/environments/{self._environment_id}/apis/{api_id}/deployments/{deployment_id}",
                            "patch",
                            body={"gatewayVersion": gateway_version},
                        )
        except requests.HTTPError as e:
            # If we get a 404, it means no deployments exist yet
            if e.response.status_code != 404:
                raise

        # If there's no deployment for this specific target, create a new one
        return self._make_api_call(
            f"proxies/xapi/v1/organizations/{self._org_id}/environments/{self._environment_id}/apis/{api_id}/deployments",
            "post",
            body={
                "type": "HY",
                "gatewayVersion": gateway_version,
                "targetId": gateway_id,
                "environmentId": self._environment_id,
            },
        )

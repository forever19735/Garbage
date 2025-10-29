# Railway 自動更新功能實作

import os
import json
import requests
from typing import Dict, Any, Optional

class RailwayAPIManager:
    """Railway API 管理器"""
    
    def __init__(self):
        self.api_token = os.getenv('RAILWAY_API_TOKEN')
        self.project_id = os.getenv('RAILWAY_PROJECT_ID')
        self.service_id = os.getenv('RAILWAY_SERVICE_ID')
        self.api_url = "https://backboard.railway.app/graphql"
        
    def is_configured(self) -> bool:
        """檢查是否已正確配置 Railway API"""
        return bool(self.api_token)
    
    def get_headers(self) -> Dict[str, str]:
        """取得 API 請求標頭"""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def discover_project_and_service(self) -> tuple[Optional[str], Optional[str]]:
        """自動發現專案和服務 ID"""
        if not self.api_token:
            return None, None
            
        try:
            # 1. 取得所有專案
            projects_query = """
            query {
                projects {
                    id
                    name
                    services {
                        id
                        name
                    }
                }
            }
            """
            
            response = requests.post(
                self.api_url,
                headers=self.get_headers(),
                json={"query": projects_query}
            )
            
            if response.status_code != 200:
                print(f"❌ Railway API 請求失敗: {response.status_code}")
                return None, None
                
            data = response.json()
            if "errors" in data:
                print(f"❌ Railway API 錯誤: {data['errors']}")
                return None, None
                
            projects = data.get("data", {}).get("projects", [])
            if not projects:
                print("❌ 沒有找到任何專案")
                return None, None
                
            # 使用第一個專案和第一個服務
            project = projects[0]
            project_id = project["id"]
            
            services = project.get("services", [])
            if not services:
                print(f"❌ 專案 {project['name']} 沒有服務")
                return project_id, None
                
            service_id = services[0]["id"]
            print(f"✅ 自動發現專案: {project['name']} ({project_id})")
            print(f"✅ 自動發現服務: {services[0]['name']} ({service_id})")
            
            return project_id, service_id
            
        except Exception as e:
            print(f"❌ 自動發現失敗: {e}")
            return None, None
    
    def update_environment_variable(self, key: str, value: str) -> bool:
        """更新環境變數"""
        if not self.api_token:
            print("❌ Railway API Token 未設定")
            return False
            
        # 使用提供的 ID 或自動發現
        project_id = self.project_id
        service_id = self.service_id
        
        if not project_id or not service_id:
            print("🔍 自動發現專案和服務...")
            project_id, service_id = self.discover_project_and_service()
            
        if not project_id or not service_id:
            print("❌ 無法取得專案或服務 ID")
            return False
            
        try:
            # GraphQL mutation 來更新環境變數
            mutation = """
            mutation($input: UpsertVariableInput!) {
                upsertVariable(input: $input) {
                    id
                    name
                    value
                }
            }
            """
            
            variables = {
                "input": {
                    "projectId": project_id,
                    "serviceId": service_id,
                    "name": key,
                    "value": value
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.get_headers(),
                json={"query": mutation, "variables": variables}
            )
            
            if response.status_code != 200:
                print(f"❌ Railway API 請求失敗: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
            data = response.json()
            if "errors" in data:
                print(f"❌ Railway API 錯誤: {data['errors']}")
                return False
                
            result = data.get("data", {}).get("upsertVariable")
            if result:
                print(f"✅ Railway 環境變數已更新: {key}")
                return True
            else:
                print(f"❌ Railway 環境變數更新失敗")
                return False
                
        except Exception as e:
            print(f"❌ Railway API 請求異常: {e}")
            return False
    
    def get_environment_variables(self) -> Optional[Dict[str, str]]:
        """取得所有環境變數"""
        if not self.api_token:
            return None
            
        project_id = self.project_id
        service_id = self.service_id
        
        if not project_id or not service_id:
            project_id, service_id = self.discover_project_and_service()
            
        if not project_id or not service_id:
            return None
            
        try:
            query = """
            query($projectId: String!, $serviceId: String!) {
                variables(projectId: $projectId, serviceId: $serviceId) {
                    id
                    name
                    value
                }
            }
            """
            
            variables = {
                "projectId": project_id,
                "serviceId": service_id
            }
            
            response = requests.post(
                self.api_url,
                headers=self.get_headers(),
                json={"query": query, "variables": variables}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "variables" in data["data"]:
                    env_vars = {}
                    for var in data["data"]["variables"]:
                        env_vars[var["name"]] = var["value"]
                    return env_vars
                    
        except Exception as e:
            print(f"❌ 取得環境變數失敗: {e}")
            
        return None

# 全域 Railway API 管理器
railway_api = RailwayAPIManager()

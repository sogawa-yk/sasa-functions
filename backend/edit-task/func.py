import io
import json
import logging
import os
import urllib.parse

import oci
from fdk import response

def handler(ctx, data: io.BytesIO = None):
    """
    タスク編集Function
    POST /edit?id=<task_id>
    リクエストボディ: 更新したいフィールド（title, description, completed等）
    """
    logger = logging.getLogger()
    
    try:
        # クエリパラメータからtask_idを取得
        request_url = ctx.RequestURL()
        parsed_url = urllib.parse.urlparse(request_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        task_id = query_params.get('id', [None])[0]
        
        # バリデーション
        if not task_id or task_id.strip() == "":
            return response.Response(
                ctx,
                response_data=json.dumps({"error": "Task ID is required in query parameter 'id'"}),
                headers={"Content-Type": "application/json"},
                status_code=400
            )
        
        task_id = task_id.strip()
        
        # リクエストボディの解析
        if data is None:
            return response.Response(
                ctx,
                response_data=json.dumps({"error": "Request body is required"}),
                headers={"Content-Type": "application/json"},
                status_code=400
            )
        
        update_data = json.loads(data.getvalue())
        if not isinstance(update_data, dict):
            return response.Response(
                ctx,
                response_data=json.dumps({"error": "Request body must be a JSON object"}),
                headers={"Content-Type": "application/json"},
                status_code=400
            )
        
        # Resource Principal認証でOCIクライアント初期化
        signer = oci.auth.signers.get_resource_principals_signer()
        nosql_client = oci.nosql.NosqlClient(config={}, signer=signer)
        
        # 環境変数からテーブル名を取得
        table_name = os.environ.get("NOSQL_TABLE_NAME")
        if not table_name:
            logger.error("NOSQL_TABLE_NAME environment variable is not set")
            return response.Response(
                ctx,
                response_data=json.dumps({"error": "Server configuration error"}),
                headers={"Content-Type": "application/json"},
                status_code=500
            )
        
        # コンパートメントIDを取得
        compartment_id = signer.compartment_id
        
        # 既存タスクを取得
        get_response = nosql_client.get_row(
            table_name_or_id=table_name,
            key=[f"id:{task_id}"],
            compartment_id=compartment_id
        )
        
        if not get_response.data.value:
            return response.Response(
                ctx,
                response_data=json.dumps({"error": f"Task with ID '{task_id}' not found"}),
                headers={"Content-Type": "application/json"},
                status_code=404
            )
        
        # 既存データを取得してcontentフィールドからJSONを取得
        existing_row = get_response.data.value
        existing_content = json.loads(existing_row.get("content", "{}"))
        
        # 更新可能なフィールドの検証と更新
        allowed_fields = {"title", "description", "completed"}
        updated_content = existing_content.copy()
        
        for field, value in update_data.items():
            if field not in allowed_fields:
                return response.Response(
                    ctx,
                    response_data=json.dumps({"error": f"Field '{field}' is not allowed to be updated"}),
                    headers={"Content-Type": "application/json"},
                    status_code=400
                )
            
            # フィールド別のバリデーション
            if field == "title":
                if not isinstance(value, str) or value.strip() == "":
                    return response.Response(
                        ctx,
                        response_data=json.dumps({"error": "Title must be a non-empty string"}),
                        headers={"Content-Type": "application/json"},
                        status_code=400
                    )
                updated_content[field] = value.strip()
            elif field == "description":
                if not isinstance(value, str):
                    return response.Response(
                        ctx,
                        response_data=json.dumps({"error": "Description must be a string"}),
                        headers={"Content-Type": "application/json"},
                        status_code=400
                    )
                updated_content[field] = value.strip()
            elif field == "completed":
                if not isinstance(value, bool):
                    return response.Response(
                        ctx,
                        response_data=json.dumps({"error": "Completed must be a boolean"}),
                        headers={"Content-Type": "application/json"},
                        status_code=400
                    )
                updated_content[field] = value
        
        # 更新されたタスクを保存
        update_row_details = oci.nosql.models.UpdateRowDetails(
            value={
                "id": task_id,
                "content": json.dumps(updated_content)
            },
            compartment_id=compartment_id
        )
        
        nosql_client.update_row(
            table_name_or_id=table_name,
            update_row_details=update_row_details
        )
        
        logger.info(f"Task updated successfully with ID: {task_id}")
        
        # レスポンス用データを作成
        response_data = {
            "id": task_id,
            **updated_content
        }
        
        return response.Response(
            ctx,
            response_data=json.dumps(response_data),
            headers={"Content-Type": "application/json"},
            status_code=200
        )
        
    except json.JSONDecodeError as ex:
        logger.error(f"Invalid JSON in request body: {str(ex)}")
        return response.Response(
            ctx,
            response_data=json.dumps({"error": "Invalid JSON format in request body"}),
            headers={"Content-Type": "application/json"},
            status_code=400
        )
    
    except oci.exceptions.ServiceError as ex:
        logger.error(f"OCI NoSQL service error: {str(ex)}")
        return response.Response(
            ctx,
            response_data=json.dumps({"error": "Database operation failed"}),
            headers={"Content-Type": "application/json"},
            status_code=500
        )
    
    except Exception as ex:
        logger.error(f"Unexpected error: {str(ex)}")
        return response.Response(
            ctx,
            response_data=json.dumps({"error": "Internal server error"}),
            headers={"Content-Type": "application/json"},
            status_code=500
        )

import io
import json
import logging
import uuid
import datetime
import os

import oci
from fdk import response

def handler(ctx, data: io.BytesIO = None):
    """
    タスク追加Function
    POST /add
    リクエストボディ: {"title": "...", "description": "..."}
    """
    logger = logging.getLogger()
    
    try:
        # リクエストボディの解析
        if data is None:
            return response.Response(
                ctx, 
                response_data=json.dumps({"error": "Request body is required"}),
                headers={"Content-Type": "application/json"},
                status_code=400
            )
        
        body = json.loads(data.getvalue())
        title = body.get("title")
        description = body.get("description", "")
        
        # バリデーション
        if not title or not isinstance(title, str) or title.strip() == "":
            return response.Response(
                ctx,
                response_data=json.dumps({"error": "Title is required and must be a non-empty string"}),
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
        
        # タスクデータの作成
        task_id = str(uuid.uuid4())
        task_data = {
            "title": title.strip(),
            "description": description.strip(),
            "created_at": datetime.datetime.utcnow().isoformat() + "Z",
            "completed": False
        }
        
        # NoSQL Databaseにタスクを保存
        # 新しい行を挿入する場合はIF_ABSENTオプションを使用
        update_row_details = oci.nosql.models.UpdateRowDetails(
            value={
                "id": task_id,
                "content": json.dumps(task_data)
            },
            compartment_id=compartment_id,
            option=oci.nosql.models.UpdateRowDetails.OPTION_IF_ABSENT
        )
        
        nosql_client.update_row(
            table_name_or_id=table_name,
            update_row_details=update_row_details
        )
        
        logger.info(f"Task created successfully with ID: {task_id}")
        
        # レスポンス
        response_data = {
            "id": task_id,
            **task_data
        }
        
        return response.Response(
            ctx,
            response_data=json.dumps(response_data),
            headers={"Content-Type": "application/json"},
            status_code=201
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

import io
import json
import logging
import os
import urllib.parse

import oci
from fdk import response

def handler(ctx, data: io.BytesIO = None):
    """
    タスク削除Function
    POST /delete?id=<task_id>
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
        
        # まず該当タスクが存在するかチェック
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
        
        # タスクを削除
        nosql_client.delete_row(
            table_name_or_id=table_name,
            key=[f"id:{task_id}"],
            compartment_id=compartment_id
        )
        
        logger.info(f"Task deleted successfully with ID: {task_id}")
        
        # レスポンス
        return response.Response(
            ctx,
            response_data=json.dumps({"message": f"Task '{task_id}' deleted successfully"}),
            headers={"Content-Type": "application/json"},
            status_code=200
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

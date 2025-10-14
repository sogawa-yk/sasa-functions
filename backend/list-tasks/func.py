import io
import json
import logging
import os

import oci
from fdk import response

def handler(ctx, data: io.BytesIO = None):
    """
    タスクリスト取得Function
    GET /list
    """
    logger = logging.getLogger()
    
    try:
        # Resource Principal認証でOCIクライアント初期化
        signer = oci.auth.signers.get_resource_principals_signer()
        nosql_client = oci.nosql.NosqlClient(config={}, signer=signer)
        
        # 環境変数からテーブル名を取得
        table_name = os.environ.get("NOSQL_TABLE_NAME")
        logger.info(f"Using table name: {table_name}")
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
        logger.info(f"compartment_id: {compartment_id}")
        # 全タスクを取得するためにクエリ実行
        query_details = oci.nosql.models.QueryDetails(
            statement=f"SELECT * FROM {table_name}",
            compartment_id=compartment_id,
            max_read_in_k_bs=1000  # 読み取り制限（必要に応じて調整）
        )
        
        tasks = []
        page_token = None
        
        # ページネーション対応でクエリ結果を取得
        while True:
            query_response = nosql_client.query(
                query_details=query_details,
                page=page_token
            )
            
            if query_response.data.items:
                tasks.extend(query_response.data.items)
            
            # 次のページがあるかチェック
            page_token = query_response.headers.get('opc-next-page')
            if not page_token:
                break
        
        # タスクリストを作成日時でソート（新しい順）
        try:
            tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        except Exception as sort_ex:
            logger.warning(f"Failed to sort tasks by created_at: {str(sort_ex)}")
            # ソートに失敗してもエラーにはしない
        
        logger.info(f"Retrieved {len(tasks)} tasks successfully")
        
        # レスポンス
        return response.Response(
            ctx,
            response_data=json.dumps(tasks),
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

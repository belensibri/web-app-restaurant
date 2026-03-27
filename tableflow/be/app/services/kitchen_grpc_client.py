import grpc
from app.grpc import kitchen_pb2, kitchen_pb2_grpc
from app.config import settings

def _get_stub():
    channel = grpc.insecure_channel(
        f"{settings.kitchen_grpc_host}:{settings.kitchen_grpc_port}"
    )
    return kitchen_pb2_grpc.KitchenServiceStub(channel)

def submit_order(order_id: int, table_number: int) -> bool:
    try:
        response = _get_stub().SubmitOrder(
            kitchen_pb2.OrderRequest(order_id=order_id, table_number=table_number)
        )
        return response.accepted
    except grpc.RpcError as e:
        print(f"gRPC SubmitOrder failed: {e}")
        return False

def update_order_status(order_id: int, new_status: str) -> bool:
    try:
        response = _get_stub().UpdateOrderStatus(
            kitchen_pb2.UpdateStatusRequest(order_id=order_id, status=new_status)
        )
        return response.success
    except grpc.RpcError as e:
        print(f"gRPC UpdateOrderStatus failed: {e}")
        return False

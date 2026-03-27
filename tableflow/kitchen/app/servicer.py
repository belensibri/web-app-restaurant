from app.generated import kitchen_pb2, kitchen_pb2_grpc

class KitchenServicer(kitchen_pb2_grpc.KitchenServiceServicer):
    _queue: dict[int, str] = {}
    _TRANSITIONS: dict[str, set[str]] = {
        "received":  {"preparing", "cancelled"},
        "preparing": {"ready",     "cancelled"},
        "ready":     {"delivered", "cancelled"},
        "delivered": set(),
        "cancelled": set(),
    }

    def SubmitOrder(self, request, context):
        if request.order_id not in self._queue:
            self._queue[request.order_id] = "received"
        return kitchen_pb2.OrderAck(order_id=request.order_id, accepted=True)

    def UpdateOrderStatus(self, request, context):
        current = self._queue.get(request.order_id)
        if not current:
            return kitchen_pb2.StatusResponse(order_id=request.order_id, status=request.status, success=False)
            
        if request.status not in self._TRANSITIONS[current]:
            return kitchen_pb2.StatusResponse(order_id=request.order_id, status=request.status, success=False)
            
        self._queue[request.order_id] = request.status
        return kitchen_pb2.StatusResponse(order_id=request.order_id, status=request.status, success=True)

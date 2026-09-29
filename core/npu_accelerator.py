from typing import Dict
from loguru import logger


class NPUAccelerator:
    def __init__(self):
        self.is_available = False
        self.provider_name = "CPUExecutionProvider"
        self.npu_info = {}
        self._detect()

    def _detect(self):
        try:
            import onnxruntime as ort
            providers = ort.get_available_providers()
            logger.info(f"ONNX providers: {providers}")
            if "QNNExecutionProvider" in providers:
                self.is_available = True
                self.provider_name = "QNNExecutionProvider"
                self.npu_info = {
                    "name": "Qualcomm Hexagon NPU",
                    "target": "Snapdragon X Elite/Plus",
                }
                logger.success("Qualcomm NPU detected!")
            else:
                logger.info("Using CPU inference (NPU not found)")
        except ImportError:
            logger.info("ONNX Runtime not installed")

    def get_status_info(self) -> Dict:
        return {
            "available": self.is_available,
            "provider": self.provider_name,
            "status": (
                "NPU Active (Snapdragon)" if self.is_available else "CPU Mode"
            ),
        }

from pathlib import Path
from typing import Dict
from loguru import logger


class ModelManager:
    MODELS_DIR = Path("models/cached")

    def __init__(self):
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    def ensure_models_available(self) -> Dict[str, bool]:
        out_path = self.MODELS_DIR / "mobilenetv2.onnx"
        if out_path.exists():
            logger.info("MobileNetV2 ONNX model found")
            return {"mobilenet_v2": True}
        return {"mobilenet_v2": self._export(out_path)}

    def _export(self, out: Path) -> bool:
        try:
            import torch
            import torchvision
            logger.info("Exporting MobileNetV2 to ONNX...")
            model = torchvision.models.mobilenet_v2(weights="DEFAULT")
            model.eval()
            dummy = torch.randn(1, 3, 224, 224)
            torch.onnx.export(
                model, dummy, str(out),
                input_names=["input"],
                output_names=["output"],
                opset_version=17,
            )
            logger.success(f"Model exported to {out}")
            return True
        except Exception as e:
            logger.warning(f"Model export skipped: {e}")
            return False

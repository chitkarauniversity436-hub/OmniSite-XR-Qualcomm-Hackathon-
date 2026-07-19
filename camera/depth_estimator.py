"""
depth_estimator.py
-------------------
Wraps Intel ISL's MiDaS monocular depth model so you can get a
distance estimate for every object in frame, not just detected people.

Usage from live_camera_detect.py:

    from depth_estimator import DepthEstimator
    depth_est = DepthEstimator(device="cuda")   # falls back to cpu if no GPU

    # inside your main loop, once per frame you want depth for:
    depth_map = depth_est.predict(frame)        # HxW float array, relative depth
    obj_distance_m = depth_est.distance_for_box(depth_map, x1, y1, x2, y2)

Notes:
- MiDaS gives *relative* inverse depth by default (not metric meters) unless
  you calibrate it. For your rescue-dashboard use case, relative depth is
  usually enough to say "this is closer than that" and to color/rank objects.
- If you want it in real meters like your existing bbox-height formula,
  calibrate() below does a one-point linear fit the same way you calibrated
  FOCAL_LENGTH_PX — stand at a known distance, capture the model's raw
  depth value at that point, and it computes a scale/offset for you.
"""

import cv2
import numpy as np
import torch


class DepthEstimator:
    def __init__(self, model_type="MiDaS_small", device=None):
        """
        model_type options (speed vs accuracy):
          - "MiDaS_small"  -> fastest, ~1-2GB VRAM, good for real-time demo
          - "DPT_Hybrid"   -> more accurate, more VRAM, still fine on 6GB
          - "DPT_Large"    -> most accurate, heaviest, skip for a live demo
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.model = torch.hub.load("intel-isl/MiDaS", model_type)
        self.model.to(self.device)
        self.model.eval()

        transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        self.transform = (
            transforms.small_transform
            if model_type == "MiDaS_small"
            else transforms.dpt_transform
        )

        # calibration: raw_depth_value -> meters, set via calibrate()
        self._scale = None
        self._offset = None

    def predict(self, frame_bgr):
        """
        frame_bgr: a single OpenCV frame (BGR, as read from cv2.VideoCapture).
        Returns: 2D numpy array, same H/W as input, relative inverse depth
                 (bigger value = closer, by MiDaS convention).
        """
        img_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        input_batch = self.transform(img_rgb).to(self.device)

        with torch.no_grad():
            prediction = self.model(input_batch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img_rgb.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()

        return prediction.cpu().numpy()

    def distance_for_box(self, depth_map, x1, y1, x2, y2):
        """
        Average the depth map over a bounding box (e.g. a YOLO detection)
        and return either the raw relative value, or meters if calibrated.
        """
        x1, y1 = max(0, int(x1)), max(0, int(y1))
        x2, y2 = min(depth_map.shape[1], int(x2)), min(depth_map.shape[0], int(y2))
        if x2 <= x1 or y2 <= y1:
            return None

        region = depth_map[y1:y2, x1:x2]
        raw_value = float(np.median(region))  # median is more robust than mean here

        if self._scale is not None:
            # MiDaS output is inverse depth, so convert: distance = scale / raw + offset
            return round(self._scale / raw_value + self._offset, 2)
        return round(raw_value, 3)  # relative units if not calibrated

    def calibrate(self, known_distance_m, raw_value_at_that_distance, offset=0.0):
        """
        One-point calibration, mirrors your FOCAL_LENGTH_PX approach.
        Call this once with a real measured distance and the raw_value
        distance_for_box() reported at that distance, then reuse the
        instance for the rest of the session.
        """
        self._scale = known_distance_m * raw_value_at_that_distance
        self._offset = offset

    def depth_overlay(self, depth_map):
        """
        Returns a colorized BGR image for display purposes (demo eye-candy:
        show this side-by-side with the raw camera feed).
        """
        norm = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
        norm = norm.astype(np.uint8)
        return cv2.applyColorMap(norm, cv2.COLORMAP_MAGMA)
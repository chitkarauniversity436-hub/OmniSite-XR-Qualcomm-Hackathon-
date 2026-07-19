const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:5000";

export default function LiveCamera() {
  return (
    <div className="chart-panel">
      <h2>Live Camera — Person Detection</h2>
      <div style={{ borderRadius: 6, overflow: "hidden", border: "1px solid #1c3634" }}>
        <img
          src={`${BASE_URL}/video_feed`}
          alt="Live camera feed"
          style={{ display: "block", width: "100%", background: "#000" }}
          onError={(e) => {
            e.target.style.display = "none";
          }}
        />
      </div>
      <div className="status-line">
        no feed yet? start camera/live_camera_detect.py
      </div>
    </div>
  );
}

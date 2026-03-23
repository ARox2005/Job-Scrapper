import { useRef, useState } from "react";
import { uploadResume } from "../api";

function ResumeUpload({ resumeName, onUpload }) {
    const fileInput = useRef(null);
    const [uploading, setUploading] = useState(false);
    async function handleFile(e) {
        const file = e.target.files[0];
        if (!file) return;
        setUploading(true);
        try {
            const data = await uploadResume(file);
            onUpload(data.resume_id, data.filename);
        } catch (err) {
            console.error("Upload failed:", err);
        } finally {
            setUploading(false);
        }
    }
    return (
        <div className="card">
            <h2>📄 Resume</h2>
            <div className="upload-zone" onClick={() => fileInput.current.click()}>
                <input
                    ref={fileInput}
                    type="file"
                    accept=".pdf"
                    onChange={handleFile}
                />
                <div className="icon">📁</div>
                <p>{uploading ? "Uploading..." : "Click to upload your resume (PDF)"}</p>
            </div>
            {resumeName && (
                <p className="upload-success">✅ Loaded: {resumeName}</p>
            )}
        </div>
    );
}
export default ResumeUpload;
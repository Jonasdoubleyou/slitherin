import { useEffect, useRef, useState } from "react"
import { Pattern, scanStream } from "./pattern";

export function Scanner({ onStart }: { onStart: (pattern: Pattern) => void }) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [showCanvas, setShowCanvas] = useState(false);
    const [result, setResult] = useState<Pattern | null>(null);

    const resumeRef = useRef<() => void>(() => {});
    const makePhotoRef = useRef<() => void>(() => {});

    // On Mount, request camera access, and start a stream from the camera to the video element
    useEffect(() => {
        if (!videoRef.current) return;

        // Prefer camera resolution nearest to 1280x720.
        const constraints = {
            audio: false,
            video: { width: 720, height: 720, facingMode: "environment" },
        };
        
        ("mediaDevices" in navigator ? navigator.mediaDevices.getUserMedia(constraints) : new Promise<MediaProvider>(res => (navigator as any).getUserMedia(constraints, res)))
            .then((mediaStream: MediaProvider) => {
            videoRef.current!.srcObject = mediaStream;
            videoRef.current!.onloadedmetadata = () => {
                videoRef.current!.play();
            };
            })
            .catch((err) => {
                console.error(`${err.name}: ${err.message}`);
            });
    }, [videoRef.current]);

    // Once the video stream is there, start scanning the stream for patterns
    useEffect(() => {
        if (!videoRef.current || !canvasRef.current) return;
        
        const { cancel, makePhoto, resume } = scanStream(videoRef.current, canvasRef.current, (result) => {
            setShowCanvas(true);
            setResult(result);
        });

        resumeRef.current = resume;
        makePhotoRef.current = makePhoto;

        return cancel;
    }, [videoRef.current, canvasRef.current]);

    return <div>
        <h3 className="info">
            Make a photo from the top of the puzzle while standing in front of the display.
        </h3>
        <video style={showCanvas ? { display: "none" } : {}} width="350px" height="350px" ref={videoRef}
            playsInline />
        <canvas style={!showCanvas ? { display: "none" } : {}} width="350px" height="350px" ref={canvasRef} />

        {!showCanvas && <button onClick={() => { makePhotoRef.current(); }}>Scan!</button>}
        {showCanvas && <button onClick={() => { setShowCanvas(false); resumeRef.current(); setResult(null); }}>Scan again</button>}
        {result && <button onClick={() => onStart(result)}>Start</button>}
    </div>
}
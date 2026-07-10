// Camera management functions

let currentStreams = {};

function initializeCamera(videoId) {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true, audio: false })
            .then(function(stream) {
                const video = document.getElementById(videoId);
                if (video) {
                    video.srcObject = stream;
                    currentStreams[videoId] = stream;
                }
            })
            .catch(function(error) {
                console.error('Error accessing camera:', error);
                const video = document.getElementById(videoId);
                if (video) {
                    video.parentElement.innerHTML = `
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle"></i> 
                            Unable to access camera. Please ensure you have granted camera permissions.
                        </div>
                    `;
                }
            });
    } else {
        console.error('Camera not supported');
        const video = document.getElementById(videoId);
        if (video) {
            video.parentElement.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-times-circle"></i> 
                    Camera not supported in this browser.
                </div>
            `;
        }
    }
}

function captureImage(inputId) {
    const videoId = inputId === 'image1_data' ? 'video' : 'video2';
    const video = document.getElementById(videoId);
    const canvas = document.getElementById(inputId === 'image1_data' ? 'canvas1' : 'canvas2');
    
    if (video && canvas) {
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw video frame to canvas
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert to base64
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        document.getElementById(inputId).value = imageData;
        
        // Show preview
        const previewDiv = document.getElementById(inputId === 'image1_data' ? 'image1_preview' : 'image2_preview');
        previewDiv.innerHTML = `
            <img src="${imageData}" style="max-width: 100%; max-height: 150px; border-radius: 4px; border: 2px solid #28a745;">
            <p class="text-success small mt-1"><i class="fas fa-check-circle"></i> Image captured!</p>
        `;
    }
}

// Video recording functionality
let mediaRecorder = null;
let recordedChunks = [];

function setupVideoRecording() {
    const startBtn = document.getElementById('startVideoBtn');
    const stopBtn = document.getElementById('stopVideoBtn');
    
    if (startBtn) {
        startBtn.addEventListener('click', startRecording);
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', stopRecording);
    }
}

function startRecording() {
    const video = document.getElementById('video3');
    
    if (video && video.srcObject) {
        const stream = video.srcObject;
        
        // Create MediaRecorder
        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'video/webm;codecs=vp9'
        });
        
        recordedChunks = [];
        
        mediaRecorder.ondataavailable = function(event) {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = function() {
            // Create video blob
            const blob = new Blob(recordedChunks, {
                type: 'video/webm'
            });
            
            // Convert to base64
            const reader = new FileReader();
            reader.onload = function(e) {
                const base64Data = e.target.result;
                document.getElementById('video_data').value = base64Data;
                
                // Show preview
                const previewDiv = document.getElementById('video_preview');
                previewDiv.innerHTML = `
                    <video controls style="max-width: 100%; max-height: 150px; border-radius: 4px;">
                        <source src="${URL.createObjectURL(blob)}" type="video/webm">
                    </video>
                    <p class="text-success small mt-1"><i class="fas fa-check-circle"></i> Video recorded!</p>
                `;
            };
            reader.readAsDataURL(blob);
        };
        
        // Start recording
        mediaRecorder.start();
        
        // Update button visibility
        document.getElementById('startVideoBtn').style.display = 'none';
        document.getElementById('stopVideoBtn').style.display = 'inline-block';
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        
        // Reset button visibility
        document.getElementById('startVideoBtn').style.display = 'inline-block';
        document.getElementById('stopVideoBtn').style.display = 'none';
    }
}

// Clean up streams when page unloads
window.addEventListener('beforeunload', function() {
    for (let streamId in currentStreams) {
        const stream = currentStreams[streamId];
        if (stream && stream.getTracks) {
            stream.getTracks().forEach(track => track.stop());
        }
    }
});
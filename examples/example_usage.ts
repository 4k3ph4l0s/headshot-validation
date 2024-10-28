import { spawn } from 'child_process';

function validateHeadshot(imagePath: string): Promise<boolean> {
    return new Promise((resolve, reject) => {
        const process = spawn('python3', ['../headshot_validation.py', '--image-path', imagePath]);

        process.on('close', (code) => {
            resolve(code === 0);  // Returns true if exit code is 0, false otherwise
        });

        process.on('error', (error) => {
            reject(`Failed to start process: ${error.message}`);
        });
    });
}

(async () => {
    const imagePath = "/path/to/image.jpg";  // Set your image path here
    try {
        const isValid = await validateHeadshot(imagePath);
        if (isValid) {
            console.log("Image is valid headshot.");
        } else {
            console.log("Image is no valid headshot.");
        }
    } catch (error) {
        console.error("Error:", error);
    }
})();
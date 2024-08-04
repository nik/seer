"use client";

import { useState, useCallback, useRef } from "react";
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Label } from '@/components/ui/label';

export default function Page() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = useCallback((file: File | null) => {
    if (file && file.type === 'application/zip') {
      setSelectedFile(file);
      if (fileInputRef.current) {
        // Create a new FileList containing the selected file
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInputRef.current.files = dataTransfer.files;
      }
    } else {
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      if (file) {
        alert('Please select a zip file');
      }
    }
  }, []);

  const handleUpload = () => {
    if (selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const xhr = new XMLHttpRequest();
      xhr.open('POST', 'http://localhost:8000/upload');

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          setUploadProgress(progress);
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200) {
          const result = JSON.parse(xhr.responseText);
          console.log('Upload result:', result);
        } else {
          console.error('Error uploading file:', xhr.statusText);
          alert('Error uploading file');
        }
        setUploadProgress(null);
      };

      xhr.onerror = () => {
        console.error('Error uploading file');
        alert('Error uploading file');
        setUploadProgress(null);
      };

      xhr.send(formData);
    } else {
      alert('Please select a file first');
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-white">
      <div className="flex flex-col items-center justify-center">
        <div className="grid w-full max-w-sm items-center gap-2">
          <Label htmlFor="file">Upload your code</Label>
          <Input
            ref={fileInputRef}
            id="file"
            type="file"
            accept=".zip"
            onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
          />
          {selectedFile && (
            <p className="mt-2 text-sm">Selected file: {selectedFile.name}</p>
          )}
          <Button className="w-full max-w-sm" onClick={handleUpload}>
            Upload
          </Button>
          {uploadProgress !== null && (
            <div className="w-full">
              <Progress value={uploadProgress} className="w-full" />
              <p className="text-sm text-center mt-1">{uploadProgress}%</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

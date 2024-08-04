"use client";

import { useState, useCallback, useRef } from "react";
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function Page() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
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

  const handleDragEnter = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      handleFileChange(file);
    },
    [handleFileChange]
  );

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
          alert(
            result.status === 'success'
              ? 'File uploaded successfully'
              : 'Upload failed'
          );
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
      <h1 className="text-3xl font-bold mb-8">Upload Zipped Codebase</h1>
      <div className="flex flex-col items-center justify-center">
        <Input
          ref={fileInputRef}
          type="file"
          accept=".zip"
          onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
        />
      </div>
      {selectedFile && (
        <p className="mt-4 text-sm">Selected file: {selectedFile.name}</p>
      )}
      <Button className="mt-4" onClick={handleUpload}>
        Upload
      </Button>
    </main>
  );
}

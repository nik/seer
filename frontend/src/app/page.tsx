"use client"

import { useState, useCallback, useRef } from "react"

export default function Page() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<number | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = useCallback((file: File | null) => {
    if (file && file.type === "application/zip") {
      setSelectedFile(file)
      if (fileInputRef.current) {
        // Create a new FileList containing the selected file
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        fileInputRef.current.files = dataTransfer.files
      }
    } else {
      setSelectedFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
      if (file) {
        alert("Please select a zip file")
      }
    }
  }, [])

  const handleDragEnter = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    handleFileChange(file)
  }, [handleFileChange])

  const handleUpload = () => {
    if (selectedFile) {
      const formData = new FormData()
      formData.append("file", selectedFile)

      const xhr = new XMLHttpRequest()
      xhr.open("POST", "http://localhost:8000/upload")

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100)
          setUploadProgress(progress)
        }
      }

      xhr.onload = () => {
        if (xhr.status === 200) {
          const result = JSON.parse(xhr.responseText)
          console.log("Upload result:", result)
          alert(result.status === "success" ? "File uploaded successfully" : "Upload failed")
        } else {
          console.error("Error uploading file:", xhr.statusText)
          alert("Error uploading file")
        }
        setUploadProgress(null)
      }

      xhr.onerror = () => {
        console.error("Error uploading file")
        alert("Error uploading file")
        setUploadProgress(null)
      }

      xhr.send(formData)
    } else {
      alert("Please select a file first")
    }
  }

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-white">
      <h1 className="text-3xl font-bold mb-8">Upload Zipped Codebase</h1>
      <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-lg"> 
        <div
        className={`flex flex-col items-center justify-center w-full h-64 ${
          isDragging ? "border-black bg-gray-100" : "border-gray-300"
        }`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        >
          <p className="text-center mb-4">Drag and drop a zip file here</p>
          <p className="text-center mb-4">or</p>
          <div className="w-full flex justify-center">
            <input
              ref={fileInputRef}
              type="file"
              accept=".zip"
              onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
              className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-black file:text-white hover:file:bg-gray-800"
            />
          </div>
        </div>
        {selectedFile && (
          <p className="mt-4 text-sm">Selected file: {selectedFile.name}</p>
        )}
        {uploadProgress !== null && (
          <div className="w-full mt-4">
            <div className="bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
              <div
                className="bg-blue-600 h-2.5 rounded-full"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-center mt-2">{uploadProgress}% uploaded</p>
          </div>
        )}
        <button
          onClick={handleUpload}
          className="mt-4 bg-black text-white py-2 px-4 rounded-full hover:bg-gray-800"
        >
          Upload
        </button>
      </div>
    </main>
  )
}
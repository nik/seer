'use client';

import { useState, useEffect } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/ui/spinner';

export default function Page() {
  const [text, setText] = useState('');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setTaskId(data.task_id);
      setJobStatus('PENDING');
    } catch (error) {
      console.error('Error submitting query:', error);
    }
  };

  useEffect(() => {
    const checkJobStatus = async () => {
      if (taskId && jobStatus !== 'SUCCESS') {
        try {
          const response = await fetch(
            `http://localhost:8000/job_status/${taskId}`
          );
          if (response.ok) {
            const data = await response.json();
            setJobStatus(data.status);
          }
        } catch (error) {
          console.error('Error checking job status:', error);
        }
      }
    };

    const intervalId = setInterval(checkJobStatus, 5000); // Check every 5 seconds

    return () => clearInterval(intervalId);
  }, [taskId, jobStatus]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white">
      <form onSubmit={handleSubmit} className="w-full max-w-md">
        <Textarea
          className="min-h-[200px] mb-4 p-2"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="What would you like to know about your product?"
        />
        <Button className="w-full" type="submit">
          Submit
        </Button>
      </form>
      {jobStatus && jobStatus !== 'SUCCESS' && (
        <div className="mt-4">
          <LoadingSpinner />
          <p>Job status: {jobStatus}</p>
        </div>
      )}
    </div>
  );
}
'use client';

import { useState, useEffect } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/ui/spinner';

export default function Page() {
  const [text, setText] = useState('');
  const [generatorTaskId, setGeneratorTaskId] = useState<string | null>(null);
  const [listenerTaskId, setListenerTaskId] = useState<string | null>(null);
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
      setGeneratorTaskId(data.task_id);
      setListenerTaskId(data.listener_task_id);
      setJobStatus('PROGRESS');
    } catch (error) {
      console.error('Error submitting query:', error);
    }
  };

  useEffect(() => {
    if (generatorTaskId) {
      const eventSource = new EventSource(
        `http://localhost:8000/generator_job/${generatorTaskId}`
      );

      eventSource.addEventListener('job_status', (event) => {
        setJobStatus(event.data);

        if (event.data === 'SUCCESS' || event.data === 'FAILURE') {
          setJobStatus(event.data);
          eventSource.close();
        }
      });

      eventSource.onerror = (error) => {
        console.error('EventSource failed:', error);
        eventSource.close();
      };

      return () => {
        eventSource.close();
      };
    }

    if (listenerTaskId) {
      const eventSource = new EventSource(
        `http://localhost:8000/listener_job/${listenerTaskId}`
      );
      eventSource.addEventListener('screenshot', (event) => {
        console.log(event.data);
      });
      eventSource.addEventListener('end', (event) => {
        console.log(event.data);
        eventSource.close();
      });
      eventSource.onerror = (error) => {
        console.error('EventSource failed:', error);
        eventSource.close();
      };
      return () => {
        eventSource.close();
      };
    }
  }, [generatorTaskId, listenerTaskId]);

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
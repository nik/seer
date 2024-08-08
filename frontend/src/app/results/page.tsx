'use client';

import { useState } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';

export default function Page() {
  const [text, setText] = useState('');

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
      console.log('Query submitted successfully');
    } catch (error) {
      console.error('Error submitting query:', error);
    }
  };

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
    </div>
  );
}
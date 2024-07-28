async function getData() {
  const res = await fetch('http://127.0.0.1:8000/items/2')
 
  if (!res.ok) {
    throw new Error('Failed to fetch data')
  }
 
  return res.json()
}

export default async function Page() {
  const data = await getData()

  return (
    <main>
      <h1>Hello, Next.js!</h1>
      <p>{data.item_id}</p>
    </main>
  )
}
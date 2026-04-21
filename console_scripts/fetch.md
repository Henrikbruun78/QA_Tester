## Scripts til at hente informationer

fetch('/api/products')
  .then(res => res.json())
  .then(data => console.log(data))

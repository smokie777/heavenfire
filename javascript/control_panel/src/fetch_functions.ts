export const fetch_post = async(route:string, body = {}) => {
  const res = await fetch(route, {
    method: 'post',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });
  const data = await res.json();
  return data;
};

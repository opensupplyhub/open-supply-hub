import { test, expect, APIResponse } from '@playwright/test';

[...Array(10).keys()].forEach((i) => {
test.only(`Tile should  7*7*9=441 ${i}`, async ({ request }) => {
  test.setTimeout(900000);
  const host = "http://django:8081";
  //const host = "https://preprod.os-hub.net";

  const hash =  Math.random().toString(36).substring(2, 10);
  
  let urls: string[] = [];
  for (let x = 0; x < 9; x++) {
    for (let y = 0; y < 9; y++) {
      for (let z = 0; z < 9; z++) {
        urls.push(`${host}/tile/facilitygrid/U-${hash}/${z+1}/${x+1}/${y+1}.pbf?sort_by=contributors_desc`);
      }
    }
  }

  let requests:Promise<APIResponse>[] = [];

  for (const [index, url] of urls.entries()) {
    requests.push(request.get(url, {
      headers: {
        'Referer': `${host}/?sort_by=contributors_desc`,
      }
    }) );
    if (index % 50 === 0){
      await new Promise(resolve => setTimeout(resolve, 250));
    }  
  }
  console.log(`Requesting ${urls.length} tiles`);
  

  const titles = await Promise.all(requests);
  const statuses = await titles.map((tile) => tile.status());
  console.log(statuses);
  expect(statuses).toContain(200);
  expect(statuses).toContain(429);
});
});
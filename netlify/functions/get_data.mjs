export default async (req, context) => {
  const url = new URL(req.url);
  const region = url.searchParams.get('region') || 'C';
  const daysBack = 1;
  const daysForward = 2;

  try {
    const [prices, carbon] = await Promise.all([
      fetchOctopusPrices(region, daysBack, daysForward),
      fetchCarbonIntensity(daysBack, daysForward)
    ]);

    return new Response(
      JSON.stringify({
        prices,
        carbon,
        region,
        timestamp: new Date().toISOString()
      }),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: error.message,
        type: error.name,
        stack: error.stack
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      }
    );
  }
};

async function fetchOctopusPrices(region, daysBack, daysForward) {
  const productCode = 'AGILE-24-10-01';
  const tariffCode = `E-1R-${productCode}-${region}`;

  const now = new Date();
  const start = new Date(now.getTime() - daysBack * 24 * 60 * 60 * 1000);
  const end = new Date(now.getTime() + daysForward * 24 * 60 * 60 * 1000);

  const url = new URL(
    `https://api.octopus.energy/v1/products/${productCode}/electricity-tariffs/${tariffCode}/standard-unit-rates/`
  );
  
  url.searchParams.set('period_from', start.toISOString());
  url.searchParams.set('period_to', end.toISOString());
  url.searchParams.set('page_size', '2500');

  const response = await fetch(url.toString(), {
    signal: AbortSignal.timeout(20000)
  });

  if (!response.ok) {
    throw new Error(`Octopus API error: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return data.results || [];
}

async function fetchCarbonIntensity(daysBack, daysForward) {
  const now = new Date();
  const start = new Date(now.getTime() - daysBack * 24 * 60 * 60 * 1000);
  const end = new Date(now.getTime() + daysForward * 24 * 60 * 60 * 1000);

  const startStr = start.toISOString().replace(/\.\d{3}Z$/, 'Z');
  const endStr = end.toISOString().replace(/\.\d{3}Z$/, 'Z');

  const url = `https://api.carbonintensity.org.uk/regional/intensity/${startStr}/${endStr}/regionid/13`;

  const response = await fetch(url, {
    signal: AbortSignal.timeout(20000)
  });

  if (!response.ok) {
    throw new Error(`Carbon Intensity API error: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return data.data?.data || [];
}

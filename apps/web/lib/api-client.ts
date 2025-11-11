import { OpenAPI } from '@peter/api-client';

// Configure the API client
OpenAPI.BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
OpenAPI.WITH_CREDENTIALS = true;

export { OpenAPI };
export * from '@peter/api-client';

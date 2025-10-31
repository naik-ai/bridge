/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type HealthStatus = {
    status: 'healthy' | 'degraded' | 'unhealthy';
    components?: {
        database?: 'healthy' | 'unhealthy';
        bigquery?: 'healthy' | 'unhealthy';
        cache?: 'healthy' | 'unhealthy';
        storage?: 'healthy' | 'unhealthy';
    };
    version?: string;
};


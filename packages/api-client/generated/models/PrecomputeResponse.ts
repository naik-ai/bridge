/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PrecomputeResponse = {
    status: 'success' | 'partial' | 'failed';
    queries_executed: number;
    total_duration_ms: number;
    bytes_scanned?: number;
    errors?: Array<string>;
};


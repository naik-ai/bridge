/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type VerificationPayload = {
    schema: Array<{
        name?: string;
        type?: string;
    }>;
    row_count: number;
    bytes_scanned: number;
    duration_ms: number;
    sample_rows?: Array<Record<string, any>>;
    job_id?: string;
    cache_hit?: boolean;
};


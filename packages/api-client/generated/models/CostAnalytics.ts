/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type CostAnalytics = {
    total_bytes_scanned: number;
    estimated_cost_usd: number;
    query_count: number;
    breakdown?: Array<{
        dashboard_slug?: string;
        bytes_scanned?: number;
        cost_usd?: number;
        query_count?: number;
    }>;
};


/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $CostAnalytics = {
    properties: {
        total_bytes_scanned: {
            type: 'number',
            isRequired: true,
        },
        estimated_cost_usd: {
            type: 'number',
            isRequired: true,
            format: 'float',
        },
        query_count: {
            type: 'number',
            isRequired: true,
        },
        breakdown: {
            type: 'array',
            contains: {
                properties: {
                    dashboard_slug: {
                        type: 'string',
                    },
                    bytes_scanned: {
                        type: 'number',
                    },
                    cost_usd: {
                        type: 'number',
                    },
                    query_count: {
                        type: 'number',
                    },
                },
            },
        },
    },
} as const;

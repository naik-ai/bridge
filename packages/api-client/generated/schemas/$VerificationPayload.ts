/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $VerificationPayload = {
    properties: {
        schema: {
            type: 'array',
            contains: {
                properties: {
                    name: {
                        type: 'string',
                    },
                    type: {
                        type: 'string',
                    },
                },
            },
            isRequired: true,
        },
        row_count: {
            type: 'number',
            isRequired: true,
        },
        bytes_scanned: {
            type: 'number',
            isRequired: true,
        },
        duration_ms: {
            type: 'number',
            isRequired: true,
        },
        sample_rows: {
            type: 'array',
            contains: {
                type: 'dictionary',
                contains: {
                    properties: {
                    },
                },
            },
        },
        job_id: {
            type: 'string',
        },
        cache_hit: {
            type: 'boolean',
        },
    },
} as const;

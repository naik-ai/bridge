/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $PrecomputeResponse = {
    properties: {
        status: {
            type: 'Enum',
            isRequired: true,
        },
        queries_executed: {
            type: 'number',
            isRequired: true,
        },
        total_duration_ms: {
            type: 'number',
            isRequired: true,
        },
        bytes_scanned: {
            type: 'number',
        },
        errors: {
            type: 'array',
            contains: {
                type: 'string',
            },
        },
    },
} as const;

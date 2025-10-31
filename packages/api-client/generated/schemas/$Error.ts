/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $Error = {
    properties: {
        code: {
            type: 'string',
            isRequired: true,
        },
        message: {
            type: 'string',
            isRequired: true,
        },
        details: {
            type: 'dictionary',
            contains: {
                properties: {
                },
            },
        },
        trace_id: {
            type: 'string',
        },
        remediation: {
            type: 'string',
        },
    },
} as const;

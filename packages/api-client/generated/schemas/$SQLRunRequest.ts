/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $SQLRunRequest = {
    properties: {
        sql: {
            type: 'string',
            isRequired: true,
        },
        parameters: {
            type: 'dictionary',
            contains: {
                properties: {
                },
            },
        },
        max_bytes_billed: {
            type: 'number',
        },
    },
} as const;

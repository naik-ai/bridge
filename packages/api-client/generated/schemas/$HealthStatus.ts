/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $HealthStatus = {
    properties: {
        status: {
            type: 'Enum',
            isRequired: true,
        },
        components: {
            properties: {
                database: {
                    type: 'Enum',
                },
                bigquery: {
                    type: 'Enum',
                },
                cache: {
                    type: 'Enum',
                },
                storage: {
                    type: 'Enum',
                },
            },
        },
        version: {
            type: 'string',
        },
    },
} as const;

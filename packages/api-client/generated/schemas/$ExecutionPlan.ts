/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $ExecutionPlan = {
    properties: {
        queries: {
            type: 'array',
            contains: {
                properties: {
                    query_id: {
                        type: 'string',
                    },
                    sql: {
                        type: 'string',
                    },
                    depends_on: {
                        type: 'array',
                        contains: {
                            type: 'string',
                        },
                    },
                },
            },
            isRequired: true,
        },
        lineage_seeds: {
            type: 'array',
            contains: {
                properties: {
                    query_id: {
                        type: 'string',
                    },
                    tables: {
                        type: 'array',
                        contains: {
                            type: 'string',
                        },
                    },
                },
            },
            isRequired: true,
        },
    },
} as const;

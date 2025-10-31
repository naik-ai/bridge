/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $ChartData = {
    properties: {
        chart_id: {
            type: 'string',
            isRequired: true,
        },
        data: {
            type: 'array',
            contains: {
                type: 'dictionary',
                contains: {
                    properties: {
                    },
                },
            },
            isRequired: true,
        },
        as_of: {
            type: 'DateTime',
            isRequired: true,
        },
        source: {
            type: 'string',
        },
    },
} as const;

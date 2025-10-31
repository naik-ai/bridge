/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $DashboardData = {
    properties: {
        charts: {
            type: 'dictionary',
            contains: {
                type: 'ChartData',
            },
            isRequired: true,
        },
        as_of: {
            type: 'DateTime',
            isRequired: true,
        },
        cache_hit: {
            type: 'boolean',
        },
    },
} as const;

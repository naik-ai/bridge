/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $FreshnessInfo = {
    properties: {
        chart_id: {
            type: 'string',
            isRequired: true,
        },
        as_of: {
            type: 'DateTime',
            isRequired: true,
        },
        age_seconds: {
            type: 'number',
            isRequired: true,
        },
        status: {
            type: 'Enum',
        },
    },
} as const;

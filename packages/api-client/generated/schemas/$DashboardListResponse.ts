/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $DashboardListResponse = {
    properties: {
        dashboards: {
            type: 'array',
            contains: {
                type: 'DashboardMetadata',
            },
            isRequired: true,
        },
        total: {
            type: 'number',
            isRequired: true,
        },
        page: {
            type: 'number',
        },
        page_size: {
            type: 'number',
        },
    },
} as const;

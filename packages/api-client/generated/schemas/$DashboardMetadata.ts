/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $DashboardMetadata = {
    properties: {
        id: {
            type: 'UUID',
            isRequired: true,
        },
        slug: {
            type: 'string',
            isRequired: true,
            pattern: '^[a-z0-9-]+$',
        },
        name: {
            type: 'string',
            isRequired: true,
        },
        description: {
            type: 'string',
            isNullable: true,
        },
        owner_id: {
            type: 'UUID',
            isRequired: true,
        },
        owner_email: {
            type: 'string',
            format: 'email',
        },
        storage_path: {
            type: 'string',
        },
        version: {
            type: 'number',
            isRequired: true,
            minimum: 1,
        },
        view_type: {
            type: 'ViewType',
            isRequired: true,
        },
        tags: {
            type: 'array',
            contains: {
                type: 'string',
            },
        },
        created_at: {
            type: 'DateTime',
            isRequired: true,
        },
        updated_at: {
            type: 'DateTime',
            isRequired: true,
        },
        last_accessed: {
            type: 'DateTime',
            isNullable: true,
        },
        access_count: {
            type: 'number',
        },
    },
} as const;

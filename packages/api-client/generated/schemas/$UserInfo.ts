/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $UserInfo = {
    properties: {
        id: {
            type: 'UUID',
            isRequired: true,
        },
        email: {
            type: 'string',
            isRequired: true,
            format: 'email',
        },
        name: {
            type: 'string',
            isNullable: true,
        },
        created_at: {
            type: 'DateTime',
        },
        last_login: {
            type: 'DateTime',
            isNullable: true,
        },
    },
} as const;

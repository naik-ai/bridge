/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $LineageNode = {
    properties: {
        id: {
            type: 'UUID',
            isRequired: true,
        },
        node_type: {
            type: 'NodeType',
            isRequired: true,
        },
        node_id: {
            type: 'string',
            isRequired: true,
        },
        metadata: {
            type: 'dictionary',
            contains: {
                properties: {
                },
            },
        },
    },
} as const;

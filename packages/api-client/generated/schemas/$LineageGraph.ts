/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $LineageGraph = {
    properties: {
        nodes: {
            type: 'array',
            contains: {
                type: 'LineageNode',
            },
            isRequired: true,
        },
        edges: {
            type: 'array',
            contains: {
                type: 'LineageEdge',
            },
            isRequired: true,
        },
    },
} as const;

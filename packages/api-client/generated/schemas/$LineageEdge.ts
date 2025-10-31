/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $LineageEdge = {
    properties: {
        source_node_id: {
            type: 'UUID',
            isRequired: true,
        },
        target_node_id: {
            type: 'UUID',
            isRequired: true,
        },
        edge_type: {
            type: 'EdgeType',
            isRequired: true,
        },
    },
} as const;

/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EdgeType } from './EdgeType';
import type { UUID } from './UUID';
export type LineageEdge = {
    source_node_id: UUID;
    target_node_id: UUID;
    edge_type: EdgeType;
};


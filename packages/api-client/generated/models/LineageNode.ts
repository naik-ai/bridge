/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NodeType } from './NodeType';
import type { UUID } from './UUID';
export type LineageNode = {
    id: UUID;
    node_type: NodeType;
    node_id: string;
    metadata?: Record<string, any>;
};


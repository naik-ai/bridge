/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DateTime } from './DateTime';
import type { UUID } from './UUID';
import type { ViewType } from './ViewType';
export type DashboardMetadata = {
    id: UUID;
    slug: string;
    name: string;
    description?: string | null;
    owner_id: UUID;
    owner_email?: string;
    storage_path?: string;
    version: number;
    view_type: ViewType;
    tags?: Array<string>;
    created_at: DateTime;
    updated_at: DateTime;
    last_accessed?: DateTime | null;
    access_count?: number;
};


/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DateTime } from './DateTime';
import type { UUID } from './UUID';
export type UserInfo = {
    id: UUID;
    email: string;
    name?: string | null;
    created_at?: DateTime;
    last_login?: DateTime | null;
};


/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DateTime } from './DateTime';
export type FreshnessInfo = {
    chart_id: string;
    as_of: DateTime;
    age_seconds: number;
    status?: 'fresh' | 'stale' | 'unknown';
};


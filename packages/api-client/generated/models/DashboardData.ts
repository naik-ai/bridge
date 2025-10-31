/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChartData } from './ChartData';
import type { DateTime } from './DateTime';
export type DashboardData = {
    charts: Record<string, ChartData>;
    as_of: DateTime;
    cache_hit?: boolean;
};


/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CostAnalytics } from '../models/CostAnalytics';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AnalyticsService {
    /**
     * Get cost analytics
     * @param startDate
     * @param endDate
     * @param dashboardSlug
     * @param groupBy
     * @returns CostAnalytics Cost analytics
     * @throws ApiError
     */
    public static getCostAnalytics(
        startDate?: string,
        endDate?: string,
        dashboardSlug?: string,
        groupBy?: 'dashboard' | 'user' | 'date',
    ): CancelablePromise<CostAnalytics> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/costs',
            query: {
                'start_date': startDate,
                'end_date': endDate,
                'dashboard_slug': dashboardSlug,
                'group_by': groupBy,
            },
        });
    }
}

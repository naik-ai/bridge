/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DashboardData } from '../models/DashboardData';
import type { FreshnessInfo } from '../models/FreshnessInfo';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DataService {
    /**
     * Get dashboard data
     * @param slug
     * @param forceRefresh
     * @returns DashboardData Dashboard data
     * @throws ApiError
     */
    public static getDashboardData(
        slug: string,
        forceRefresh: boolean = false,
    ): CancelablePromise<DashboardData> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dashboards/{slug}/data',
            path: {
                'slug': slug,
            },
            query: {
                'force_refresh': forceRefresh,
            },
        });
    }
    /**
     * Get data freshness
     * @param slug
     * @returns FreshnessInfo Freshness information
     * @throws ApiError
     */
    public static getDataFreshness(
        slug: string,
    ): CancelablePromise<Array<FreshnessInfo>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dashboards/{slug}/freshness',
            path: {
                'slug': slug,
            },
        });
    }
}

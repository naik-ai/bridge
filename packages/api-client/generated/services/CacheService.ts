/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PrecomputeRequest } from '../models/PrecomputeRequest';
import type { PrecomputeResponse } from '../models/PrecomputeResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CacheService {
    /**
     * Precompute dashboard data
     * @param slug
     * @param requestBody
     * @returns PrecomputeResponse Precompute results
     * @throws ApiError
     */
    public static precomputeDashboard(
        slug: string,
        requestBody?: PrecomputeRequest,
    ): CancelablePromise<PrecomputeResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/dashboards/{slug}/precompute',
            path: {
                'slug': slug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Invalidate cache
     * @param slug
     * @param pattern
     * @returns any Cache invalidated
     * @throws ApiError
     */
    public static invalidateCache(
        slug?: string,
        pattern?: string,
    ): CancelablePromise<{
        keys_deleted?: number;
    }> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/cache',
            query: {
                'slug': slug,
                'pattern': pattern,
            },
        });
    }
}

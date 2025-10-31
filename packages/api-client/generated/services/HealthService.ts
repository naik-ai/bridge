/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HealthStatus } from '../models/HealthStatus';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class HealthService {
    /**
     * Health check
     * @returns HealthStatus Service health status
     * @throws ApiError
     */
    public static getHealth(): CancelablePromise<HealthStatus> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health',
        });
    }
    /**
     * Readiness probe
     * @returns any Service is ready
     * @throws ApiError
     */
    public static getReadiness(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/ready',
            errors: {
                503: `Service not ready`,
            },
        });
    }
}

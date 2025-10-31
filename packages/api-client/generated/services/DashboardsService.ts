/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DashboardCreate } from '../models/DashboardCreate';
import type { DashboardListResponse } from '../models/DashboardListResponse';
import type { DashboardMetadata } from '../models/DashboardMetadata';
import type { DashboardUpdate } from '../models/DashboardUpdate';
import type { DashboardYAML } from '../models/DashboardYAML';
import type { ExecutionPlan } from '../models/ExecutionPlan';
import type { UUID } from '../models/UUID';
import type { ValidationResult } from '../models/ValidationResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DashboardsService {
    /**
     * List dashboards
     * @param page
     * @param pageSize
     * @param tags
     * @param ownerId
     * @returns DashboardListResponse List of dashboards
     * @throws ApiError
     */
    public static listDashboards(
        page: number = 1,
        pageSize: number = 20,
        tags?: Array<string>,
        ownerId?: UUID,
    ): CancelablePromise<DashboardListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dashboards',
            query: {
                'page': page,
                'page_size': pageSize,
                'tags': tags,
                'owner_id': ownerId,
            },
        });
    }
    /**
     * Create dashboard
     * @param requestBody
     * @returns DashboardMetadata Dashboard created
     * @throws ApiError
     */
    public static createDashboard(
        requestBody: DashboardCreate,
    ): CancelablePromise<DashboardMetadata> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/dashboards',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Invalid YAML`,
            },
        });
    }
    /**
     * Validate dashboard YAML
     * @param requestBody
     * @returns ValidationResult Validation result
     * @throws ApiError
     */
    public static validateDashboard(
        requestBody: DashboardYAML,
    ): CancelablePromise<ValidationResult> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/dashboards/validate',
            body: requestBody,
            mediaType: 'text/plain',
        });
    }
    /**
     * Compile dashboard to execution plan
     * @param requestBody
     * @returns ExecutionPlan Execution plan
     * @throws ApiError
     */
    public static compileDashboard(
        requestBody: DashboardYAML,
    ): CancelablePromise<ExecutionPlan> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/dashboards/compile',
            body: requestBody,
            mediaType: 'text/plain',
        });
    }
    /**
     * Get dashboard
     * @param slug
     * @param version
     * @returns DashboardMetadata Dashboard details
     * @throws ApiError
     */
    public static getDashboard(
        slug: string,
        version?: number,
    ): CancelablePromise<DashboardMetadata> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dashboards/{slug}',
            path: {
                'slug': slug,
            },
            query: {
                'version': version,
            },
            errors: {
                404: `Dashboard not found`,
            },
        });
    }
    /**
     * Update dashboard
     * @param slug
     * @param requestBody
     * @returns DashboardMetadata Dashboard updated
     * @throws ApiError
     */
    public static updateDashboard(
        slug: string,
        requestBody: DashboardUpdate,
    ): CancelablePromise<DashboardMetadata> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/dashboards/{slug}',
            path: {
                'slug': slug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Delete dashboard
     * @param slug
     * @returns void
     * @throws ApiError
     */
    public static deleteDashboard(
        slug: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/dashboards/{slug}',
            path: {
                'slug': slug,
            },
        });
    }
}

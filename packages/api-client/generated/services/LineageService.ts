/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LineageGraph } from '../models/LineageGraph';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class LineageService {
    /**
     * Get dashboard lineage
     * @param slug
     * @returns LineageGraph Lineage graph
     * @throws ApiError
     */
    public static getDashboardLineage(
        slug: string,
    ): CancelablePromise<LineageGraph> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dashboards/{slug}/lineage',
            path: {
                'slug': slug,
            },
        });
    }
}

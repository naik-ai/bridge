/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SQLRunRequest } from '../models/SQLRunRequest';
import type { VerificationPayload } from '../models/VerificationPayload';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SqlService {
    /**
     * Execute SQL for verification
     * @param requestBody
     * @returns VerificationPayload Query results with metadata
     * @throws ApiError
     */
    public static runSql(
        requestBody: SQLRunRequest,
    ): CancelablePromise<VerificationPayload> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/sql/run',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Invalid SQL or exceeded byte limit`,
            },
        });
    }
    /**
     * Validate SQL syntax
     * @param requestBody
     * @returns any SQL is valid
     * @throws ApiError
     */
    public static validateSql(
        requestBody: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/sql/validate',
            body: requestBody,
            mediaType: 'text/plain',
            errors: {
                400: `SQL syntax error`,
            },
        });
    }
}

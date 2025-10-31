/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserInfo } from '../models/UserInfo';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthService {
    /**
     * Initiate OAuth login
     * @returns void
     * @throws ApiError
     */
    public static initiateLogin(): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/auth/login',
            errors: {
                302: `Redirect to Google OAuth`,
                500: `OAuth configuration error`,
            },
        });
    }
    /**
     * OAuth callback
     * @param code
     * @param state
     * @returns void
     * @throws ApiError
     */
    public static handleCallback(
        code: string,
        state?: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/auth/callback',
            query: {
                'code': code,
                'state': state,
            },
            errors: {
                302: `Redirect to app with session cookie`,
                401: `Authentication failed`,
            },
        });
    }
    /**
     * Logout
     * @returns any Logged out successfully
     * @throws ApiError
     */
    public static logout(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/logout',
            errors: {
                401: `Not authenticated`,
            },
        });
    }
    /**
     * Get current user
     * @returns UserInfo User information
     * @throws ApiError
     */
    public static getCurrentUser(): CancelablePromise<UserInfo> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/auth/me',
            errors: {
                401: `Not authenticated`,
            },
        });
    }
}

/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ValidationResult = {
    valid: boolean;
    errors?: Array<{
        line?: number;
        column?: number;
        message?: string;
        severity?: 'error' | 'warning';
    }>;
};


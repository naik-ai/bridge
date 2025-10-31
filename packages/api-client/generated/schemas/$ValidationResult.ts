/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $ValidationResult = {
    properties: {
        valid: {
            type: 'boolean',
            isRequired: true,
        },
        errors: {
            type: 'array',
            contains: {
                properties: {
                    line: {
                        type: 'number',
                    },
                    column: {
                        type: 'number',
                    },
                    message: {
                        type: 'string',
                    },
                    severity: {
                        type: 'Enum',
                    },
                },
            },
        },
    },
} as const;

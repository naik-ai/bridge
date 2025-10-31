/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ExecutionPlan = {
    queries: Array<{
        query_id?: string;
        sql?: string;
        depends_on?: Array<string>;
    }>;
    lineage_seeds: Array<{
        query_id?: string;
        tables?: Array<string>;
    }>;
};


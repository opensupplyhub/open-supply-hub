import env from '../util/env';

const cache = {
    version: null,
    taxonomy: null,
    promise: null,
};

export function isIsic4TaxonomyFeatureEnabled() {
    const value = env('ISIC4_TAXONOMY_ENABLED');
    return value === true || value === 'true';
}

function getTaxonomyVersion() {
    const version = env('ISIC4_TAXONOMY_VERSION');
    if (version == null || version === '') {
        return 'unknown';
    }
    return String(version);
}

function getTaxonomyUrl() {
    const url = env('ISIC4_TAXONOMY_URL');
    return url || '/api/taxonomy/isic4/';
}

async function fetchTaxonomyFromApi(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to load ISIC taxonomy (${response.status})`);
    }

    const taxonomy = await response.json();
    if (!taxonomy?.sections) {
        throw new Error('ISIC taxonomy response did not include sections');
    }

    return taxonomy;
}

async function resolveTaxonomy() {
    return fetchTaxonomyFromApi(getTaxonomyUrl());
}

export async function loadIsic4Taxonomy() {
    if (!isIsic4TaxonomyFeatureEnabled()) {
        return null;
    }

    const version = getTaxonomyVersion();

    if (cache.taxonomy && cache.version === version) {
        return cache.taxonomy;
    }

    if (cache.promise && cache.version === version) {
        return cache.promise;
    }

    cache.version = version;
    cache.taxonomy = null;
    cache.promise = resolveTaxonomy()
        .then(taxonomy => {
            cache.taxonomy = taxonomy;
            cache.promise = null;
            return taxonomy;
        })
        .catch(error => {
            cache.promise = null;
            throw error;
        });

    return cache.promise;
}

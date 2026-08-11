import env from '../util/env';
import { ISIC_REV4_TAXONOMY } from './isicRev4Taxonomy';

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
        return 'bundled';
    }
    return String(version);
}

function getBundleUrl() {
    const url = env('ISIC4_TAXONOMY_BUNDLE_URL');
    return url || null;
}

function rewriteBundleUrlForLocal(url) {
    if (env('ENVIRONMENT') === 'local') {
        return url.replace('minio', 'localhost');
    }
    return url;
}

async function importBundleModule(url) {
    const module = await import(/* @vite-ignore */ url);
    if (!module?.ISIC_REV4_TAXONOMY) {
        throw new Error('ISIC taxonomy bundle did not export ISIC_REV4_TAXONOMY');
    }
    return module.ISIC_REV4_TAXONOMY;
}

async function importBundleFromUrl(url) {
    const rewrittenUrl = rewriteBundleUrlForLocal(url);

    try {
        return await importBundleModule(rewrittenUrl);
    } catch (directImportError) {
        const response = await fetch(rewrittenUrl);
        if (!response.ok) {
            throw directImportError;
        }

        const scriptText = await response.text();
        const blob = new Blob([scriptText], { type: 'application/javascript' });
        const blobUrl = URL.createObjectURL(blob);

        try {
            return await importBundleModule(blobUrl);
        } finally {
            URL.revokeObjectURL(blobUrl);
        }
    }
}

async function resolveTaxonomy() {
    const bundleUrl = getBundleUrl();

    if (bundleUrl) {
        return importBundleFromUrl(bundleUrl);
    }

    return ISIC_REV4_TAXONOMY;
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

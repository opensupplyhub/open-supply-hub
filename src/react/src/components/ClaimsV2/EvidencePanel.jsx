import React, { useEffect, useRef, useState } from 'react';
import Typography from '@material-ui/core/Typography';
import isURL from 'validator/lib/isURL';

import {
    getEvidenceText,
    isPdfFile,
    matchesEvidenceKey,
} from './automatedReviewUtils';
import styles from './styles';

/*
 * Evidence strip + viewer (OSDEV-3356 workbench, SPEC.md §5b): the
 * viewer auto-opens the first document on claim load/navigation
 * (mount this with key={claimID}), ✕ closes it, clicking another
 * attachment swaps. Images render inline; PDFs open the original in a
 * new tab while the viewer shows the pipeline's extracted text. The
 * translation/original tabs apply to both kinds and degrade to a
 * check-the-original hint when the automation data is absent.
 */

const TABS = Object.freeze({
    DOCUMENT: 'document',
    TRANSLATED: 'translated',
    ORIGINAL: 'original',
});

/*
 * Images render inline (§5b), so the image is an image doc's default
 * view; a PDF's inline view is its extracted text (the original lives
 * in the new tab), so text is the default there. A URL's inline view is
 * the page text the pipeline fetched — the page itself opens in a new
 * tab, like a PDF's original.
 */
const defaultTabFor = doc =>
    doc && (doc.is_url || isPdfFile(doc.file_name))
        ? TABS.TRANSLATED
        : TABS.DOCUMENT;

/*
 * Links submitted as claim evidence, as pseudo-documents for the strip.
 * The claim stores them across four fields (two claim-flow generations);
 * the pipeline normalizes a scheme-less value with an https:// prefix
 * and dedupes before fetching, and the note block keys the page text by
 * that normalized URL — so build the names identically here or the
 * viewer's text lookup misses. The legacy `website` field is free text
 * ("N/A", "none", two addresses in one), so only values that are a URL
 * after normalization become chips — anything else is neither linkable
 * nor evidence.
 */
const URL_EVIDENCE_FIELDS = [
    ['facility_website', 'Production location website'],
    ['linkedin_profile', 'LinkedIn'],
    ['claimant_linkedin_profile_url', 'Claimant LinkedIn'],
    ['website', 'Business website'],
];

export const buildUrlEvidence = detail => {
    const seen = new Set();
    const urlDocs = [];
    URL_EVIDENCE_FIELDS.forEach(([field, label]) => {
        const raw = detail?.[field];
        if (typeof raw !== 'string' || raw.trim() === '') {
            return;
        }
        let url = raw.trim();
        if (!url.startsWith('http')) {
            url = `https://${url}`;
        }
        if (!isURL(url, { require_protocol: true })) {
            return;
        }
        if (!seen.has(url)) {
            seen.add(url);
            urlDocs.push({ file_name: url, label, is_url: true });
        }
    });
    return urlDocs;
};

/*
 * Attachment URL, compatible with both sides of OSDEV-2278 (PR #1274):
 * today the serializer carries a presigned claim_attachment URL; after
 * that PR merges it carries only the attachment id, and files are
 * fetched through the authorization-checked download action (a 302 to
 * a short-lived presigned URL), which works directly as an <img src>
 * or window.open target because the browser follows the redirect with
 * the session cookie.
 */
const attachmentHref = (claimID, doc) => {
    if (doc.is_url) {
        return doc.file_name;
    }
    if (doc.claim_attachment) {
        return doc.claim_attachment;
    }
    // The download endpoint needs the attachment id, which the API only
    // sends once OSDEV-2278 lands — without it there is no valid URL.
    return doc.id != null
        ? `/api/facility-claims/${claimID}/attachments/${doc.id}/download/`
        : null;
};

export default function EvidencePanel({
    attachments,
    urlEvidence,
    review,
    matchValues,
    claimID,
    requestedDoc,
}) {
    const docs = (Array.isArray(attachments) ? attachments : []).concat(
        Array.isArray(urlEvidence) ? urlEvidence : [],
    );
    // Spec §5b: the first document auto-opens on claim load.
    const [openIndex, setOpenIndex] = useState(docs.length > 0 ? 0 : null);
    const [tab, setTab] = useState(defaultTabFor(docs[0]));

    const openDoc = openIndex === null ? null : docs[openIndex];
    const evidenceText = openDoc
        ? getEvidenceText(review, openDoc.file_name)
        : null;

    /*
     * A PDF's original opens in a new tab (the viewer itself only
     * shows extracted text). Auto-opening the first document must NOT
     * do this — only a click does, or J/K navigation would spawn a tab
     * per claim.
     */
    const selectDoc = index => {
        setOpenIndex(index);
        setTab(defaultTabFor(docs[index]));
        const doc = docs[index];
        const href = doc && attachmentHref(claimID, doc);
        if (doc && (doc.is_url || isPdfFile(doc.file_name)) && href) {
            window.open(href, '_blank', 'noopener');
        }
    };

    /* Only a request issued after this mount may open a document —
       initializing to the current seq means a remount (navigation,
       refetch) never replays the previous request, which for a PDF
       would spawn an unrequested tab. */
    const handledSeq = useRef(requestedDoc?.seq || 0);

    /* Reset the auto-open when the attachments list itself changes
       (e.g. a refetch after an action added documents). */
    useEffect(() => {
        setOpenIndex(docs.length > 0 ? 0 : null);
        setTab(defaultTabFor(docs[0]));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [docs.length]);

    /* A verification row's source link requested a document: open it
       (same semantics as clicking its chip, so a PDF's original still
       opens in a new tab). `seq` distinguishes repeated requests for
       the same file. Legacy blocks name the source by the derived
       artifact ("badge.json" for badge.pdf), so match like the text
       lookup does. */
    useEffect(() => {
        if (!requestedDoc?.name || requestedDoc.seq === handledSeq.current) {
            return;
        }
        handledSeq.current = requestedDoc.seq;
        const index = docs.findIndex(doc =>
            matchesEvidenceKey(doc.file_name, requestedDoc.name),
        );
        if (index !== -1) {
            selectDoc(index);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [requestedDoc?.seq]);

    const renderViewerBody = () => {
        if (!openDoc) {
            return null;
        }
        if (tab === TABS.TRANSLATED || tab === TABS.ORIGINAL) {
            const text =
                tab === TABS.TRANSLATED
                    ? evidenceText?.translated
                    : evidenceText?.original;
            if (text) {
                return <pre style={styles.evidenceText}>{text}</pre>;
            }
        }
        const openHref = attachmentHref(claimID, openDoc);
        if (
            tab === TABS.DOCUMENT &&
            !openDoc.is_url &&
            !isPdfFile(openDoc.file_name) &&
            openHref
        ) {
            return (
                <div>
                    <img
                        src={openHref}
                        alt={openDoc.file_name}
                        style={styles.evidenceImage}
                    />
                    <div style={styles.viewerCaption}>
                        Original document — as uploaded by the claimant.
                    </div>
                </div>
            );
        }
        /* eslint-disable no-nested-ternary */
        const hint = openDoc.is_url
            ? tab === TABS.DOCUMENT
                ? 'Web link — the page opens in a new tab: '
                : 'No page text recorded for this link — '
            : tab === TABS.DOCUMENT
            ? 'PDF — the original opens in a new tab: '
            : 'No extracted text for this document — ';
        /* eslint-enable no-nested-ternary */
        return (
            <Typography variant="body1" style={styles.evidenceHint}>
                {hint}
                {openHref ? (
                    <a
                        href={openHref}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {openDoc.is_url
                            ? 'open the link ↗'
                            : 'open the original ↗'}
                    </a>
                ) : (
                    'original unavailable until the download endpoint ships'
                )}
            </Typography>
        );
    };

    return (
        <section style={styles.evidenceHalf} aria-label="Evidence">
            <div style={styles.sectionLabel}>Evidence ({docs.length})</div>
            <div style={styles.evidenceStrip}>
                {docs.map((doc, index) => (
                    <button
                        type="button"
                        key={doc.file_name + String(index)}
                        style={{
                            ...styles.evidenceChip,
                            ...(index === openIndex
                                ? styles.evidenceChipOpen
                                : {}),
                        }}
                        onClick={() => selectDoc(index)}
                        title={doc.is_url ? doc.file_name : undefined}
                    >
                        {/* eslint-disable-next-line no-nested-ternary */}
                        {doc.is_url
                            ? '🔗 '
                            : isPdfFile(doc.file_name)
                            ? '📄 '
                            : '🖼 '}
                        {doc.is_url
                            ? `${doc.label}: ${doc.file_name.replace(
                                  /^https?:\/\/(www\.)?/,
                                  '',
                              )}`
                            : doc.file_name}
                    </button>
                ))}
                {docs.length === 0 && (
                    <Typography variant="body1" style={styles.evidenceHint}>
                        No documents attached to this claim.
                    </Typography>
                )}
            </div>
            {openDoc && (
                <div style={styles.evidenceViewer}>
                    <div style={styles.evidenceViewerBar}>
                        <span style={styles.evidenceViewerName}>
                            {openDoc.file_name}
                            {evidenceText?.lang
                                ? ` · detected language: ${evidenceText.lang}`
                                : ''}
                        </span>
                        <span>
                            <button
                                type="button"
                                style={{
                                    ...styles.evidenceTab,
                                    ...(tab === TABS.DOCUMENT
                                        ? styles.evidenceTabActive
                                        : {}),
                                }}
                                onClick={() => setTab(TABS.DOCUMENT)}
                            >
                                {openDoc.is_url ? 'Link' : 'Document'}
                            </button>
                            <button
                                type="button"
                                style={{
                                    ...styles.evidenceTab,
                                    ...(tab === TABS.TRANSLATED
                                        ? styles.evidenceTabActive
                                        : {}),
                                }}
                                onClick={() => setTab(TABS.TRANSLATED)}
                            >
                                {openDoc.is_url
                                    ? 'Page text (English)'
                                    : 'English translation'}
                            </button>
                            <button
                                type="button"
                                style={{
                                    ...styles.evidenceTab,
                                    ...(tab === TABS.ORIGINAL
                                        ? styles.evidenceTabActive
                                        : {}),
                                }}
                                onClick={() => setTab(TABS.ORIGINAL)}
                            >
                                Original text
                            </button>
                            <button
                                type="button"
                                aria-label="Close viewer"
                                style={styles.evidenceClose}
                                onClick={() => setOpenIndex(null)}
                            >
                                ✕
                            </button>
                        </span>
                    </div>
                    {renderViewerBody()}
                    {/* The values this document must corroborate — the
                        match-box sits below the viewer so the document
                        itself gets the full width. */}
                    {Array.isArray(matchValues) && matchValues.length > 0 && (
                        <div style={styles.matchBox}>
                            <div style={styles.matchTitle}>
                                Match against OS Hub profile
                            </div>
                            <div style={styles.matchGrid}>
                                {matchValues.map(([key, value]) => (
                                    <div key={key} style={styles.matchRow}>
                                        <span style={styles.matchKey}>
                                            {key}
                                        </span>
                                        <span style={styles.matchValue}>
                                            {value || '—'}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </section>
    );
}

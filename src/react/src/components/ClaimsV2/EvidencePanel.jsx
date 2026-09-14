import React, { useEffect, useState } from 'react';
import Typography from '@material-ui/core/Typography';

import { getEvidenceText, isPdfFile } from './automatedReviewUtils';
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
 * in the new tab), so text is the default there.
 */
const defaultTabFor = doc =>
    doc && isPdfFile(doc.file_name) ? TABS.TRANSLATED : TABS.DOCUMENT;

export default function EvidencePanel({ attachments, review, matchValues }) {
    const docs = Array.isArray(attachments) ? attachments : [];
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
        if (doc && isPdfFile(doc.file_name)) {
            window.open(doc.claim_attachment, '_blank', 'noopener');
        }
    };

    /* Reset the auto-open when the attachments list itself changes
       (e.g. a refetch after an action added documents). */
    useEffect(() => {
        setOpenIndex(docs.length > 0 ? 0 : null);
        setTab(defaultTabFor(docs[0]));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [docs.length]);

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
        if (tab === TABS.DOCUMENT && !isPdfFile(openDoc.file_name)) {
            return (
                <div>
                    <img
                        src={openDoc.claim_attachment}
                        alt={openDoc.file_name}
                        style={styles.evidenceImage}
                    />
                    <div style={styles.viewerCaption}>
                        Original document — as uploaded by the claimant.
                    </div>
                </div>
            );
        }
        return (
            <Typography variant="body1" style={styles.evidenceHint}>
                {tab === TABS.DOCUMENT
                    ? 'PDF — the original opens in a new tab: '
                    : 'No extracted text for this document — '}
                <a
                    href={openDoc.claim_attachment}
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    open the original ↗
                </a>
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
                    >
                        {isPdfFile(doc.file_name) ? '📄 ' : '🖼 '}
                        {doc.file_name}
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
                                Document
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
                                English translation
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
                    {/* The values this document must corroborate,
                        pinned beside the evidence (prototype's
                        match-box). */}
                    <div style={styles.viewerBody}>
                        <div style={styles.viewerContent}>
                            {renderViewerBody()}
                        </div>
                        {Array.isArray(matchValues) && matchValues.length > 0 && (
                            <div style={styles.matchBox}>
                                <div style={styles.matchTitle}>
                                    Match against OS Hub profile
                                </div>
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
                        )}
                    </div>
                </div>
            )}
        </section>
    );
}

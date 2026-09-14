import React, { useState } from 'react';
import Typography from '@material-ui/core/Typography';
import { toast } from 'react-toastify';

import { MESSAGE_TEMPLATES, composeMessage } from './templates';
import { getSuggestedDraft } from './automatedReviewUtils';
import styles from './styles';

/*
 * Message composer (OSDEV-3356 workbench, SPEC.md §5b): template chips
 * + the ★ suggested draft from the automated review, both prefilling
 * an editable textarea; send posts via the message-claimant action and
 * the sent message lands in the timeline labeled "Emailed to
 * claimant". Template selection recomposes the draft (with the
 * sensitive-notice dedupe in composeMessage) until the moderator edits
 * by hand — after that, chips are inert until the draft is cleared, so
 * a click never destroys manual work.
 */

export default function MessageComposer({
    detail,
    review,
    messageClaimant,
    acting,
    onSent,
}) {
    const [message, setMessage] = useState('');
    const [selectedTemplates, setSelectedTemplates] = useState([]);
    const [edited, setEdited] = useState(false);

    const suggestedDraft = getSuggestedDraft(review);
    const templateContext = {
        facilityName: detail.facility?.properties?.name || 'your facility',
        jobTitle: detail.job_title || 'your stated title',
        emailDomain: (detail.email || '').split('@')[1] || 'your email domain',
        facilityAddress: detail.facility?.properties?.address || '',
        osID: detail.os_id || detail.facility?.id || '',
    };

    const chipsLocked = edited && message.trim() !== '';

    const toggleTemplate = key => {
        if (chipsLocked) {
            return;
        }
        const next = selectedTemplates.includes(key)
            ? selectedTemplates.filter(k => k !== key)
            : [...selectedTemplates, key];
        setSelectedTemplates(next);
        setMessage(composeMessage(next, templateContext));
        setEdited(false);
    };

    const applySuggestedDraft = () => {
        if (chipsLocked) {
            return;
        }
        setSelectedTemplates([]);
        setMessage(suggestedDraft || '');
        setEdited(false);
    };

    const clearDraft = () => {
        setMessage('');
        setSelectedTemplates([]);
        setEdited(false);
    };

    const send = () => {
        messageClaimant(message.trim())
            .then(() => {
                toast('Message sent to the claimant');
                clearDraft();
                onSent();
            })
            .catch(() => {});
    };

    return (
        <section style={styles.composerHalf} aria-label="Message claimant">
            <Typography variant="subheading">Message claimant</Typography>
            <div style={styles.templateChips}>
                {Object.entries(MESSAGE_TEMPLATES).map(([key, template]) => (
                    <button
                        type="button"
                        key={key}
                        disabled={chipsLocked}
                        style={{
                            ...styles.templateChip,
                            ...(selectedTemplates.includes(key)
                                ? styles.templateChipSelected
                                : {}),
                            ...(chipsLocked ? styles.templateChipLocked : {}),
                        }}
                        onClick={() => toggleTemplate(key)}
                    >
                        {template.label}
                    </button>
                ))}
                {suggestedDraft && (
                    <button
                        type="button"
                        disabled={chipsLocked}
                        style={{
                            ...styles.templateChip,
                            ...styles.suggestedDraftChip,
                            ...(chipsLocked ? styles.templateChipLocked : {}),
                        }}
                        onClick={applySuggestedDraft}
                        title="Prefill the automated review's draft reply"
                    >
                        ★ Suggested draft
                    </button>
                )}
            </div>
            {chipsLocked && (
                <Typography variant="caption" style={styles.evidenceHint}>
                    Draft edited by hand — clear it to use templates again.
                </Typography>
            )}
            <textarea
                value={message}
                aria-label="Message to the claimant"
                placeholder="Write to the claimant, or start from a template…"
                style={styles.composerTextarea}
                onChange={event => {
                    setMessage(event.target.value);
                    setEdited(true);
                }}
            />
            <div style={styles.composerActions}>
                <button
                    type="button"
                    style={styles.composerClear}
                    onClick={clearDraft}
                    disabled={message === ''}
                >
                    Clear
                </button>
                <button
                    type="button"
                    style={styles.composerSend}
                    onClick={send}
                    disabled={acting || message.trim() === ''}
                >
                    {acting ? 'Sending…' : 'Send to claimant'}
                </button>
            </div>
        </section>
    );
}

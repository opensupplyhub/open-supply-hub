import React, { useState } from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import { toast } from 'react-toastify';

import { makeClaimTrackerTicketSearchURL } from './jiraUtils';
import styles from './styles';

/*
 * Decision rail (OSDEV-3356, SPEC.md §5b right column + §5c):
 * approve/deny with confirmation dialogs, the stage rationale, and the
 * Jira assignment box.
 *
 * §5c: the deny reason is STORED AS status_change_reason AND EMAILED
 * TO THE CLAIMANT VERBATIM — the dialog says so prominently and the
 * reason is required. The optional "Internal note" field (spec's
 * provisional option) posts separately through the /note/ endpoint as
 * INTERNAL so candid rationale never reaches the claimant. Approve
 * reasons are never emailed.
 */

const DIALOGS = Object.freeze({
    APPROVE: 'approve',
    DENY: 'deny',
});

export default function DecisionPanel({
    detail,
    stage,
    acting,
    actionError,
    approveClaim,
    denyClaim,
    addNote,
    onDecided,
}) {
    const [openDialog, setOpenDialog] = useState(null);
    const [reason, setReason] = useState('');
    const [internalNote, setInternalNote] = useState('');

    const close = () => {
        setOpenDialog(null);
        setReason('');
        setInternalNote('');
    };

    /*
     * The decision and the optional internal note are separate posts
     * with different failure meanings. A failed DECISION keeps the
     * dialog open with the error visible so the moderator can retry —
     * nothing was decided. A failed NOTE after a successful decision
     * must NOT invite a retry: the claim is already decided, so
     * re-submitting would re-post the decision. The dialog closes, the
     * queue refreshes, and a toast tells the moderator to re-add the
     * note from the Activity box.
     */
    const decide = () => {
        const action =
            openDialog === DIALOGS.APPROVE ? approveClaim : denyClaim;
        const verb = openDialog === DIALOGS.APPROVE ? 'approved' : 'denied';
        const note = internalNote.trim();
        action(reason.trim())
            .then(() => {
                const finish = () => {
                    close();
                    onDecided();
                };
                if (note === '') {
                    toast(`Claim #${detail.id} ${verb}`);
                    finish();
                    return;
                }
                addNote(note)
                    .then(() => {
                        toast(`Claim #${detail.id} ${verb}`);
                        finish();
                    })
                    .catch(() => {
                        toast(
                            `Claim #${detail.id} ${verb} — but the ` +
                                'internal note failed to save. Re-add it ' +
                                'from the Activity box.',
                        );
                        finish();
                    });
            })
            .catch(() => {
                // actionError renders inside the dialog; nothing was
                // decided, so retrying is safe.
            });
    };

    const denyBlocked = openDialog === DIALOGS.DENY && reason.trim() === '';

    return (
        <aside style={styles.decisionRail} aria-label="Decision">
            <div style={styles.sectionLabel}>Decision</div>
            <div style={styles.decisionButtons}>
                <button
                    type="button"
                    style={styles.approveButton}
                    onClick={() => setOpenDialog(DIALOGS.APPROVE)}
                    disabled={acting}
                >
                    Approve claim
                    <span style={styles.decisionButtonSub}>
                        Grants the claimant control of this profile
                    </span>
                </button>
                <button
                    type="button"
                    style={styles.denyButton}
                    onClick={() => setOpenDialog(DIALOGS.DENY)}
                    disabled={acting}
                >
                    Deny claim…
                    <span style={styles.decisionButtonSub}>
                        Requires a reason — emailed to claimant &amp; logged
                    </span>
                </button>
            </div>
            <div style={styles.stageBox}>
                <strong>Stage rationale</strong>
                <div style={styles.noteMeta}>{stage.reason}</div>
            </div>
            <div style={styles.jiraBox}>
                <strong>Assignment</strong>
                <div>
                    <a
                        href={makeClaimTrackerTicketSearchURL(detail.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Managed in Jira — open this claim&apos;s ticket ↗
                    </a>
                </div>
            </div>

            <Dialog open={openDialog !== null} onClose={close} fullWidth>
                <DialogTitle>
                    {openDialog === DIALOGS.APPROVE
                        ? `Approve claim #${detail.id}`
                        : `Deny claim #${detail.id}`}
                </DialogTitle>
                <DialogContent>
                    {openDialog === DIALOGS.DENY ? (
                        <Typography
                            variant="body1"
                            style={styles.claimantFacingWarning}
                        >
                            ⚠ The reason below is emailed to the claimant
                            verbatim as the explanation for the denial. Write it
                            to them, not about them.
                        </Typography>
                    ) : (
                        <Typography variant="body1" style={styles.noteMeta}>
                            Approve reasons are recorded on the claim and are
                            never emailed to the claimant.
                        </Typography>
                    )}
                    <textarea
                        value={reason}
                        aria-label={
                            openDialog === DIALOGS.DENY
                                ? 'Reason (emailed to the claimant)'
                                : 'Reason (internal record)'
                        }
                        placeholder={
                            openDialog === DIALOGS.DENY
                                ? 'Reason — emailed to the claimant (required)'
                                : 'Reason (optional)'
                        }
                        style={styles.dialogTextarea}
                        onChange={event => setReason(event.target.value)}
                    />
                    {actionError && (
                        <Typography
                            variant="body1"
                            style={styles.claimantFacingWarning}
                        >
                            {actionError} Nothing was decided — you can retry.
                        </Typography>
                    )}
                    {openDialog === DIALOGS.DENY && (
                        <textarea
                            value={internalNote}
                            aria-label="Internal note, moderators only"
                            placeholder={
                                '🔒 Internal note (moderators only, never ' +
                                'sent) — optional'
                            }
                            style={styles.dialogTextareaSmall}
                            onChange={event =>
                                setInternalNote(event.target.value)
                            }
                        />
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={close}>Cancel</Button>
                    <Button
                        color="primary"
                        variant="contained"
                        onClick={decide}
                        disabled={acting || denyBlocked}
                    >
                        {openDialog === DIALOGS.APPROVE
                            ? 'Approve'
                            : 'Deny and email reason'}
                    </Button>
                </DialogActions>
            </Dialog>
        </aside>
    );
}

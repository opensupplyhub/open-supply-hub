import React, { useState } from 'react';
import { toast } from 'react-toastify';

import styles from './styles';

/*
 * Internal note box (OSDEV-3356, SPEC.md §5b): lives inside the
 * Activity section, 🔒 deliberately separate from the claimant
 * composer — notes posted here go through the /note/ endpoint as
 * INTERNAL and are never emailed.
 */

export default function InternalNoteBox({ addNote, acting, onAdded }) {
    const [note, setNote] = useState('');

    const submit = () => {
        addNote(note.trim())
            .then(() => {
                toast('Internal note added');
                setNote('');
                onAdded();
            })
            .catch(() => {});
    };

    return (
        <div style={styles.internalNoteBox}>
            <textarea
                value={note}
                aria-label="Internal note, moderators only"
                placeholder={
                    '🔒 Internal note — visible to moderators only, ' +
                    'never sent to the claimant'
                }
                style={styles.internalNoteTextarea}
                onChange={event => setNote(event.target.value)}
            />
            <div style={styles.composerActions}>
                <button
                    type="button"
                    style={styles.composerClear}
                    onClick={submit}
                    disabled={acting || note.trim() === ''}
                >
                    🔒 Add internal note
                </button>
            </div>
        </div>
    );
}

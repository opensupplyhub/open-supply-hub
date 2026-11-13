import React, { useCallback, useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import { arrayOf, func, shape, string } from 'prop-types';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import COLOURS from '../util/COLOURS';

/*
 * A short walkthrough of the review step: four callouts, each pointing at
 * one part of the page, in the order a contributor would use them. Steps
 * find their target by a `data-tour` attribute, so a step whose target is
 * not on the page (a list with nothing fixed automatically, say) is simply
 * skipped.
 *
 * The dialog opens it the first time a user reaches the review; closing
 * it is recorded against the user, so later reviews start without it and
 * "Show me around" in the header brings it back. `onDone` says how it was
 * closed: 'skipped', 'finished' or 'escaped'.
 */
export const REVIEW_TOUR_STEPS = Object.freeze([
    Object.freeze({
        anchor: 'intro',
        scroll: 'nearest',
        title: 'Where you are in the upload',
        text:
            'Your review is one step of the upload: after you submit, a ' +
            'human moderator still checks the list before it goes live. ' +
            'This bar counts the rows that still need your review. It fills as ' +
            'you work through them, and the next steps show how to make ' +
            'those decisions here, with no need to re-upload.',
    }),
    Object.freeze({
        anchor: 'automatic',
        title: 'Automatic fixes',
        text:
            'Formatting issues that needed no input from you, like country ' +
            'codes and worker counts, were fixed automatically and go on ' +
            'when you submit. View automatic fixes shows each type, and ' +
            'you can undo one if we got it wrong.',
    }),
    Object.freeze({
        anchor: 'chips',
        title: 'Required fixes first, then recommended',
        text:
            'The same mistake usually repeats through a file, so rows are ' +
            'grouped by type. Required fixes come first: they must be made ' +
            'before your list can be approved, such as personal ' +
            'information or a PO Box. Recommended fixes improve your data ' +
            'but will not stop approval. Pick a chip to see why it matters ' +
            'and just those rows.',
    }),
    Object.freeze({
        anchor: 'rows',
        title: 'Decide by type or row by row',
        text:
            'Accept or keep every recommended fix at once, or pick a type ' +
            'to accept, keep or remove all of its rows in one go. Rows ' +
            'you fix or remove one by one keep your decision.',
    }),
    Object.freeze({
        anchor: 'apply',
        title: 'Apply and submit when you are done',
        text:
            'One click applies every decision you made here and submits ' +
            'the list, and you can download the current list first. This ' +
            'is the one submission: after it, or once the hour is up, ' +
            'nothing changes and a human moderator takes over.',
    }),
]);

const Z_INDEX = 1400; // above the full-screen dialog (1300)
const PAD = 6;
const GAP = 18;
const CALLOUT_WIDTH = 320;
const CALLOUT_HEIGHT = 200; // estimate used only to pick above or below
const ARROW = 14;

const styles = Object.freeze({
    spotlight: Object.freeze({
        position: 'fixed',
        zIndex: Z_INDEX,
        border: `3px solid ${COLOURS.LIGHT_BLUE}`,
        borderRadius: '8px',
        boxShadow: '0 0 0 9999px rgba(4, 39, 164, 0.3)',
        pointerEvents: 'none',
        transition: 'top .25s, left .25s, width .25s, height .25s',
    }),
    callout: Object.freeze({
        position: 'fixed',
        zIndex: Z_INDEX + 1,
        width: `${CALLOUT_WIDTH}px`,
        maxWidth: 'calc(100vw - 32px)',
        padding: '16px 18px 12px 18px',
        borderRadius: '8px',
        background: COLOURS.WHITE,
        boxShadow: '0 8px 28px rgba(0, 0, 0, 0.35)',
        transition: 'top .25s, left .25s',
    }),
    arrow: Object.freeze({
        position: 'absolute',
        width: `${ARROW}px`,
        height: `${ARROW}px`,
        background: COLOURS.WHITE,
        transform: 'rotate(45deg)',
    }),
    counter: Object.freeze({
        display: 'inline-block',
        padding: '2px 10px',
        borderRadius: '12px',
        background: COLOURS.LIGHT_BLUE,
        color: COLOURS.WHITE,
        fontSize: '0.75rem',
        fontWeight: 700,
        letterSpacing: '0.04em',
        marginBottom: '8px',
    }),
    title: Object.freeze({
        fontSize: '1.05rem',
        fontWeight: 700,
        marginBottom: '6px',
    }),
    text: Object.freeze({
        fontSize: '0.9rem',
        lineHeight: 1.45,
    }),
    buttons: Object.freeze({
        display: 'flex',
        justifyContent: 'flex-end',
        alignItems: 'center',
        gap: '4px',
        marginTop: '12px',
    }),
    skip: Object.freeze({
        marginRight: 'auto',
        color: 'rgba(0, 0, 0, 0.6)',
    }),
});

const findTarget = anchor => document.querySelector(`[data-tour="${anchor}"]`);

const measure = el => {
    const r = el.getBoundingClientRect();
    return { top: r.top, left: r.left, width: r.width, height: r.height };
};

const clamp = (n, lo, hi) => Math.min(Math.max(n, lo), hi);

const ListCleaningTour = ({ steps, onDone }) => {
    // Only steps whose target exists on the page, found once the page
    // around this component has been committed.
    const [present, setPresent] = useState(null);
    const [index, setIndex] = useState(0);
    const [rect, setRect] = useState(null);
    useEffect(() => {
        setPresent(steps.filter(s => findTarget(s.anchor)));
    }, [steps]);
    const step = present ? present[index] : null;

    const remeasure = useCallback(() => {
        if (!step) return;
        const el = findTarget(step.anchor);
        setRect(el ? measure(el) : null);
    }, [step]);

    // Bring the target on screen, then follow it through scrolls, resizes
    // and the page re-rendering after a decision.
    useEffect(() => {
        if (!step) return undefined;
        const el = findTarget(step.anchor);
        if (el?.scrollIntoView) {
            el.scrollIntoView({ block: step.scroll || 'center' });
        }
        remeasure();
        window.addEventListener('resize', remeasure);
        window.addEventListener('scroll', remeasure, true);
        const timer = setInterval(remeasure, 400);
        return () => {
            window.removeEventListener('resize', remeasure);
            window.removeEventListener('scroll', remeasure, true);
            clearInterval(timer);
        };
    }, [step, remeasure]);

    useEffect(() => {
        const onKey = e => {
            if (e.key === 'Escape') onDone('escaped');
        };
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    }, [onDone]);

    if (!step || !rect) return null;

    const last = index === present.length - 1;
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const width = Math.min(CALLOUT_WIDTH, vw - 32);
    const below = rect.top + rect.height + GAP + CALLOUT_HEIGHT < vh;
    const left = clamp(rect.left, 16, vw - width - 16);
    // The arrow sits over the target's left edge, a little way in.
    const arrowX = clamp(
        rect.left + Math.min(rect.width / 2, 48) - left - ARROW / 2,
        14,
        width - ARROW - 14,
    );

    const calloutStyle = {
        ...styles.callout,
        left: `${left}px`,
        ...(below
            ? { top: `${rect.top + rect.height + PAD + GAP}px` }
            : { bottom: `${vh - rect.top + PAD + GAP}px` }),
    };
    const arrowStyle = {
        ...styles.arrow,
        left: `${arrowX}px`,
        ...(below ? { top: `${-ARROW / 2}px` } : { bottom: `${-ARROW / 2}px` }),
    };

    return ReactDOM.createPortal(
        <>
            <div
                style={{
                    ...styles.spotlight,
                    top: `${rect.top - PAD}px`,
                    left: `${rect.left - PAD}px`,
                    width: `${rect.width + PAD * 2}px`,
                    height: `${rect.height + PAD * 2}px`,
                }}
            />
            <dialog
                open
                style={calloutStyle}
                aria-label={`Tour step ${index + 1} of ${present.length}`}
            >
                <div style={arrowStyle} />
                <span style={styles.counter}>
                    {index + 1} of {present.length}
                </span>
                <Typography style={styles.title}>{step.title}</Typography>
                <Typography style={styles.text}>{step.text}</Typography>
                <div style={styles.buttons}>
                    {!last && (
                        <Button
                            size="small"
                            style={styles.skip}
                            onClick={() => onDone('skipped')}
                        >
                            Skip tour
                        </Button>
                    )}
                    {index > 0 && (
                        <Button
                            size="small"
                            onClick={() => setIndex(index - 1)}
                        >
                            Back
                        </Button>
                    )}
                    <Button
                        size="small"
                        variant="contained"
                        color="primary"
                        onClick={() =>
                            last ? onDone('finished') : setIndex(index + 1)
                        }
                    >
                        {last ? 'Got it' : 'Next'}
                    </Button>
                </div>
            </dialog>
        </>,
        document.body,
    );
};

ListCleaningTour.defaultProps = {
    steps: REVIEW_TOUR_STEPS,
};

ListCleaningTour.propTypes = {
    steps: arrayOf(
        shape({
            anchor: string.isRequired,
            title: string.isRequired,
            text: string.isRequired,
            scroll: string,
        }),
    ),
    onDone: func.isRequired,
};

export default ListCleaningTour;

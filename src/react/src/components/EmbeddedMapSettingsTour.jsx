import React, { useEffect, useRef } from 'react';
import { arrayOf, func, number, shape, string } from 'prop-types';

const styles = {
    card: {
        margin: '12px 0 4px',
        padding: '14px 16px 12px',
        background: 'rgb(13, 17, 40)',
        color: 'white',
        fontSize: '15px',
        lineHeight: 1.45,
    },
    step: {
        fontSize: '12px',
        fontWeight: 700,
        letterSpacing: '0.06em',
        textTransform: 'uppercase',
        opacity: 0.75,
    },
    title: {
        margin: '2px 0 6px',
        fontSize: '18px',
        fontWeight: 700,
    },
    actions: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginTop: '12px',
    },
    button: {
        padding: '6px 14px',
        border: '1px solid white',
        background: 'none',
        color: 'white',
        fontFamily: 'inherit',
        fontSize: '13px',
        fontWeight: 700,
        cursor: 'pointer',
    },
    primary: {
        background: 'white',
        color: 'rgb(13, 17, 40)',
    },
    skip: {
        marginLeft: 'auto',
        padding: 0,
        border: 0,
        background: 'none',
        color: 'white',
        fontFamily: 'inherit',
        fontSize: '13px',
        textDecoration: 'underline',
        cursor: 'pointer',
    },
};

/*
A short tour of the Embed settings: one card that steps through what each
section is for. The settings screen switches section as the tour moves on,
and marks what the current step is about.
*/
function EmbeddedMapSettingsTour({ steps, stepIndex, onStep, onClose }) {
    const cardRef = useRef(null);
    const step = steps[stepIndex];

    // Keep the card in view as the tour moves between sections.
    useEffect(() => {
        if (cardRef.current && cardRef.current.scrollIntoView) {
            cardRef.current.scrollIntoView({
                block: 'nearest',
                behavior: 'smooth',
            });
        }
    }, [stepIndex]);

    if (!step) return null;
    const isFirst = stepIndex === 0;
    const isLast = stepIndex === steps.length - 1;

    return (
        <div
            ref={cardRef}
            style={styles.card}
            role="dialog"
            aria-label="Tour of the Embed settings"
            data-testid="embed-settings-tour"
        >
            <div style={styles.step}>
                Step {stepIndex + 1} of {steps.length}
            </div>
            <div style={styles.title}>{step.title}</div>
            <div aria-live="polite">{step.body}</div>
            <div style={styles.actions}>
                {isFirst ? null : (
                    <button
                        type="button"
                        style={styles.button}
                        onClick={() => onStep(stepIndex - 1)}
                    >
                        Back
                    </button>
                )}
                <button
                    type="button"
                    style={{ ...styles.button, ...styles.primary }}
                    onClick={() => (isLast ? onClose() : onStep(stepIndex + 1))}
                >
                    {isLast ? 'Done' : 'Next'}
                </button>
                {isLast ? null : (
                    <button type="button" style={styles.skip} onClick={onClose}>
                        Skip the tour
                    </button>
                )}
            </div>
        </div>
    );
}

EmbeddedMapSettingsTour.propTypes = {
    steps: arrayOf(
        shape({ id: string, title: string, body: string, section: string }),
    ).isRequired,
    stepIndex: number.isRequired,
    onStep: func.isRequired,
    onClose: func.isRequired,
};

export default EmbeddedMapSettingsTour;

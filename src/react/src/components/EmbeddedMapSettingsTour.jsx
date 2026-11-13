import React, { useEffect, useRef } from 'react';
import { arrayOf, func, number, shape, string } from 'prop-types';

const styles = {
    card: {
        // Clear of the site's header when the card is scrolled into view.
        scrollMarginTop: '130px',
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
A card that steps through a short tour or tutorial on the Embed settings
screen: the tour of what each section is for, and the tutorial on building
a supply chain. Whatever shows the card moves to, and marks, what the
current step is about.
*/
function EmbeddedMapSettingsTour({
    steps,
    stepIndex,
    onStep,
    onClose,
    label,
    skipLabel,
    testId,
}) {
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
            aria-label={label}
            data-testid={testId}
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
                        {skipLabel}
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
    label: string,
    skipLabel: string,
    testId: string,
};

EmbeddedMapSettingsTour.defaultProps = {
    label: 'Tour of the Embed settings',
    skipLabel: 'Skip the tour',
    testId: 'embed-settings-tour',
};

export default EmbeddedMapSettingsTour;

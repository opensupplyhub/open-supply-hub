import React from 'react';
import { Link } from 'react-router-dom';

import { isOnboardingComplete, onboardingSteps } from './utils';
import { contributeRoute, facilitiesRoute } from '../../util/constants';
import styles from './styles';

const STEP_LINKS = Object.freeze({
    contribute: Object.freeze({ to: contributeRoute, label: 'Contribute' }),
    claim: Object.freeze({
        to: facilitiesRoute,
        label: 'Search production locations',
    }),
});

/*
 * The first steps of a new organization, ticked from what it has
 * already done. Shown until all of them are done, and not at all before
 * the progress is known, so it never flashes for an organization that
 * finished long ago.
 */
const OnboardingChecklist = ({ progress, isAdmin }) => {
    if (!progress) return null;

    const steps = onboardingSteps(progress, isAdmin);
    if (isOnboardingComplete(steps)) return null;

    return (
        <div style={styles.section} data-testid="organization-onboarding">
            <h3 style={styles.sectionTitle}>Getting started</h3>
            <p style={styles.sectionHint}>
                First steps for your organization. This list goes away once all
                of them are done.
            </p>
            <ul style={styles.checklist}>
                {steps.map(step => {
                    const link = STEP_LINKS[step.key];
                    return (
                        <li
                            key={step.key}
                            style={styles.checklistItem}
                            data-testid={`onboarding-step-${step.key}`}
                        >
                            <span
                                style={
                                    step.done
                                        ? styles.checkDone
                                        : styles.checkTodo
                                }
                                aria-hidden="true"
                            >
                                {step.done ? '✓' : ''}
                            </span>
                            <div>
                                <div style={styles.checklistTitle}>
                                    {step.title}{' '}
                                    <span style={styles.meta}>
                                        {step.done ? '(done)' : '(to do)'}
                                    </span>
                                </div>
                                {!step.done && (
                                    <p style={styles.meta}>
                                        {step.hint}{' '}
                                        {link && (
                                            <Link to={link.to}>
                                                {link.label}
                                            </Link>
                                        )}
                                    </p>
                                )}
                            </div>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
};

export default OnboardingChecklist;

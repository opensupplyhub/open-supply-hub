import React from 'react';
import { arrayOf, bool, func, number, object, shape, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import CollapsibleSection from './CollapsibleSection';
import ClassifierComparison from './ClassifierComparison';
import {
    ADMIN_PREVIEW_LABEL,
    CALCULATION_SECTION_TITLE,
    PROFILE_COMPLETENESS_SECTION_ID,
    STRENGTHEN_SECTION_INTRO,
    STRENGTHEN_SECTION_TITLE,
} from './constants';
import {
    formatComponentValue,
    formatLevel,
    formatRunDate,
    formatScore,
    getStrengthenSteps,
} from './utils';
import profileCompletenessStyles from './styles';

/*
The two sections under the header: how the level was reached (with the
model classification alongside for comparison) and what would strengthen
the profile.
*/
const ProfileCompletenessSections = ({
    classes,
    className,
    profileCompleteness,
    isCalculationOpen,
    onToggleCalculation,
    isStrengthenOpen,
    onToggleStrengthen,
}) => {
    const score = profileCompleteness?.score;
    const classifier = profileCompleteness?.classifier;

    if (!score && !classifier) {
        return null;
    }

    const steps = score ? getStrengthenSteps(score.components) : [];
    const runDate = formatRunDate(score?.run_date);

    return (
        <div
            id={PROFILE_COMPLETENESS_SECTION_ID}
            className={`${classes.sections} ${className}`}
        >
            <CollapsibleSection
                classes={classes}
                testId="profile-completeness-calculation"
                title={CALCULATION_SECTION_TITLE}
                meta={
                    <>
                        {score && (
                            <span className={classes.headerMeta}>
                                {`${formatLevel(
                                    score.level,
                                    score.max_level,
                                )} · score ${formatScore(score.value)}`}
                            </span>
                        )}
                        <span className={classes.adminChip}>
                            {ADMIN_PREVIEW_LABEL}
                        </span>
                    </>
                }
                isOpen={isCalculationOpen}
                onToggle={onToggleCalculation}
            >
                {score && (
                    <>
                        <ul className={classes.breakdown}>
                            {score.components.map(component => (
                                <li
                                    key={component.key}
                                    className={classes.component}
                                >
                                    <span className={classes.componentName}>
                                        {component.label}
                                    </span>
                                    <span className={classes.componentValue}>
                                        {formatComponentValue(component.value)}
                                    </span>
                                    <span className={classes.componentTrack}>
                                        <span
                                            className={classes.componentFill}
                                            style={{
                                                width: `${
                                                    (component.value || 0) * 100
                                                }%`,
                                                display: 'block',
                                            }}
                                        />
                                    </span>
                                </li>
                            ))}
                        </ul>
                        <div className={classes.totalLine}>
                            <span
                                className={classes.totalValue}
                                data-testid="profile-completeness-score"
                            >
                                {formatScore(score.value)}
                            </span>
                            <p className={classes.note}>
                                The average of the components above, from 0 to
                                1. It reflects how complete, recent and widely
                                contributed-to this profile is, not whether the
                                data is correct.
                                {score.scorer_version || runDate
                                    ? ` Scorer ${[score.scorer_version, runDate]
                                          .filter(Boolean)
                                          .join(', ')}.`
                                    : ''}
                            </p>
                        </div>
                    </>
                )}
                <ClassifierComparison
                    classes={classes}
                    score={score}
                    classifier={classifier}
                />
            </CollapsibleSection>
            {steps.length > 0 && (
                <CollapsibleSection
                    classes={classes}
                    testId="profile-completeness-strengthen"
                    title={STRENGTHEN_SECTION_TITLE}
                    meta={
                        <span className={classes.headerMeta}>
                            {`${steps.length} suggested next step${
                                steps.length === 1 ? '' : 's'
                            }`}
                        </span>
                    }
                    isOpen={isStrengthenOpen}
                    onToggle={onToggleStrengthen}
                >
                    <p className={classes.note}>{STRENGTHEN_SECTION_INTRO}</p>
                    <ul className={classes.steps}>
                        {steps.map(step => (
                            <li key={step.key} className={classes.step}>
                                <div className={classes.stepText}>
                                    {step.text}
                                </div>
                                <div className={classes.stepDetail}>
                                    {step.detail}
                                </div>
                            </li>
                        ))}
                    </ul>
                </CollapsibleSection>
            )}
        </div>
    );
};

ProfileCompletenessSections.propTypes = {
    classes: object.isRequired,
    className: string,
    profileCompleteness: shape({
        score: shape({
            value: number,
            level: number,
            max_level: number,
            components: arrayOf(
                shape({
                    key: string.isRequired,
                    label: string.isRequired,
                    value: number,
                }),
            ),
            scorer_version: string,
            run_date: string,
        }),
        classifier: object,
    }),
    isCalculationOpen: bool.isRequired,
    onToggleCalculation: func.isRequired,
    isStrengthenOpen: bool.isRequired,
    onToggleStrengthen: func.isRequired,
};

ProfileCompletenessSections.defaultProps = {
    className: '',
    profileCompleteness: null,
};

export default withStyles(profileCompletenessStyles)(
    ProfileCompletenessSections,
);

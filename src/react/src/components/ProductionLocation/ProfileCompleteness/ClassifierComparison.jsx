import React from 'react';
import { number, object, shape, string } from 'prop-types';

import { CLASSIFIER_NOTE, CLASSIFIER_TITLE } from './constants';
import { compareLevels, formatLevel, formatRunDate, formatTier } from './utils';

/*
The model-backed classification of the same profile, next to the numeric
score so the two can be compared. It is a separate reading and never
changes the score or the bars.
*/
const ClassifierComparison = ({ classes, score, classifier }) => {
    if (!classifier?.tier) {
        return null;
    }

    const agrees = compareLevels(score, classifier);
    const runDate = formatRunDate(classifier.run_date);

    return (
        <div
            className={classes.classifier}
            data-testid="profile-completeness-classifier"
        >
            <h4 className={classes.classifierHeading}>
                {CLASSIFIER_TITLE}
                <span className={classes.classifierTier}>
                    {formatTier(classifier.tier)}
                </span>
            </h4>
            <dl className={classes.classifierList}>
                <div>
                    <dt className={classes.classifierTerm}>
                        Contributor agreement
                    </dt>
                    <dd className={classes.classifierDefinition}>
                        {formatTier(classifier.agreement_tier)}
                    </dd>
                </div>
                <div>
                    <dt className={classes.classifierTerm}>Field data</dt>
                    <dd className={classes.classifierDefinition}>
                        {formatTier(classifier.field_tier)}
                    </dd>
                </div>
                {agrees !== null && (
                    <div>
                        <dt className={classes.classifierTerm}>
                            Compared with the score
                        </dt>
                        <dd
                            className={classes.classifierDefinition}
                            data-testid="profile-completeness-comparison"
                        >
                            {agrees
                                ? `Same level (${formatLevel(
                                      score.level,
                                      score.max_level,
                                  )})`
                                : `Different: score is ${formatLevel(
                                      score.level,
                                      score.max_level,
                                  ).toLowerCase()}, classification is level ${
                                      classifier.level
                                  }`}
                        </dd>
                    </div>
                )}
            </dl>
            <p className={classes.note}>
                {[classifier.model, runDate].filter(Boolean).join(' · ')}
                {classifier.model || runDate ? '. ' : ''}
                {CLASSIFIER_NOTE}
            </p>
        </div>
    );
};

ClassifierComparison.propTypes = {
    classes: object.isRequired,
    score: shape({
        level: number,
        max_level: number,
    }),
    classifier: shape({
        tier: string,
        level: number,
        agreement_tier: string,
        field_tier: string,
        model: string,
        run_date: string,
    }),
};

ClassifierComparison.defaultProps = {
    score: null,
    classifier: null,
};

export default ClassifierComparison;

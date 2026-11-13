import moment from 'moment';

import {
    CLASSIFIER_TIER_LABELS,
    MAX_STRENGTHEN_STEPS,
    PLACEHOLDER_DATA_VALUES,
    STRENGTHEN_STEPS,
} from './constants';

export const formatScore = value =>
    typeof value === 'number' ? value.toFixed(3) : null;

export const formatComponentValue = value =>
    typeof value === 'number' ? value.toFixed(2) : '–';

export const formatRunDate = date => {
    if (!date) return null;
    const parsed = moment(date);
    return parsed.isValid() ? parsed.format('LL') : null;
};

// "Enhanced (level 2 of 3)": the word leads, the number backs it up.
export const formatLevel = ({ level, level_name: name, max_level: maxLevel }) =>
    name
        ? `${name} (level ${level} of ${maxLevel})`
        : `Level ${level} of ${maxLevel}`;

export const formatTier = tier => CLASSIFIER_TIER_LABELS[tier] || tier || '–';

export const formatPlaceholderData = tier =>
    PLACEHOLDER_DATA_VALUES[tier] || '–';

const componentsByKey = components =>
    (components || []).reduce(
        (acc, { key, value }) => ({ ...acc, [key]: value }),
        {},
    );

export const getStrengthenSteps = components => {
    const values = componentsByKey(components);
    return STRENGTHEN_STEPS.filter(step => step.applies(values)).slice(
        0,
        MAX_STRENGTHEN_STEPS,
    );
};

/*
How the model classification lines up with the score's level: null when
either side is missing, otherwise whether the two agree.
*/
export const compareLevels = (score, classifier) => {
    if (!score?.level || !classifier?.level) return null;
    return score.level === classifier.level;
};

import CheckCircleOutline from '@material-ui/icons/CheckCircleOutline';
import People from '@material-ui/icons/People';

import HandshakeIcon from '../../../HandshakeIcon';

export const DATA_SOURCES_TOOLTIP_TEXT =
    'Open Supply Hub is collaboratively mapping global supply chains. This model means that data comes into the platform in a few ways.';
export const DATA_SOURCES_LEARN_MORE_URL =
    'https://info.opensupplyhub.org/resources/an-open-data-model';

export const DATA_SOURCES_ITEMS = Object.freeze([
    Object.freeze({
        Icon: CheckCircleOutline,
        iconClassNameKey: 'iconClaimed',
        title: 'Claimed',
        subsectionText:
            'General information & operational details submitted by production location',
        learnMoreUrl:
            'https://info.opensupplyhub.org/resources/claim-a-facility',
    }),
    Object.freeze({
        Icon: People,
        iconClassNameKey: 'iconCrowdsourced',
        title: 'Crowdsourced',
        subsectionText:
            "General information shared by supply chain stakeholders & OS Hub's research team",
        learnMoreUrl: DATA_SOURCES_LEARN_MORE_URL,
    }),
    Object.freeze({
        Icon: HandshakeIcon,
        iconClassNameKey: 'iconPartner',
        title: 'Partner Data',
        subsectionText:
            'Additional social or environmental information shared by third party platforms',
        learnMoreUrl: 'https://info.opensupplyhub.org/data-integrations',
    }),
]);
